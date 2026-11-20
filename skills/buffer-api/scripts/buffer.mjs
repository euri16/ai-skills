#!/usr/bin/env node
// buffer: thin CLI over Buffer's official GraphQL API (https://api.buffer.com).
// No dependencies. The API key comes from the BUFFER_API_KEY environment variable and is never printed.
//
// Reads are free. Every write without --yes only shows the plan; --check really validates
// on the server by creating a draft that is deleted on the spot; --yes executes.
//
// Environment:
//   BUFFER_API_KEY            Buffer personal API key (required for any API call).
//   BLOB_READ_WRITE_TOKEN     Vercel Blob read/write token (required only to upload or delete local media).
//   BUFFER_TIMEZONE           IANA zone of "YYYY-MM-DD HH:MM" times when --tz is not given. Scheduling with
//                             --at needs one of the two; reads fall back to the machine's zone for display.
//   BUFFER_SECONDARY_TIMEZONE optional second IANA zone shown next to the local time in plans.
//   BUFFER_QUEUE_LIMIT        optional: scheduled posts per channel the account's Buffer plan allows. With it, the
//                             plan and doctor warn when a queue reaches it; without it, no limit is assumed.
//   BUFFER_YOUTUBE_CATEGORY   optional: YouTube category id used when --category is not given (no built-in default).
//   BUFFER_STATE_DIR          folder of the uploaded-media registry (default: <workspace>/.buffer-state).
//   WORKSPACE_ROOT            the user's workspace (default: current directory).
//   BUFFER_API_URL            API endpoint override (default: https://api.buffer.com).
//   BUFFER_ORGANIZATION       optional: id or name of the Buffer organization to work on (default: the account's first).
//
// Exit codes: 0 ok · 1 API error · 2 local validation · 3 missing or invalid key · 4 rate limit.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const WORKSPACE = path.resolve(process.env.WORKSPACE_ROOT || process.cwd());
const STATE_DIR = path.resolve(WORKSPACE, process.env.BUFFER_STATE_DIR || '.buffer-state');
const REGISTRY = path.join(STATE_DIR, 'media.json');
const ENDPOINT = process.env.BUFFER_API_URL || 'https://api.buffer.com';
// Scheduled posts per channel allowed by the account's plan; null when the user has not declared it.
const QUEUE_LIMIT = (() => {
  const v = (process.env.BUFFER_QUEUE_LIMIT || '').trim(); if (!v) return null;
  if (!/^[1-9]\d*$/.test(v)) { console.error('buffer: BUFFER_QUEUE_LIMIT must be a positive integer; ignoring it'); return null; }
  return Number(v);
})();
const queueCount = (n) => QUEUE_LIMIT ? `${n}/${QUEUE_LIMIT}` : String(n);
// Buffer's text limits, in UTF-16 units (developers.buffer.com/guides/character-limits.html, read on 2026-11-20).
const TEXT_LIMITS = { instagram: 2196, tiktok: 2200, youtube: 5000, linkedin: 3000, threads: 500, twitter: 280, bluesky: 300 };

class CliError extends Error { constructor(msg, code = 1) { super(msg); this.code = code; } }
const fail = (m, c = 2) => { throw new CliError(m, c); };
const log = (m) => console.error(`buffer: ${m}`);
const out = (o) => console.log(typeof o === 'string' ? o : JSON.stringify(o, null, 2));
const rel = (p) => path.relative(WORKSPACE, p);

// ---------- arguments ----------
export function parseArgs(argv) {
  const pos = []; const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) { const eq = a.indexOf('='); const k = eq > 0 ? a.slice(2, eq) : a.slice(2); const v = eq > 0 ? a.slice(eq + 1) : undefined; if (v !== undefined) flags[k] = v; else if (argv[i + 1] !== undefined && !argv[i + 1].startsWith('--')) flags[k] = argv[++i]; else flags[k] = true; }
    else pos.push(a);
  }
  return { pos, flags };
}

// ---------- credentials ----------
function apiKey() {
  const k = (process.env.BUFFER_API_KEY || '').trim();
  if (!k) fail('missing environment variable BUFFER_API_KEY; create a key at https://publish.buffer.com/settings/api and export it (see Prerequisites in SKILL.md)', 3);
  return k;
}
const redact = (s) => { const k = (process.env.BUFFER_API_KEY || '').trim(); const t = (process.env.BLOB_READ_WRITE_TOKEN || '').trim(); let r = String(s); if (k) r = r.split(k).join('[key]'); if (t) r = r.split(t).join('[token]'); return r; };

// ---------- time zones ----------
// Zone used to read and write "YYYY-MM-DD HH:MM" times. Scheduling requires an explicit one (--tz or BUFFER_TIMEZONE).
export function configuredTz(flags = {}) { return (flags.tz && flags.tz !== true ? String(flags.tz) : '') || process.env.BUFFER_TIMEZONE || null; }
export function requireTz(flags = {}) { return configuredTz(flags) || fail('no time zone for "YYYY-MM-DD HH:MM": pass --tz <IANA zone> or set BUFFER_TIMEZONE (for example America/New_York)'); }
// For display only: configured zone, else the machine's zone.
export function displayTz(flags = {}) { return configuredTz(flags) || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'; }
const SECONDARY_TZ = process.env.BUFFER_SECONDARY_TIMEZONE || null;

// ---------- GraphQL ----------
let lastRate = null;
function parseRate(h) {
  // One policy per window: its name in quotes, r = requests remaining, t = seconds until the window resets
  // (developers.buffer.com/guides/api-limits.html). Illustrative example with invented values:
  //   "100-in-15min"; r=42; t=300, "400-in-24h"; r=250; t=40000, "2000-in-30d"; r=1500; t=1000000
  if (!h) return null; const o = {};
  for (const m of h.matchAll(/"([^"]+)";\s*r=(\d+);\s*t=(\d+)/g)) o[m[1]] = { remaining: Number(m[2]), resetSeconds: Number(m[3]) };
  return o;
}
export async function gql(query, variables = {}) {
  const key = apiKey(); let r;
  try { r = await fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` }, body: JSON.stringify({ query, variables }) }); }
  catch (e) { throw new CliError(`no connection to ${ENDPOINT}: ${e.message}`, 1); }
  lastRate = parseRate(r.headers.get('ratelimit'));
  if (r.status === 401 || r.status === 403) throw new CliError('Buffer rejected the key (401/403): create another at https://publish.buffer.com/settings/api and update BUFFER_API_KEY', 3);
  if (r.status === 429) throw new CliError(`Buffer rate limit: wait ${r.headers.get('retry-after') || '?'} s before retrying (do not retry in a loop)`, 4);
  const text = await r.text(); let j;
  try { j = JSON.parse(text); } catch { throw new CliError(`non-JSON response (${r.status}): ${redact(text).slice(0, 300)}`, 1); }
  if (j.errors?.length) {
    const msg = j.errors.map(e => e.message + (e.extensions?.code ? ` [${e.extensions.code}]` : '')).join(' · ');
    if (j.errors.some(e => /RATE_LIMIT/.test(e.extensions?.code || ''))) throw new CliError(`Buffer rate limit: ${msg}`, 4);
    if (j.errors.some(e => /UNAUTH/i.test(e.extensions?.code || ''))) throw new CliError(`invalid key: ${msg}`, 3);
    throw new CliError(`API error: ${redact(msg).slice(0, 600)}`, 1);
  }
  const low = lastRate && Object.entries(lastRate).find(([, v]) => v.remaining < 15);
  if (low) log(`warning: ${low[1].remaining} requests left in the ${low[0]} window (resets in ${Math.ceil(low[1].resetSeconds / 60)} min)`);
  return j.data;
}
// Mutations return unions: success or an error type with `message`.
const ERR_FRAGMENT = '... on MutationError { message } __typename';
function unwrap(payload, okType) {
  if (!payload) throw new CliError('empty mutation response', 1);
  if (payload.__typename !== okType) throw new CliError(`${payload.__typename}: ${payload.message || 'no message'}`, payload.__typename === 'InvalidInputError' ? 2 : 1);
  return payload;
}

// ---------- organization and channels ----------
let cache = {};
export async function account() { return cache.account ||= (await gql('query{account{id timezone organizations{id name channelCount}}}')).account; }
// The organization every command works on: BUFFER_ORGANIZATION (id or name) or the account's first one.
export async function organization() {
  const a = await account(); const list = a.organizations || [];
  if (!list.length) fail('the account has no organizations', 1);
  const want = (process.env.BUFFER_ORGANIZATION || '').trim(); if (!want) return list[0];
  const hits = list.filter(o => o.id === want || (o.name || '').toLowerCase() === want.toLowerCase());
  if (hits.length !== 1) fail(`BUFFER_ORGANIZATION "${want}" matches ${hits.length} organizations; the account has: ${list.map(o => `${o.name} (${o.id})`).join(', ')}`);
  return hits[0];
}
export async function orgId() { return (await organization()).id; }
const CHANNEL_FIELDS = 'id name service type descriptor externalLink isDisconnected isLocked isQueuePaused hasActiveMemberDevice timezone postingSchedule{day paused times}';
export async function channels() { return cache.channels ||= (await gql(`query($o:OrganizationId!){channels(input:{organizationId:$o}){${CHANNEL_FIELDS}}}`, { o: await orgId() })).channels; }
// Accepts id, service (instagram) or channel name.
export async function resolveChannel(ref) {
  if (!ref) fail('missing --channel (id, service such as instagram|tiktok|youtube, or name)');
  const list = await channels(); const r = String(ref).toLowerCase();
  const hits = list.filter(c => c.id === ref || c.service.toLowerCase() === r || c.name.toLowerCase() === r);
  if (hits.length === 1) return hits[0];
  if (hits.length > 1) fail(`"${ref}" matches several channels: ${hits.map(c => `${c.service}/${c.name} (${c.id})`).join(', ')}; use the id`);
  fail(`no channel "${ref}"; channels: ${list.map(c => `${c.service}/${c.name} (${c.id})`).join(', ')}`);
}

// ---------- dates and time zones ----------
function tzOffsetMs(date, tz) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).formatToParts(date).filter(x => x.type !== 'literal').map(x => [x.type, Number(x.value)]));
  return Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second) - date.getTime();
}
// "2026-11-10 19:00" in time zone tz → Date (UTC). Also accepts ISO with an explicit zone.
export function wallToUtc(str, tz) {
  const s = String(str).trim();
  if (/[zZ]$|[+-]\d\d:?\d\d$/.test(s)) { const d = new Date(s); if (isNaN(d)) fail(`invalid date: ${s}`); return d; }
  const m = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{1,2}):(\d{2})$/.exec(s);
  if (!m) fail(`date "${s}" is not in the YYYY-MM-DD HH:MM format`);
  if (!tz) fail(`no time zone to read "${s}": pass --tz or set BUFFER_TIMEZONE`);
  try { new Intl.DateTimeFormat('en-US', { timeZone: tz }); } catch { fail(`unknown time zone: ${tz}`); }
  const guess = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
  let d = new Date(guess - tzOffsetMs(new Date(guess), tz));
  d = new Date(guess - tzOffsetMs(d, tz));
  return d;
}
export function fmtLocal(date, tz = displayTz()) {
  if (!date) return null; const d = new Date(date);
  return new Intl.DateTimeFormat('sv-SE', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(d).replace(',', '');
}
const utf16 = (s) => String(s || '').length;
const igLength = (s) => utf16(s) + (String(s || '').match(/\n/g) || []).length; // on Instagram each line break counts 2

// ---------- media: Vercel Blob ----------
function blobToken() {
  const t = (process.env.BLOB_READ_WRITE_TOKEN || '').trim();
  if (!t) fail('missing environment variable BLOB_READ_WRITE_TOKEN (Vercel Blob read/write token; needed to upload or delete local media). Use --url with an already public URL to skip uploads', 2);
  return t;
}
function vercel(args) {
  const r = spawnSync('vercel', args, { encoding: 'utf8', env: { ...process.env, BLOB_READ_WRITE_TOKEN: blobToken() }, maxBuffer: 16e6 });
  if (r.error) fail(`vercel CLI not found: ${r.error.message}`, 1);
  return r;
}
export function blobPut(file) {
  blobToken();
  const ext = path.extname(file).toLowerCase();
  const base = path.basename(file, ext).toLowerCase().replace(/[^a-z0-9-]+/g, '-').slice(0, 40);
  const name = `buffer-${base}-${Date.now().toString(36)}${ext}`;
  const tmp = path.join(os.tmpdir(), name); fs.copyFileSync(file, tmp);
  const r = vercel(['blob', 'put', tmp, '--access', 'public']); fs.rmSync(tmp, { force: true });
  const m = /(https:\/\/[^\s]+\.blob\.vercel-storage\.com\/[^\s]+)/.exec((r.stdout || '') + (r.stderr || ''));
  if (r.status !== 0 || !m) throw new CliError(`vercel blob put failed: ${redact(String(r.stderr || r.stdout)).slice(0, 300)}`, 1);
  registry((reg) => { reg.blobs.push({ url: m[1], file: rel(path.resolve(file)), uploadedAt: new Date().toISOString(), postId: null }); });
  return m[1];
}
export function blobDel(url) {
  const r = vercel(['blob', 'del', url]);
  if (r.status !== 0 && !/not found/i.test(r.stderr || '')) throw new CliError(`vercel blob del failed: ${redact(String(r.stderr)).slice(0, 200)}`, 1);
  registry((reg) => { reg.blobs = reg.blobs.filter(b => b.url !== url); });
}
// Registry of uploaded media and the post that uses each file. Lives in BUFFER_STATE_DIR (keep it out of git).
function registry(mutator) {
  const reg = fs.existsSync(REGISTRY) ? JSON.parse(fs.readFileSync(REGISTRY, 'utf8')) : { blobs: [] };
  if (mutator) { mutator(reg); fs.mkdirSync(STATE_DIR, { recursive: true }); fs.writeFileSync(REGISTRY, JSON.stringify(reg, null, 2) + '\n'); }
  return reg;
}
const linkBlob = (url, postId) => registry((reg) => { const b = reg.blobs.find(x => x.url === url); if (b) b.postId = postId; });

function ffprobe(file) {
  const r = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate', '-of', 'json', file], { encoding: 'utf8' });
  if (r.status !== 0) return null;
  const j = JSON.parse(r.stdout); const v = j.streams.find(s => s.codec_type === 'video');
  return { durationS: Number(j.format.duration), sizeMB: Number(j.format.size) / 1e6, codec: v?.codec_name, width: v?.width, height: v?.height, fps: v?.r_frame_rate, hasAudio: j.streams.some(s => s.codec_type === 'audio') };
}

// ---------- build and validate a post ----------
const VIDEO_EXT = ['.mp4', '.mov', '.m4v']; const IMAGE_EXT = ['.jpg', '.jpeg', '.png', '.webp', '.gif'];
export async function buildPost(flags) {
  const ch = await resolveChannel(flags.channel); const svc = ch.service;
  const problems = []; const warnings = [];
  if (ch.isDisconnected) problems.push('the channel is disconnected in Buffer: reconnect it in the app');
  if (ch.isLocked) problems.push("the channel is locked in Buffer (the account has more channels than its plan allows)");
  if (ch.isQueuePaused) warnings.push('the channel queue is paused: scheduled posts will not go out until it is resumed');

  // Text
  let text = flags['text-file'] ? fs.readFileSync(path.resolve(String(flags['text-file'])), 'utf8').replace(/\n$/, '') : (flags.text === true ? '' : flags.text ?? '');
  const limit = TEXT_LIMITS[svc]; const len = svc === 'instagram' ? igLength(text) : utf16(text);
  if (limit && len > limit) problems.push(`text of ${len} UTF-16 units for ${svc}; the maximum is ${limit}${svc === 'instagram' ? ' (each line break counts 2)' : ''}`);
  if (svc === 'instagram' && (text.match(/(^|\s)#[\p{L}\p{N}_]+/gu) || []).length > 5) warnings.push('more than 5 hashtags: Instagram limits posts to 5');
  if (svc === 'tiktok' && (text.match(/(^|\s)#[\p{L}\p{N}_]+/gu) || []).length > 5) warnings.push('more than 5 hashtags: Buffer limits TikTok to 5');
  if (svc === 'youtube' && /[<>]/.test(text)) problems.push('the YouTube description cannot contain < or >');

  // Media
  const files = flags.files ? String(flags.files).split(',').map(s => path.resolve(s.trim())) : flags.file ? [path.resolve(String(flags.file))] : [];
  const urls = flags.url ? String(flags.url).split(',').map(s => s.trim()) : [];
  for (const f of files) if (!fs.existsSync(f)) problems.push(`${f} does not exist`);
  const media = [...files.map(f => ({ file: f, ext: path.extname(f).toLowerCase() })), ...urls.map(u => ({ url: u, ext: path.extname(new URL(u).pathname).toLowerCase() }))];
  const isVideo = (m) => VIDEO_EXT.includes(m.ext);
  const probes = media.filter(m => m.file && isVideo(m)).map(m => ({ file: rel(m.file), ...ffprobe(m.file) }));
  const thumbOffset = flags['thumb-offset'] !== undefined ? Number(flags['thumb-offset']) : (media.some(isVideo) ? 0 : undefined);

  // Type per channel
  let type = flags.type;
  if (svc === 'instagram') {
    if (!type) type = media.length > 1 ? 'post' : media.some(isVideo) ? 'reel' : 'post';
    if (!['post', 'reel', 'story'].includes(type)) problems.push(`--type ${type} is not valid on Instagram (post|reel|story)`);
    if (!media.length) problems.push('Instagram needs an image or a video');
    if (media.length > 20) problems.push('a carousel accepts up to 20 items');
    if (type === 'reel') for (const p of probes) { if (p.durationS < 5 || p.durationS > 900) problems.push(`Reel of ${p.durationS?.toFixed(1)} s outside 5 s to 15 min`); if (p.sizeMB > 300) problems.push(`video of ${p.sizeMB.toFixed(0)} MB; Buffer accepts 300 MB for Reels`); }
  }
  if (svc === 'youtube') {
    if (!flags.title) problems.push('YouTube needs --title (100 characters at most, no < or >)');
    else if (utf16(flags.title) > 100 || /[<>]/.test(flags.title)) problems.push('the YouTube title exceeds 100 characters or contains < or >');
    if (!media.some(isVideo)) problems.push('YouTube (Shorts) needs a video');
    for (const p of probes) if (p.durationS > 180) problems.push(`Short of ${p.durationS.toFixed(0)} s; automatic publishing accepts up to 3 min`);
  }
  if (svc === 'tiktok') {
    if (!media.length) problems.push('TikTok needs a video or photos');
    for (const p of probes) if (p.durationS < 3 || p.durationS > 600) problems.push(`video of ${p.durationS?.toFixed(1)} s outside 3 s to 10 min`);
  }
  for (const p of probes) if (p.width && p.height && Math.abs(p.width / p.height - 9 / 16) > 0.02 && svc !== 'youtube') warnings.push(`${p.file} is ${p.width}×${p.height}, not 9:16`);

  // Scheduling
  const modeMap = { queue: 'addToQueue', next: 'shareNext', now: 'shareNow', at: 'customScheduled' };
  const mode = flags.at ? 'customScheduled' : modeMap[flags.mode || 'queue'] || flags.mode;
  if (!Object.values(modeMap).includes(mode)) problems.push(`--mode ${flags.mode} does not exist (queue|next|now|at)`);
  let dueAt = null; let tz = configuredTz(flags);
  if (mode === 'customScheduled') {
    if (!flags.at) problems.push('--mode at requires --at "YYYY-MM-DD HH:MM"');
    else { tz = requireTz(flags); dueAt = wallToUtc(flags.at, tz); if (dueAt.getTime() < Date.now() + 5 * 60e3) problems.push(`the time ${flags.at} (${tz}) has passed or is less than 5 minutes away`); }
  }
  if (!tz) tz = displayTz(flags);
  if (mode === 'shareNow') warnings.push('--mode now publishes immediately when run with --yes');
  const schedulingType = flags.notify ? 'notification' : 'automatic';
  if (schedulingType === 'notification' && !ch.hasActiveMemberDevice) problems.push('notification publishing without any phone with the Buffer app and notifications: the post would not go out');

  // Queue and daily limits
  let queue = null; let daily = null;
  if (!flags.draft) {
    const sched = await listPosts({ channelIds: [ch.id], status: ['scheduled'] }, 100);
    queue = { scheduled: sched.length, limit: QUEUE_LIMIT };
    if (QUEUE_LIMIT && sched.length >= QUEUE_LIMIT) warnings.push(`the ${svc} queue already has ${sched.length} scheduled posts and BUFFER_QUEUE_LIMIT is ${QUEUE_LIMIT}: Buffer may reject this one`);
    const d = (await gql('query($i:DailyPostingLimitsInput!){dailyPostingLimits(input:$i){limit sent scheduled isAtLimit}}', { i: { channelIds: [ch.id], date: (dueAt || new Date()).toISOString() } })).dailyPostingLimits[0];
    daily = d; if (d?.isAtLimit) problems.push(`${svc} already reached its daily limit (${d.limit}) that day`);
  }

  // Metadata
  const metadata = {};
  const category = String(flags.category && flags.category !== true ? flags.category : process.env.BUFFER_YOUTUBE_CATEGORY || '').trim();
  if (svc === 'instagram') metadata.instagram = { type, shouldShareToFeed: flags['no-feed'] ? false : true, ...(flags['first-comment'] ? { firstComment: String(flags['first-comment']) } : {}), ...(flags.ai ? { isAiGenerated: true } : {}) };
  if (svc === 'youtube') {
    // Buffer documents categoryId as required when creating a YouTube post; there is no built-in default.
    if (!category) problems.push('YouTube needs a category id: pass --category <id> or set BUFFER_YOUTUBE_CATEGORY (for example 22 People & Blogs, 26 Howto & Style, 28 Science & Technology)');
    else if (!/^\d+$/.test(category)) problems.push(`--category "${category}" is not a numeric YouTube category id`);
  }
  if (svc === 'youtube') metadata.youtube = { title: String(flags.title || ''), ...(category ? { categoryId: category } : {}), privacy: flags.privacy || 'public', ...(flags.ai ? { isAiGenerated: true } : {}), ...(flags['made-for-kids'] ? { madeForKids: true } : {}) };
  if (svc === 'tiktok' && (flags.ai || flags.title)) metadata.tiktok = { ...(flags.ai ? { isAiGenerated: true } : {}), ...(flags.title ? { title: String(flags.title) } : {}) };
  if (flags['first-comment'] && svc === 'instagram') warnings.push('the first comment depends on the Buffer plan: Buffer may reject it');

  const input = { channelId: ch.id, mode, schedulingType, text, assets: [], ...(dueAt ? { dueAt: dueAt.toISOString() } : {}), ...(Object.keys(metadata).length ? { metadata } : {}), ...(flags.ai ? { aiAssisted: true } : {}), ...(flags.draft ? { saveToDraft: true } : {}) };
  return { channel: ch, svc, input, media, thumbOffset, probes, problems, warnings, queue, daily, tz, dueAt };
}
function assetsFor(media, urls, thumbOffset, title, altText) {
  return media.map((m, i) => VIDEO_EXT.includes(m.ext)
    ? { video: { url: urls[i], metadata: { ...(thumbOffset !== undefined ? { thumbnailOffset: thumbOffset } : {}), ...(title ? { title } : {}) } } }
    : { image: { url: urls[i], ...(altText ? { metadata: { altText } } : {}) } });
}
function planSummary(b, flags) {
  return {
    channel: `${b.svc} · ${b.channel.name} (${b.channel.id})`,
    mode: b.input.mode, publishing: b.input.schedulingType,
    time: b.dueAt ? { local: `${fmtLocal(b.dueAt, b.tz)} (${b.tz})`, utc: b.dueAt.toISOString(), ...(SECONDARY_TZ ? { secondary: `${fmtLocal(b.dueAt, SECONDARY_TZ)} (${SECONDARY_TZ})` } : {}) } : null,
    type: b.input.metadata?.instagram?.type || (b.svc === 'youtube' ? 'short' : null),
    media: b.media.map(m => m.file ? rel(m.file) : m.url), video: b.probes,
    cover: b.thumbOffset !== undefined ? `frame at ${b.thumbOffset} ms` : null,
    title: b.input.metadata?.youtube?.title || b.input.metadata?.tiktok?.title || null,
    ...(b.svc === 'youtube' ? { category: b.input.metadata?.youtube?.categoryId || null, privacy: b.input.metadata?.youtube?.privacy } : {}),
    text: b.input.text, length: b.svc === 'instagram' ? igLength(b.input.text) : utf16(b.input.text),
    queue: b.queue, daily_limit: b.daily, draft: !!flags.draft, ai_generated: !!flags.ai,
    problems: b.problems, warnings: b.warnings,
  };
}
const POST_FIELDS = 'id status channelId channelService text dueAt sentAt createdAt schedulingType shareMode externalLink error{message supportUrl} assets{__typename source thumbnail ... on VideoAsset{video{durationMs width height thumbnailOffset}}}';
async function createPost(input) {
  const d = await gql(`mutation($i:CreatePostInput!){createPost(input:$i){... on PostActionSuccess{post{${POST_FIELDS}}} ${ERR_FRAGMENT}}}`, { i: input });
  return unwrap(d.createPost, 'PostActionSuccess').post;
}
export async function deletePost(id) {
  const d = await gql(`mutation($i:DeletePostInput!){deletePost(input:$i){... on DeletePostSuccess{id} ... on VoidMutationError{message} __typename}}`, { i: { id } });
  return unwrap(d.deletePost, 'DeletePostSuccess');
}
export async function getPost(id, extra = '') { return (await gql(`query($i:PostInput!){post(input:$i){${POST_FIELDS} ${extra}}}`, { i: { id } })).post; }
export async function listPosts(filter = {}, max = 50, fields = POST_FIELDS) {
  const o = await orgId(); const outList = []; let after = null;
  while (outList.length < max) {
    const d = await gql(`query($i:PostsInput!,$a:String,$n:Int){posts(input:$i,first:$n,after:$a){edges{node{${fields}}} pageInfo{hasNextPage endCursor}}}`, { i: { organizationId: o, filter, sort: [{ field: 'dueAt', direction: 'desc' }] }, a: after, n: Math.min(50, max - outList.length) });
    outList.push(...(d.posts.edges || []).map(e => e.node));
    if (!d.posts.pageInfo?.hasNextPage) break; after = d.posts.pageInfo.endCursor;
  }
  return outList;
}

// Uploads the local files and returns the URLs in the same order.
function uploadAll(media) { return media.map(m => m.url || blobPut(m.file)); }

async function cmdPostCreate(flags) {
  const b = await buildPost(flags); const summary = planSummary(b, flags);
  out({ plan: summary });
  if (b.problems.length) fail(`the plan has ${b.problems.length} problem(s); fix them before continuing`, 2);
  if (flags.check) {
    // Real validation: draft + read + delete. Publishes nothing.
    const urls = uploadAll(b.media);
    let post;
    try { post = await createPost({ ...b.input, saveToDraft: true, assets: assetsFor(b.media, urls, b.thumbOffset, null, flags['alt-text']) }); }
    finally { if (!post) for (const [i, m] of b.media.entries()) if (m.file) blobDel(urls[i]); }
    const back = await getPost(post.id); await deletePost(post.id);
    for (const [i, m] of b.media.entries()) if (m.file) blobDel(urls[i]);
    out({ check: 'ok', server: { status: back.status, schedulingType: back.schedulingType, assets: back.assets }, cleanup: 'test draft and media deleted' });
    if (back.schedulingType !== b.input.schedulingType) log(`warning: Buffer switched publishing to "${back.schedulingType}"`);
    return;
  }
  if (!flags.yes) { log('rehearsal: nothing was sent. --check validates on the server with a temporary draft; --yes executes'); return; }
  const urls = uploadAll(b.media);
  let post;
  try { post = await createPost({ ...b.input, assets: assetsFor(b.media, urls, b.thumbOffset, null, flags['alt-text']) }); }
  catch (e) { for (const [i, m] of b.media.entries()) if (m.file) blobDel(urls[i]); throw e; }
  for (const [i, m] of b.media.entries()) if (m.file) linkBlob(urls[i], post.id);
  if (post.schedulingType && post.schedulingType !== b.input.schedulingType) log(`warning: Buffer switched publishing to "${post.schedulingType}": it will need the mobile app`);
  out({ created: true, id: post.id, status: post.status, schedulingType: post.schedulingType, dueAt: post.dueAt, local: fmtLocal(post.dueAt, b.tz), media: urls });
}

// editPost replaces the whole post: text, assets and channel metadata must be sent again even when only the time changes.
const EDIT_FIELDS = `assets{__typename source ... on VideoAsset{video{thumbnailOffset}}}
  metadata{__typename ... on InstagramPostMetadata{type shouldShareToFeed isAiGenerated firstComment}
    ... on YoutubePostMetadata{title privacy isAiGenerated madeForKids category{categoryId}}
    ... on TiktokPostMetadata{title isAiGenerated}}`;
function editInputFrom(cur) {
  const m = cur.metadata || {}; const metadata = {};
  if (m.__typename === 'InstagramPostMetadata') metadata.instagram = { type: m.type, shouldShareToFeed: m.shouldShareToFeed, isAiGenerated: m.isAiGenerated, ...(m.firstComment ? { firstComment: m.firstComment } : {}) };
  if (m.__typename === 'YoutubePostMetadata') metadata.youtube = { title: m.title, ...(m.category?.categoryId ? { categoryId: m.category.categoryId } : {}), privacy: m.privacy, isAiGenerated: m.isAiGenerated, madeForKids: m.madeForKids };
  if (m.__typename === 'TiktokPostMetadata') metadata.tiktok = { isAiGenerated: m.isAiGenerated, ...(m.title ? { title: m.title } : {}) };
  const assets = (cur.assets || []).map(a => a.__typename === 'VideoAsset'
    ? { video: { url: a.source, metadata: a.video?.thumbnailOffset != null ? { thumbnailOffset: a.video.thumbnailOffset } : {} } }
    : { image: { url: a.source } });
  return { id: cur.id, text: cur.text, assets, schedulingType: cur.schedulingType, ...(Object.keys(metadata).length ? { metadata } : {}),
    ...(cur.dueAt ? { mode: 'customScheduled', dueAt: cur.dueAt } : {}) };
}

async function cmdPostEdit(id, flags) {
  if (!id) fail('usage: buffer post edit <id> [--at "YYYY-MM-DD HH:MM" --tz <zone>] [--text … | --text-file …] --yes');
  const cur = await getPost(id); const tz = flags.at ? requireTz(flags) : displayTz(flags);
  const curFull = (await gql(`query($i:PostInput!){post(input:$i){id text dueAt schedulingType ${EDIT_FIELDS}}}`, { i: { id } })).post;
  const input = editInputFrom(curFull); let changed = false;
  if (flags.at) { const d = wallToUtc(flags.at, tz); if (d.getTime() < Date.now() + 5 * 60e3) fail('that time has already passed'); input.dueAt = d.toISOString(); input.mode = 'customScheduled'; changed = true; }
  if (flags['text-file']) { input.text = fs.readFileSync(path.resolve(String(flags['text-file'])), 'utf8').replace(/\n$/, ''); changed = true; }
  else if (typeof flags.text === 'string') { input.text = flags.text; changed = true; }
  if (!changed) fail('nothing to change: use --at or --text/--text-file');
  out({ plan: { id, channel: cur.channelService, status: cur.status, current_time: fmtLocal(cur.dueAt, tz), new_time: flags.at ? fmtLocal(input.dueAt, tz) : '(unchanged)', time_zone: tz,
    new_text: input.text !== curFull.text ? input.text : '(unchanged)', kept: { media: input.assets.length, metadata: Object.keys(input.metadata || {}) } } });
  if (!['scheduled', 'draft', 'error'].includes(cur.status)) fail(`the post is "${cur.status}"; only scheduled posts, drafts or posts with an error can be edited`);
  if (!flags.yes) { log('rehearsal: repeat with --yes to edit'); return; }
  const d = await gql(`mutation($i:EditPostInput!){editPost(input:$i){... on PostActionSuccess{post{${POST_FIELDS}}} ${ERR_FRAGMENT}}}`, { i: input });
  const p = unwrap(d.editPost, 'PostActionSuccess').post; out({ edited: true, id: p.id, status: p.status, local: fmtLocal(p.dueAt, tz) });
}

async function cmdPostDelete(id, flags) {
  if (!id) fail('usage: buffer post delete <id> --yes');
  const cur = await getPost(id);
  out({ plan: { delete: id, channel: cur.channelService, status: cur.status, time: fmtLocal(cur.dueAt, displayTz(flags)), text: (cur.text || '').slice(0, 120) } });
  if (cur.status === 'sent') log('warning: the post was already sent; deleting it in Buffer does NOT remove it from the social network');
  if (!flags.yes) { log('rehearsal: repeat with --yes to delete'); return; }
  await deletePost(id);
  const reg = registry(); for (const b of reg.blobs.filter(x => x.postId === id)) blobDel(b.url);
  out({ deleted: id });
}

// ---------- read commands ----------
async function cmdDoctor(flags) {
  const a = await account(); const org = await organization(); const list = await channels(); const tz = configuredTz(flags);
  const report = { account: { time_zone: a.timezone, organization: org.id, organizations: a.organizations.length, channels: list.length }, configured_time_zone: tz || '(none: set BUFFER_TIMEZONE or pass --tz when scheduling)', channels: [], quota: lastRate, warnings: [] };
  for (const c of list) {
    const sched = (await listPosts({ channelIds: [c.id], status: ['scheduled'] }, 100, 'id')).length;
    report.channels.push({ service: c.service, name: c.name, id: c.id, type: c.descriptor, ok: !c.isDisconnected && !c.isLocked, disconnected: c.isDisconnected, locked: c.isLocked, queue_paused: c.isQueuePaused, time_zone: c.timezone, scheduled: queueCount(sched), phone_with_notifications: c.hasActiveMemberDevice });
    if (c.isDisconnected) report.warnings.push(`${c.service}: disconnected, reconnect it in Buffer`);
    if (c.isLocked) report.warnings.push(`${c.service}: locked by the channel limit`);
    if (c.isQueuePaused) report.warnings.push(`${c.service}: queue paused`);
    if (tz && c.timezone !== tz) report.warnings.push(`${c.service}: zone ${c.timezone}; scheduling uses ${tz} (change it in Buffer › channel › Posting schedule if queue slots should follow it)`);
    if (!c.hasActiveMemberDevice) report.warnings.push(`${c.service}: no phone with the Buffer app; a notification post would not go out`);
    if (QUEUE_LIMIT && sched >= QUEUE_LIMIT - 2) report.warnings.push(`${c.service}: queue almost full (${queueCount(sched)})`);
  }
  if (tz && a.timezone !== tz) report.warnings.push(`account in ${a.timezone}; scheduling uses ${tz}`);
  const orphans = registry().blobs.filter(b => !b.postId);
  if (orphans.length) report.warnings.push(`${orphans.length} uploaded file(s) without an associated post: buffer media cleanup`);
  report.quota = lastRate; out(report);
  if (report.channels.some(c => !c.ok)) process.exitCode = 1;
}
async function cmdQueue(flags) {
  const list = flags.channel ? [await resolveChannel(flags.channel)] : await channels(); const tz = displayTz(flags); const res = [];
  for (const c of list) {
    const posts = await listPosts({ channelIds: [c.id], status: ['scheduled', 'sending', 'error'] }, 100);
    res.push({ channel: `${c.service} · ${c.name}`, time_zone: tz, scheduled: queueCount(posts.filter(p => p.status === 'scheduled').length), posts: posts.sort((x, y) => String(x.dueAt).localeCompare(String(y.dueAt))).map(p => ({ id: p.id, status: p.status, time: fmtLocal(p.dueAt, tz), publishing: p.schedulingType, text: (p.text || '').split('\n')[0].slice(0, 80), error: p.error?.message })) });
  }
  out(res);
}
async function cmdPostsList(flags) {
  const filter = {}; const tz = displayTz(flags);
  if (flags.status) filter.status = String(flags.status).split(',');
  if (flags.channel) filter.channelIds = [(await resolveChannel(flags.channel)).id];
  if (flags.since) filter.dueAt = { start: wallToUtc(`${flags.since} 00:00`, tz).toISOString() };
  const posts = await listPosts(filter, Number(flags.limit) || 20);
  out(posts.map(p => ({ id: p.id, channel: p.channelService, status: p.status, time: fmtLocal(p.dueAt || p.sentAt, tz), sent: fmtLocal(p.sentAt, tz), link: p.externalLink, text: (p.text || '').split('\n')[0].slice(0, 80), error: p.error?.message })));
}
const METRIC_FIELDS = 'metrics{type name value unit} metricsUpdatedAt';
async function cmdMetrics(sub, rest, flags) {
  if (sub === 'post') { const p = await getPost(rest[0] || fail('usage: buffer metrics post <id>'), METRIC_FIELDS); out({ id: p.id, channel: p.channelService, sent: p.sentAt, link: p.externalLink, updated: p.metricsUpdatedAt, metrics: Object.fromEntries((p.metrics || []).map(m => [m.type, m.value])) }); return; }
  if (sub === 'aggregate') {
    const tz = displayTz(flags);
    const end = flags.until ? wallToUtc(`${flags.until} 23:59`, tz) : new Date(); const start = flags.since ? wallToUtc(`${flags.since} 00:00`, tz) : new Date(end - 7 * 864e5);
    if (Date.now() - start > 31 * 864e5) log('warning: the range starts more than 31 days ago; how far back the aggregate reaches depends on the Buffer plan');
    const i = { organizationId: await orgId(), startDateTime: start.toISOString(), endDateTime: end.toISOString(), ...(flags.channel ? { channelIds: [(await resolveChannel(flags.channel)).id] } : {}) };
    const d = (await gql('query($i:AggregatedPostMetricsInput!){aggregatedPostMetrics(input:$i){metrics{type name value unit} metricsUpdatedAt}}', { i })).aggregatedPostMetrics;
    out({ since: i.startDateTime, until: i.endDateTime, channel: flags.channel || 'all', updated: d.metricsUpdatedAt, metrics: Object.fromEntries(d.metrics.map(m => [m.type, m.value])) }); return;
  }
  fail('usage: buffer metrics post <id> | aggregate [--channel x] [--since YYYY-MM-DD] [--until YYYY-MM-DD]');
}
async function cmdIdeas(sub, flags) {
  if (sub && !['list', 'create'].includes(sub)) fail('usage: buffer ideas list | create --title … --yes');
  if (sub === 'create') {
    const content = { title: flags.title || undefined, text: flags.text || undefined, ...(flags.services ? { services: String(flags.services).split(',') } : {}) };
    if (!content.title && !content.text) fail('usage: buffer ideas create --title … [--text …] [--services instagram,tiktok] --yes');
    out({ plan: { create_idea: content, note: 'the API cannot edit or delete ideas: they can only be deleted in the app' } });
    if (!flags.yes) { log('rehearsal: repeat with --yes'); return; }
    const d = await gql('mutation($i:CreateIdeaInput!){createIdea(input:$i){... on Idea{id} ... on MutationError{message} __typename}}', { i: { organizationId: await orgId(), content } });
    out(unwrap(d.createIdea, 'Idea')); return;
  }
  const d = (await gql('query($i:IdeasInput!){ideas(input:$i,first:100){edges{node{id createdAt content{title text services date}}}}}', { i: { organizationId: await orgId() } })).ideas;
  out(d.edges.map(e => ({ id: e.node.id, created: new Date(e.node.createdAt * 1000).toISOString().slice(0, 10), title: e.node.content.title, text: (e.node.content.text || '').slice(0, 200), services: e.node.content.services })));
}
async function cmdMedia(sub, rest, flags) {
  if (sub === 'list') { out({ registry: rel(REGISTRY), ...registry() }); return; }
  if (sub === 'put') { const f = rest[0] || fail('usage: buffer media put <file>'); if (!fs.existsSync(f)) fail(`${f} does not exist`); out({ url: blobPut(path.resolve(f)), note: 'recorded without a post; media cleanup deletes it if unused' }); return; }
  if (sub === 'cleanup') {
    const reg = registry(); const plan = [];
    for (const b of reg.blobs) {
      if (!b.postId) { const ageH = (Date.now() - new Date(b.uploadedAt)) / 36e5; plan.push({ ...b, action: ageH > 24 ? 'delete (no post for more than 24 h)' : 'keep (recently uploaded, no post)', del: ageH > 24 }); continue; }
      let st; try { st = (await getPost(b.postId)).status; } catch (e) { st = /NotFound|not found/i.test(e.message) ? 'deleted' : `unknown (${e.message.slice(0, 60)})`; }
      const del = st === 'sent' || st === 'deleted';
      plan.push({ ...b, post_status: st, action: del ? 'delete' : st === 'error' ? 'keep (post with an error, can be retried)' : 'keep (pending publication)', del });
    }
    out(plan.map(({ del, ...x }) => x));
    if (!flags.yes) { if (plan.some(p => p.del)) log('rehearsal: repeat with --yes to delete the marked ones'); return; }
    let n = 0; for (const p of plan.filter(x => x.del)) { blobDel(p.url); n++; } out({ deleted: n }); return;
  }
  fail('usage: buffer media list | put <file> | cleanup [--yes]');
}
async function cmdRaw(rest, flags) {
  const q = rest.join(' ') || (flags.file ? fs.readFileSync(String(flags.file), 'utf8') : fail('usage: buffer raw \'query{…}\' [--vars \'{…}\'] (mutations with --yes)'));
  const vars = flags.vars ? JSON.parse(String(flags.vars)) : {};
  if (/^\s*mutation/i.test(q) && !flags.yes) { out({ plan: { mutation: q, variables: vars } }); log('rehearsal: this is a mutation; repeat with --yes'); return; }
  out(await gql(q, vars));
}

// ---------- main ----------
const HELP = `buffer: Buffer API CLI (see SKILL.md)
  whoami | doctor | channels | queue [--channel x]
  posts list [--status scheduled,sent,error,draft] [--channel x] [--since YYYY-MM-DD] [--limit N]
  post get <id>
  post create --channel instagram|tiktok|youtube|<id> (--file f | --files a,b | --url u)
              (--text "…" | --text-file f) [--at "YYYY-MM-DD HH:MM" [--tz <IANA zone>] | --mode queue|next|now]
              [--type reel|post|story] [--title "…"] [--privacy public|unlisted|private] [--category <id>]
              [--made-for-kids] [--first-comment "…"] [--thumb-offset ms] [--alt-text "…"] [--ai] [--notify]
              [--draft] [--no-feed]
              (no flag: plan · --check: validates with a temporary draft · --yes: executes)
  post edit <id> [--at … --tz …] [--text …|--text-file f] --yes · post delete <id> --yes
  metrics post <id> · metrics aggregate [--channel x] [--since d] [--until d]
  ideas list · ideas create --title … [--text …] --yes
  media list · media put <file> · media cleanup [--yes]
  raw 'query{…}' [--vars '{…}']

Environment: BUFFER_API_KEY (required for API calls), BLOB_READ_WRITE_TOKEN (to upload local media),
  BUFFER_TIMEZONE (zone of --at when --tz is absent), BUFFER_SECONDARY_TIMEZONE (optional),
  BUFFER_QUEUE_LIMIT (optional: scheduled posts per channel the plan allows, for warnings),
  BUFFER_YOUTUBE_CATEGORY (YouTube category id when --category is absent),
  BUFFER_STATE_DIR (default <workspace>/.buffer-state), WORKSPACE_ROOT (default: current directory),
  BUFFER_API_URL (default https://api.buffer.com), BUFFER_ORGANIZATION (id or name; default: the account's first).`;

async function main() {
  const { pos, flags } = parseArgs(process.argv.slice(2)); const [c1, c2, ...rest] = pos;
  switch (c1) {
    case 'whoami': { const a = await account(); out({ id: a.id, time_zone: a.timezone, organization: (await organization()).id, organizations: a.organizations.map(o => ({ id: o.id, name: o.name, channels: o.channelCount })), quota: lastRate }); break; }
    case 'doctor': await cmdDoctor(flags); break;
    case 'channels': out((await channels()).map(c => ({ id: c.id, service: c.service, name: c.name, type: c.descriptor, time_zone: c.timezone, link: c.externalLink, posting_schedule: c.postingSchedule.filter(d => d.times.length).map(d => `${d.day} ${d.times.join(',')}${d.paused ? ' (paused)' : ''}`) }))); break;
    case 'queue': await cmdQueue(flags); break;
    case 'posts': if (c2 && c2 !== 'list') fail(HELP); await cmdPostsList(flags); break;
    case 'post':
      if (c2 === 'get') { const p = await getPost(rest[0] || fail('usage: buffer post get <id>')); out({ ...p, local: fmtLocal(p.dueAt, displayTz(flags)) }); }
      else if (c2 === 'create') await cmdPostCreate(flags);
      else if (c2 === 'edit') await cmdPostEdit(rest[0], flags);
      else if (c2 === 'delete') await cmdPostDelete(rest[0], flags);
      else fail(HELP);
      break;
    case 'metrics': await cmdMetrics(c2, rest, flags); break;
    case 'ideas': await cmdIdeas(c2, flags); break;
    case 'media': await cmdMedia(c2, rest, flags); break;
    case 'raw': await cmdRaw([c2, ...rest].filter(Boolean), flags); break;
    case undefined: case 'help': case '--help': console.log(HELP); break;
    default: fail(`unknown command: ${c1}\n${HELP}`);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((e) => { console.error(`buffer: ${redact(e.message)}`); process.exit(Number.isInteger(e.code) ? e.code : 1); });
}
