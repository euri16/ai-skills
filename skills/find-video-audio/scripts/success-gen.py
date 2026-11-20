#!/usr/bin/env python3
"""Brand motif (first note short, the second 0.22 s later and sustained) in four bright timbres for the success sound.

Usage: success-gen.py <output_dir> --notes <note1>,<note2>
--notes is required: the two notes of the workspace's brand motif in the high register (octave 5, for example E5,A5).
Writes one WAV per timbre and "0 all four in a row.wav" for listening. Needs numpy.
"""
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
pos, opt = split_args(sys.argv[1:], ("--notes",))
if len(pos) != 1: die(__doc__.strip())
out = pos[0]; GAP = 0.22; rng = np.random.default_rng(21)
NOTE1, NOTE2 = two_notes(opt)
def env_att(t, a): return np.minimum(1, t/a)
def glockenspiel(f, dur, vel=1.0):  # glockenspiel: inharmonic partials, long clean tail
    t = np.arange(int(dur*SR))/SR
    y = sum(a*np.exp(-t*d)*np.sin(2*np.pi*r*f*t) for r, a, d in ((1, 1.0, 2.2), (2.76, 0.45, 5.0), (5.4, 0.2, 9.0), (8.9, 0.08, 14.0)))
    return y*env_att(t, 0.001)*vel
def marimba(f, dur, vel=1.0):       # the same marimba as motif-gen.py, in the high register
    t = np.arange(int(dur*SR))/SR
    y = (np.sin(2*np.pi*f*t)*np.exp(-t*5) + 0.45*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*16) + 0.15*np.sin(2*np.pi*10.1*f*t)*np.exp(-t*30))
    return (y + rng.normal(0,1,len(t))*np.exp(-t*900)*0.15)*env_att(t, 0.002)*vel
def crystal(f, dur, vel=1.0):       # notification tone: slightly detuned sines, soft attack, very clean
    t = np.arange(int(dur*SR))/SR
    y = sum(np.sin(2*np.pi*f*(1+d)*t + p) for d, p in ((0, 0), (0.003, 1.1), (-0.003, 2.3)))/3
    y += 0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*6)
    return y*np.exp(-t*3.0)*env_att(t, 0.012)*vel
def fm_bell(f, dur, vel=1.0):       # FM bell, electric piano/DX7 style
    t = np.arange(int(dur*SR))/SR
    idx = 2.5*np.exp(-t*4); mod = np.sin(2*np.pi*f*3.5*t)*idx
    y = np.sin(2*np.pi*f*t + mod)*np.exp(-t*3.2) + 0.2*np.sin(2*np.pi*2*f*t)*np.exp(-t*8)
    return y*env_att(t, 0.002)*vel
def reverb(x, rt=0.7, mix=0.2):
    n = int(rt*SR); t = np.arange(n)/SR; env = np.exp(-6.9*t/rt)
    L = rng.normal(0,1,n)*env; R = rng.normal(0,1,n)*env; L /= np.sqrt((L**2).sum()); R /= np.sqrt((R**2).sum())
    size = len(x)+n; X = np.fft.rfft(x, size); dry = np.zeros(size); dry[:len(x)] = x
    return np.stack([dry+mix*np.fft.irfft(X*np.fft.rfft(L,size),size), dry+mix*np.fft.irfft(X*np.fft.rfft(R,size),size)], 1)
def motif(inst, ring=1.1):
    a = inst(NOTE1, GAP+0.3, 0.85); n = int(0.15*SR); a[-n:] *= np.linspace(1,0,n); b = inst(NOTE2, ring, 1.0)
    y = np.zeros(int((GAP+ring)*SR)); y[:len(a)] += a; s = int(GAP*SR); y[s:s+len(b)] += b
    n = int(0.1*SR); y[-n:] *= np.linspace(1,0,n); return y
def save(p, y):
    y = np.clip(y, -1, 1); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y*32767).astype("<i2").tobytes()); w.close()
os.makedirs(out, exist_ok=True)
opts = (("1 glockenspiel", glockenspiel), ("2 bright marimba", marimba), ("3 notification crystal", crystal), ("4 electric bell", fm_bell))
sounds = {n: motif(f) for n, f in opts}
rms = lambda y: np.sqrt((y**2).mean()); tgt = np.mean([rms(y) for y in sounds.values()])
seq = []
for n, _ in opts:
    y = reverb(sounds[n]*(tgt/rms(sounds[n]))); y *= 0.8/np.abs(y).max(); save(out+"/"+n+".wav", y); seq += [y, np.zeros((int(0.9*SR),2))]
save(out+"/0 all four in a row.wav", np.concatenate(seq)); print("ok")
