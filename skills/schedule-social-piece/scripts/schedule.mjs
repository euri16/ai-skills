#!/usr/bin/env node
// schedule: schedules in Buffer an approved piece from social/<piece>/, channel by channel,
// from its piece record (piece.md), and keeps the record up to date when Buffer publishes.
//
//   schedule plan <piece> [--channels instagram,tiktok,youtube] [--check]
//       Reads piece.md, prepares each channel's video (cover stuck on as the first frames on
//       Instagram, TikTok and YouTube) and shows the `buffer post create` plan. --check validates on the
//       server with a temporary draft. Schedules nothing.
//   schedule run <piece> [--channels …] --yes
//       Schedules each channel and writes "Status: scheduled (…)" and "Buffer: <id>" in piece.md.
//   schedule cover <piece> [--channel instagram|tiktok|youtube]
//       Only generates the video with the cover stuck on and a control frame.
//   schedule sync [<piece>] [--write]
//       Checks in Buffer the scheduled posts of the piece records; with --write it moves the sent ones to
//       "published (date)" with the link and cleans up their media.
//
// Rules: only schedules sections with "Status: approved" and "Schedule: YYYY-MM-DD HH:MM"; never invents
// captions or titles. Time zone of the schedule, first match wins: a zone written in the field
// ("2026-11-10 19:00 (Europe/London)"), "- Time zone:" in the piece record header, BUFFER_TIMEZONE.
// Without any of them the channel is blocked.
//
// The YouTube category is "- Category: <id>" in the YouTube section; without it buffer.mjs falls back to
// BUFFER_YOUTUBE_CATEGORY, and with neither the channel is blocked.
//
// Environment: same as buffer.mjs (BUFFER_API_KEY, BLOB_READ_WRITE_TOKEN, BUFFER_TIMEZONE,
// BUFFER_SECONDARY_TIMEZONE, BUFFER_QUEUE_LIMIT, BUFFER_YOUTUBE_CATEGORY, BUFFER_STATE_DIR, WORKSPACE_ROOT,
// BUFFER_API_URL, BUFFER_ORGANIZATION). "- AI: yes" in the piece record header flags every channel as AI-generated;
// in a channel's section, only that channel.
// Pieces live in <workspace>/social/.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { getPost, fmtLocal, parseArgs, WORKSPACE } from '../../buffer-api/scripts/buffer.mjs';

const ROOT = WORKSPACE;
const BUFFER_CLI = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../buffer-api/scripts/buffer.mjs');
const SOCIAL = path.join(ROOT, 'social');
const RECORD = 'piece.md';
const die = (m, c = 1) => { console.error(`schedule: ${m}`); process.exit(Number.isInteger(c) ? c : 1); };
const log = (m) => console.error(`schedule: ${m}`);

// Channels Buffer schedules: section heading in the piece record and file suffixes.
const CHANNELS = {
  instagram: { heading: /^## Instagram\s*$/m, suffixes: ['instagram', 'ig'], coverFrame: true, label: 'Instagram' },
  tiktok: { heading: /^## TikTok\s*$/m, suffixes: ['tiktok', 'tt'], coverFrame: true, label: 'TikTok' },
  youtube: { heading: /^## YouTube( Shorts)?\s*$/m, suffixes: ['youtube', 'shorts', 'yt'], coverFrame: true, label: 'YouTube' },
};
const COVER_FRAMES = 2;

function pieceDir(arg) {
  const c = [arg, path.join(ROOT, arg), path.join(SOCIAL, arg)].find(d => fs.existsSync(path.join(d, RECORD)));
  if (!c) die(`cannot find ${RECORD} in ${arg} (nor in social/${arg})`, 2);
  return path.resolve(c);
}
const validTz = (tz) => { try { new Intl.DateTimeFormat('en-US', { timeZone: tz }); return true; } catch { return false; } };

// ---------- piece record ----------
function section(text, heading) {
  const i = text.search(heading); if (i < 0) return null;
  const rest = text.slice(i + 1); const j = rest.search(/^## /m);
  return { start: i + 1, body: j < 0 ? rest : rest.slice(0, j) };
}
const yes = (v) => /^(yes|true)\b/i.test(v || '');
const field = (body, name) => (new RegExp(`^- ${name}:[ \\t]*(.*)$`, 'mi').exec(body) || [])[1]?.trim() ?? null;
function readChannel(text, key, pieceTz) {
  const s = section(text, CHANNELS[key].heading); if (!s) return null;
  const cap = /Caption:\s*\n```[^\n]*\n([\s\S]*?)\n```/m.exec(s.body);
  const sched = field(s.body, 'Schedule');
  let when = null, tz = pieceTz;
  if (sched) { const m = /^(\d{4}-\d{2}-\d{2}[ T]\d{1,2}:\d{2})(?:\s*\(?([A-Za-z_]+(?:\/[A-Za-z_+-]+)+|UTC)\)?)?/.exec(sched); if (m) { when = m[1]; if (m[2]) tz = m[2]; } }
  return { key, status: field(s.body, 'Status') || '', schedule: sched, when, tz, title: field(s.body, 'Title'), privacy: field(s.body, 'Privacy'), category: field(s.body, 'Category'), bufferId: (field(s.body, 'Buffer') || '').split(/\s/)[0] || null, link: field(s.body, 'Link'), ai: yes(field(s.body, 'AI')), caption: cap ? cap[1] : '' };
}
function readPiece(dir) {
  const file = path.join(dir, RECORD); const text = fs.readFileSync(file, 'utf8');
  const slug = path.basename(dir).replace(/^\d{4}-\d{2}-\d{2}-/, '');
  // Header = everything before the first "## " section.
  const header = text.split(/^## /m)[0];
  const pieceTz = field(header, 'Time zone') || process.env.BUFFER_TIMEZONE || null;
  const channels = Object.fromEntries(Object.keys(CHANNELS).map(k => [k, readChannel(text, k, pieceTz)]).filter(([, v]) => v));
  return { file, text, title: (/^# (.+)$/m.exec(text) || [])[1] || slug, slug, channels, ai: yes(field(header, 'AI')) };
}
// Rewrites fields in a channel's section (adds the missing ones under "Status").
function writeFields(file, key, fields) {
  const text = fs.readFileSync(file, 'utf8'); const s = section(text, CHANNELS[key].heading);
  if (!s) die(`${RECORD} has no ${CHANNELS[key].label} section`, 2);
  let body = s.body;
  for (const [name, value] of Object.entries(fields)) {
    const re = new RegExp(`^- ${name}:.*$`, 'mi');
    if (re.test(body)) body = body.replace(re, `- ${name}: ${value}`);
    else body = body.replace(/^(- Status:.*)$/mi, `$1\n- ${name}: ${value}`);
  }
  fs.writeFileSync(file, text.slice(0, s.start) + body + text.slice(s.start + s.body.length));
}

// ---------- files ----------
const ls = (d) => fs.existsSync(d) ? fs.readdirSync(d).filter(f => !f.startsWith('.')).map(f => path.join(d, f)) : [];
function findVideo(dir, slug, key) {
  const ex = ls(path.join(dir, 'export')).filter(f => /\.(mp4|mov)$/i.test(f) && !/-buffer\.mp4$/i.test(f));
  const name = (f) => path.basename(f).toLowerCase();
  for (const s of CHANNELS[key].suffixes) { const hit = ex.find(f => new RegExp(`^${slug}-${s}\\.(mp4|mov)$`).test(name(f))); if (hit) return { file: hit }; }
  const plain = ex.find(f => new RegExp(`^${slug}\\.(mp4|mov)$`).test(name(f))); if (plain) return { file: plain };
  const others = ex.filter(f => !/-archive\.mp4$/i.test(f));
  if (others.length === 1) return { file: others[0] };
  const arch = ex.find(f => /-archive\.mp4$/i.test(f));
  if (arch) return { file: arch, warning: `only the archive copy ${path.basename(arch)} exists (recompressed); better export ${slug}-${CHANNELS[key].suffixes[0]}.mp4` };
  return null;
}
function findCover(dir, key) {
  for (const k of [key, 'instagram']) for (const ext of ['png', 'jpg', 'jpeg']) { const p = path.join(dir, `cover-${k}.${ext}`); if (fs.existsSync(p)) return { file: p, warning: k !== key ? `no cover-${key}; using cover-${k}` : null }; }
  return null;
}
function probe(file) {
  const r = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate,channels', '-of', 'json', file], { encoding: 'utf8' });
  if (r.status !== 0) die(`ffprobe could not read ${file}`);
  const j = JSON.parse(r.stdout); const v = j.streams.find(s => s.codec_type === 'video'); const a = j.streams.find(s => s.codec_type === 'audio');
  const [n, d] = v.r_frame_rate.split('/').map(Number);
  return { duration: Number(j.format.duration), width: v.width, height: v.height, fps: n / (d || 1), fpsStr: v.r_frame_rate, audio: !!a };
}
const newer = (out, ...ins) => fs.existsSync(out) && ins.every(i => fs.statSync(out).mtimeMs > fs.statSync(i).mtimeMs);

// Video with the cover stuck on as the first COVER_FRAMES frames; Buffer takes frame 0 as the cover.
function coverVideo(dir, slug, key, video, cover) {
  const outFile = path.join(dir, 'export', `${slug}-${key}-buffer.mp4`);
  const check = path.join(dir, 'edit', 'tests', `buffer-${key}-frame0.jpg`);
  const p = probe(video);
  if (!newer(outFile, video, cover)) {
    const dur = (COVER_FRAMES / p.fps).toFixed(6);
    const args = ['-v', 'error', '-y', '-loop', '1', '-framerate', p.fpsStr, '-t', dur, '-i', cover, '-i', video, '-f', 'lavfi', '-t', dur, '-i', 'anullsrc=r=48000:cl=stereo',
      '-filter_complex', `[0:v]scale=${p.width}:${p.height}:force_original_aspect_ratio=increase,crop=${p.width}:${p.height},setsar=1,format=yuv420p,fps=${p.fpsStr}[c];[1:v]setsar=1,format=yuv420p,fps=${p.fpsStr}[v];` +
        (p.audio ? `[2:a]aformat=sample_rates=48000:channel_layouts=stereo[s];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a];[c][s][v][a]concat=n=2:v=1:a=1[ov][oa]` : `[c][v]concat=n=2:v=1:a=0[ov]`),
      '-map', '[ov]', ...(p.audio ? ['-map', '[oa]', '-c:a', 'aac', '-b:a', '256k'] : []),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', p.fpsStr, '-movflags', '+faststart', outFile];
    log(`generating ${path.relative(ROOT, outFile)} (cover in the first ${COVER_FRAMES} frames)…`);
    const r = spawnSync('ffmpeg', args, { encoding: 'utf8' });
    if (r.status !== 0) die(`ffmpeg failed: ${(r.stderr || '').slice(-400)}`);
  }
  fs.mkdirSync(path.dirname(check), { recursive: true });
  spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', outFile, '-frames:v', '1', '-q:v', '2', check]);
  const q = probe(outFile);
  const expected = p.duration + COVER_FRAMES / p.fps;
  if (Math.abs(q.duration - expected) > 0.1) die(`the generated video lasts ${q.duration.toFixed(3)} s and should last ${expected.toFixed(3)} s`);
  return { file: outFile, frame0: check, duration: q.duration, original: p.duration };
}

// ---------- call the buffer CLI ----------
function bufferCli(args) {
  const r = spawnSync('node', [BUFFER_CLI, ...args], { encoding: 'utf8', maxBuffer: 32e6, env: { ...process.env, WORKSPACE_ROOT: ROOT } });
  const objs = []; const s = r.stdout || ''; let depth = 0, start = -1, inStr = false, esc = false;
  for (let i = 0; i < s.length; i++) { const ch = s[i]; if (inStr) { if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false; continue; } if (ch === '"') inStr = true; else if (ch === '{' || ch === '[') { if (!depth++) start = i; } else if (ch === '}' || ch === ']') { if (!--depth) { try { objs.push(JSON.parse(s.slice(start, i + 1))); } catch { /* ignore */ } } } }
  return { status: r.status, objs, stderr: (r.stderr || '').trim() };
}

function channelArgs(dir, f, ch, video, flags) {
  const capFile = path.join(os.tmpdir(), `schedule-${f.slug}-${ch.key}-${process.pid}.txt`);
  fs.writeFileSync(capFile, ch.caption);
  const args = ['post', 'create', '--channel', ch.key, '--file', video, '--text-file', capFile, '--at', ch.when, '--tz', ch.tz, '--thumb-offset', '0'];
  if (ch.key === 'youtube') { if (ch.title) args.push('--title', ch.title); args.push('--privacy', (ch.privacy || 'public').toLowerCase()); if (ch.category) args.push('--category', ch.category.split(/\s/)[0]); }
  if (ch.key === 'instagram' && flags.type) args.push('--type', flags.type);
  if (f.ai || ch.ai || flags.ai) args.push('--ai');
  return { args, capFile };
}

function prepare(dir, flags) {
  const f = readPiece(dir);
  const wanted = flags.channels ? String(flags.channels).split(',').map(s => s.trim().toLowerCase()) : Object.keys(f.channels);
  const items = []; const skipped = [];
  for (const key of wanted) {
    if (!CHANNELS[key]) die(`unknown channel: ${key} (instagram, tiktok, youtube)`, 2);
    const ch = f.channels[key];
    if (!ch) { skipped.push({ channel: key, reason: `${RECORD} has no section for it` }); continue; }
    if (!/^approved/i.test(ch.status)) { skipped.push({ channel: key, reason: `status "${ch.status || 'empty'}": only approved sections are scheduled` }); continue; }
    if (ch.bufferId && !flags.force) { skipped.push({ channel: key, reason: `already has a Buffer post (${ch.bufferId}); use --force to create another` }); continue; }
    const problems = [];
    if (!ch.when) problems.push('missing "- Schedule: YYYY-MM-DD HH:MM" in the section');
    else if (!ch.tz) problems.push('no time zone: write it in the field ("YYYY-MM-DD HH:MM (Area/City)"), add "- Time zone: Area/City" to the piece record header or set BUFFER_TIMEZONE');
    else if (!validTz(ch.tz)) problems.push(`unknown time zone: ${ch.tz}`);
    if (!ch.caption.trim()) problems.push('missing caption');
    if (key === 'youtube' && !ch.title) problems.push('missing "- Title:" in the YouTube section');
    if (key === 'youtube' && !ch.category && !(process.env.BUFFER_YOUTUBE_CATEGORY || '').trim()) problems.push('missing "- Category: <YouTube category id>" in the YouTube section (or set BUFFER_YOUTUBE_CATEGORY)');
    const v = findVideo(dir, f.slug, key); const warnings = [];
    if (!v) problems.push(`no video in export/ (expected ${f.slug}-${CHANNELS[key].suffixes[0]}.mp4)`); else if (v.warning) warnings.push(v.warning);
    let cover = null; let video = v?.file;
    if (v && CHANNELS[key].coverFrame) {
      const c = findCover(dir, key);
      if (!c) warnings.push('no cover: the thumbnail will be the first frame of the video');
      else { if (c.warning) warnings.push(c.warning); cover = c.file; }
    }
    items.push({ key, ch, video, cover, problems, warnings });
  }
  return { f, items, skipped };
}

async function cmdPlan(dir, flags, execute) {
  const { f, items, skipped } = prepare(dir, flags);
  if (!items.length) { console.log(JSON.stringify({ piece: f.title, skipped }, null, 2)); die('no channels ready to schedule', 2); }
  const blocked = items.filter(i => i.problems.length);
  if (blocked.length) { console.log(JSON.stringify({ piece: f.title, problems: blocked.map(i => ({ channel: i.key, problems: i.problems })), skipped }, null, 2)); die(`fix ${RECORD} before continuing`, 2); }
  const results = []; const made = new Map();
  for (const it of items) {
    let cv = null;
    if (it.cover) {
      // Channels with the same video and the same cover share a file.
      const k = `${it.video}|${it.cover}`;
      const shared = items.filter(x => x.cover && `${x.video}|${x.cover}` === k).length > 1;
      cv = made.get(k) || coverVideo(dir, f.slug, shared ? 'social' : it.key, it.video, it.cover);
      made.set(k, cv); it.video = cv.file;
    }
    const { args, capFile } = channelArgs(dir, f, it.ch, it.video, flags);
    const mode = execute ? ['--yes'] : flags.check ? ['--check'] : [];
    const r = bufferCli([...args, ...mode]); fs.rmSync(capFile, { force: true });
    const plan = r.objs.find(o => o.plan)?.plan; const created = r.objs.find(o => o.created); const check = r.objs.find(o => o.check);
    const res = { channel: it.key, schedule: `${it.ch.when} (${it.ch.tz})`, video: path.relative(ROOT, it.video), cover: it.cover ? path.relative(ROOT, it.cover) : null, frame0: cv ? path.relative(ROOT, cv.frame0) : null, warnings: [...it.warnings, ...(plan?.warnings || [])], plan, ...(check ? { check: check.check, server: check.server?.schedulingType } : {}), ...(r.status !== 0 ? { error: r.stderr.split('\n').pop() } : {}) };
    if (execute && created) {
      const local = fmtLocal(created.dueAt, it.ch.tz);
      writeFields(f.file, it.key, { Status: `scheduled (${local}, ${it.ch.tz}).`, Buffer: created.id });
      Object.assign(res, { scheduled: true, id: created.id, publishing: created.schedulingType });
    }
    results.push(res);
    if (r.status !== 0) { console.log(JSON.stringify({ piece: f.title, results }, null, 2)); die(`${it.key} failed (code ${r.status}); the previous channels ${execute ? 'are already scheduled and recorded in ' + RECORD : 'passed the plan'}`, r.status); }
  }
  console.log(JSON.stringify({ piece: f.title, record: path.relative(ROOT, f.file), results, skipped }, null, 2));
  if (!execute) log(flags.check ? 'validated on the server with temporary drafts; nothing was scheduled' : 'rehearsal: nothing was sent. --check validates on the server; run --yes schedules');
}

async function cmdSync(arg, flags) {
  const dirs = arg ? [pieceDir(arg)] : ls(SOCIAL).filter(d => fs.existsSync(path.join(d, RECORD)));
  const report = []; let anySent = false;
  for (const dir of dirs) {
    const f = readPiece(dir);
    for (const ch of Object.values(f.channels)) {
      if (!ch.bufferId || !/^scheduled/i.test(ch.status)) continue;
      // Display zone: the one recorded in "Status: scheduled (…, zone)" or the piece's zone.
      const tz = (/,\s*([A-Za-z_]+(?:\/[A-Za-z_+-]+)+|UTC)\)/.exec(ch.status) || [])[1] || ch.tz || undefined;
      let p; try { p = await getPost(ch.bufferId); } catch (e) { report.push({ piece: f.title, channel: ch.key, id: ch.bufferId, status: 'not found in Buffer', detail: e.message.slice(0, 120) }); continue; }
      const row = { piece: f.title, channel: ch.key, id: p.id, status: p.status, time: fmtLocal(p.dueAt, tz), publishing: p.schedulingType };
      if (p.status === 'sent') {
        if (p.schedulingType === 'notification' && !p.externalLink) { row.note = 'notification sent to the phone; the real publication is done in the app and marked by hand'; report.push(row); continue; }
        const date = fmtLocal(p.sentAt || p.dueAt, tz).slice(0, 10); const link = p.externalLink ? p.externalLink.replace(/\/?$/, p.externalLink.includes('?') ? '' : '/') : '';
        row.link = link; row.published = date; anySent = true;
        if (flags.write) { writeFields(f.file, ch.key, { Status: `published (${date}).`, Link: link }); row.record = 'updated'; }
      }
      if (p.status === 'error') row.error = p.error?.message;
      report.push(row);
    }
    if (flags.write && report.some(r => r.record && r.piece === f.title)) {
      const idx = path.join(SOCIAL, 'index.md'); const relPath = path.relative(SOCIAL, f.file);
      if (fs.existsSync(idx) && !fs.readFileSync(idx, 'utf8').includes(relPath)) log(`warning: ${relPath} is not in social/index.md; add its row`);
    }
  }
  console.log(JSON.stringify(report, null, 2));
  if (!report.length) log('no scheduled posts in the piece records');
  if (flags.write && anySent) { const r = bufferCli(['media', 'cleanup', '--yes']); log(`media cleanup: ${JSON.stringify(r.objs.find(o => 'deleted' in o) || {})}`); }
  else if (!flags.write && report.some(r => r.status === 'sent')) log('repeat with --write to update the piece records and clean up the media');
}

const USAGE = `schedule: schedules an approved piece from social/<piece>/ in Buffer (see SKILL.md)
  schedule plan <piece> [--channels instagram,tiktok,youtube] [--type post|story] [--check]
  schedule run <piece> [--channels …] [--force] --yes
  schedule cover <piece> [--channel instagram|tiktok|youtube]
  schedule sync [<piece>] [--write]

Environment: BUFFER_API_KEY, BLOB_READ_WRITE_TOKEN, BUFFER_TIMEZONE (when piece.md sets no zone),
  BUFFER_SECONDARY_TIMEZONE, BUFFER_QUEUE_LIMIT, BUFFER_YOUTUBE_CATEGORY (when the YouTube section has no
  "- Category:"), BUFFER_STATE_DIR, WORKSPACE_ROOT (default: current directory), BUFFER_API_URL, BUFFER_ORGANIZATION.`;

const { pos, flags } = parseArgs(process.argv.slice(2));
const cmd = pos[0];
try {
  if (!cmd || cmd === 'help' || flags.help) { console.log(USAGE); }
  else if (cmd === 'plan') await cmdPlan(pieceDir(pos[1] || die('missing the piece', 2)), flags, false);
  else if (cmd === 'run') { if (!flags.yes) die('run really schedules: add --yes after approval (or use plan to rehearse)', 2); await cmdPlan(pieceDir(pos[1] || die('missing the piece', 2)), flags, true); }
  else if (cmd === 'cover') {
    const dir = pieceDir(pos[1] || die('missing the piece', 2)); const f = readPiece(dir); const key = String(flags.channel === undefined || flags.channel === true ? 'instagram' : flags.channel).toLowerCase();
    if (!CHANNELS[key]) die(`unknown channel: ${key} (instagram, tiktok, youtube)`, 2);
    const v = findVideo(dir, f.slug, key) || die('no video in export/', 2); const c = findCover(dir, key) || die(`no cover-${key}.png/jpg`, 2);
    console.log(JSON.stringify({ ...coverVideo(dir, f.slug, key, v.file, c.file), warnings: [v.warning, c.warning].filter(Boolean) }, (k, val) => typeof val === 'string' && val.startsWith(ROOT) ? path.relative(ROOT, val) : val, 2));
  }
  else if (cmd === 'sync') await cmdSync(pos[1], flags);
  else die(`unknown command: ${cmd}\n${USAGE}`, 2);
} catch (e) { die(e.message, e.code); }
