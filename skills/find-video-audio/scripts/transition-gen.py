#!/usr/bin/env python3
"""Block transition candidates: each riser of a folder + the brand motif at the landing.

Usage: transition-gen.py <output_dir> <risers_dir> <hit_without_motif.wav> <bass_dB> <marimba_dB> --notes <note1>,<note2> [--hit-at <seconds>|auto]
<bass_dB> and <marimba_dB>: gain in dB added to each layer of the motif. At 0 the bass peaks just under the riser
(0.55 against 0.6 of full scale) and the marimba about 11 dB under it (0.16); -20 in <bass_dB> leaves the bass about
20 dB under the riser.
--notes is required: the two notes of the workspace's brand motif in the bass register (octave 2, for example E2,A2).
--hit-at: where the hit's transient is inside its file, in seconds (default 0.20); "auto" finds it at the first
sample that reaches half of the peak. Only the hit's click is used, on each note of the motif.
WARNING: the .wav files of <output_dir> are deleted first. The extension and a " trim" suffix of a riser's file name
are dropped from the output names.
Needs numpy and ffmpeg.
"""
import glob
import sys, os, shutil, subprocess, wave
def die(msg, code=2): print(msg, file=sys.stderr); sys.exit(code)
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"): print(__doc__.strip()); sys.exit(0)
try: import numpy as np
except ImportError: die("numpy is missing for this python3: python3 -m pip install --user numpy")
def split_args(argv, flags):
    """Separates positional arguments from the --flag value pairs, wherever they are written."""
    pos, opt, i = [], {}, 0
    while i < len(argv):
        if argv[i] in flags:
            if i + 1 >= len(argv): die("%s needs a value" % argv[i])
            opt[argv[i]] = argv[i + 1]; i += 2
        elif argv[i].startswith("--"): die("Unknown option: %s" % argv[i])
        else: pos.append(argv[i]); i += 1
    return pos, opt
def number(text, what):
    try: return float(text)
    except ValueError: die("%s must be a number, not \"%s\"" % (what, text))
SR = 48000
NAMES = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,"G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}
def freq(n):
    try: return 440.0 * 2 ** ((NAMES[n[:-1]] - 9 + 12 * (int(n[-1]) - 4)) / 12)
    except (KeyError, ValueError, IndexError): die("\"%s\" is not a note: write the name and the octave, such as E2, F#2 or Bb4" % n)
def two_notes(opt):
    if "--notes" not in opt: die("missing --notes <note1>,<note2>: the brand motif from the workspace's brand guide")
    parts = opt["--notes"].split(",")
    if len(parts) != 2: die("--notes takes two notes separated by a comma (E2,A2), not \"%s\"" % opt["--notes"])
    return freq(parts[0].strip()), freq(parts[1].strip())
def load(p, what="audio", channels=1):
    if not os.path.isfile(p): die("%s not found: %s" % (what, p))
    if not shutil.which("ffmpeg"): die("ffmpeg is not installed: this script needs it.")
    x = np.frombuffer(subprocess.run(['ffmpeg','-v','quiet','-i',p,'-ac',str(channels),'-ar',str(SR),'-f','f32le','-'],stdout=subprocess.PIPE).stdout, dtype=np.float32).copy()
    if len(x) == 0 or np.abs(x).max() == 0: die("%s has no audio that ffmpeg can read: %s" % (what, p), 1)
    return x
def hit_instant(x, opt, path):
    """Seconds from the start of the hit file to its transient: --hit-at <seconds>, --hit-at auto or 0.20."""
    v = opt.get("--hit-at", "0.20")
    if v == "auto":
        t = max(0.0, int(np.argmax(np.abs(x) >= 0.5 * np.abs(x).max())) / SR - 0.002)
        print("hit transient found at %.3f s" % t)
    else:
        t = number(v, "--hit-at")
    if t < 0 or len(x) < int((t + 0.06) * SR):
        die("%s lasts %.2f s and its transient is expected at %.2f s: pass --hit-at <seconds> or --hit-at auto" % (path, len(x) / SR, t), 1)
    return t
def click(x, t):
    """The hit's click: 60 ms from its transient, without the lows, to give the synthesized bass a real attack."""
    tr = x[int(t*SR):int((t+0.06)*SR)].copy()
    X = np.fft.rfft(tr); fr = np.fft.rfftfreq(len(tr), 1/SR); X[fr < 300] *= (fr[fr < 300]/300)**2; tr = np.fft.irfft(X, len(tr))
    tr *= np.linspace(1,0,len(tr))**0.5; peak = np.abs(tr).max()
    return tr / peak if peak > 0 else tr
pos, opt = split_args(sys.argv[1:], ("--notes", "--hit-at"))
if len(pos) != 5: die(__doc__.strip())
out, rdir, hitpath, dbb, dbm = pos; GAP = 0.22; rng = np.random.default_rng(5)
F1, F2 = two_notes(opt)
BASS, MAR = 0.55*10**(number(dbb, "<bass_dB>")/20), 0.16*10**(number(dbm, "<marimba_dB>")/20)
risers = sorted(glob.glob(os.path.join(rdir, "*.wav")))
if not risers: die("No .wav risers in %s" % rdir, 1)
if os.path.abspath(out) == os.path.abspath(rdir): die("<output_dir> is emptied first: it cannot be the risers folder")
def osc(ftrack, amp, drive=3.0):
    ph = 2*np.pi*np.cumsum(ftrack)/SR; return np.tanh(drive*np.sin(ph)*amp)/np.tanh(drive)
orig = load(hitpath, "Hit"); tr = click(orig, hit_instant(orig, opt, hitpath))
def bass_motif():
    T = GAP + 1.0; t = np.arange(int(T*SR))/SR
    a_env = np.exp(-t*2.0)*np.minimum(1, t/0.004)*np.clip(1-(t-GAP)/0.08, 0, 1)
    t2 = np.maximum(t-GAP, 0); b_env = np.where(t >= GAP, np.exp(-t2*3.2)*np.minimum(1, t2/0.004), 0)
    y = osc(F1*(1+1.2*np.exp(-t*45)), a_env)*0.9 + osc(np.where(t>=GAP, F2*(1+1.2*np.exp(-t2*45)), F2), b_env)
    s = int(GAP*SR); y[:len(tr)] += tr*0.5; y[s:s+len(tr)] += tr*0.7
    n = int(0.08*SR); y[-n:] *= np.linspace(1,0,n); return y
def marimba(f, dur, vel=1.0):
    t = np.arange(int(dur*SR))/SR
    y = (np.sin(2*np.pi*f*t)*np.exp(-t*3.8) + 0.45*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*14) + 0.15*np.sin(2*np.pi*10.1*f*t)*np.exp(-t*28))
    return (y + rng.normal(0,1,len(t))*np.exp(-t*900)*0.2) * np.minimum(1, t/0.002) * vel
def marimba_motif():
    a = marimba(F1*2, GAP+0.25, 0.8); n = int(0.12*SR); a[-n:] *= np.linspace(1,0,n); b = marimba(F2*2, 0.9)
    y = np.zeros(int((GAP+1.0)*SR)); y[:len(a)] += a; s = int(GAP*SR); y[s:s+len(b)] += b; return y
def save(p, y):
    y = np.clip(y, -1, 1); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([y,y],1)*32767).astype("<i2").tobytes()); w.close()
os.makedirs(out, exist_ok=True)
for f in glob.glob(out + "/*.wav"): os.remove(f)
bm = bass_motif(); mm = marimba_motif(); seq = []
for i, rp in enumerate(risers, 1):
    r = load(rp, "Riser"); name = os.path.splitext(os.path.basename(rp))[0]
    if name.endswith(" trim"): name = name[:-len(" trim")]
    land = len(r); start = land - int(GAP*SR)
    base = np.zeros(start + len(bm) + int(0.2*SR)); base[:len(r)] += r / np.abs(r).max() * 0.6
    ref = base * (0.9/np.abs(base).max()); save(out + "/%da %s, without motif.wav" % (i, name), ref)
    v1 = base.copy(); v1[start:start+len(bm)] += bm * BASS; v1 *= 0.9/np.abs(v1).max(); save(out + "/%db %s, tuned bass.wav" % (i, name), v1)
    v2 = base.copy(); v2[start:start+len(bm)] += bm * BASS; v2[start:start+len(mm)] += mm / np.abs(mm).max() * MAR; v2 *= 0.9/np.abs(v2).max(); save(out + "/%dc %s, bass and marimba.wav" % (i, name), v2)
    seq += [ref, np.zeros(int(0.8*SR)), v1, np.zeros(int(0.8*SR)), v2, np.zeros(int(1.4*SR))]
save(out + "/0 all in a row (each riser without motif, bass, bass and marimba).wav", np.concatenate(seq))
print("motif: bass %s dB, marimba %s dB added to their default gains (0.55 and 0.16)" % (dbb, dbm))
