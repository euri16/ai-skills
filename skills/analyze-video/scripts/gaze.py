"""Frame and eye movement around the end of a take's voice, and the audible end of its last syllable; used by cuts.py.

- frame: difference between consecutive frames of the whole frame at low resolution. It catches the body leaning back or
  forward and the hands entering.
- eyes: how different the eye band is from its state at a reference instant (the end of the voice). Each frame is aligned
  with sub-pixel precision on the face of the reference frame and slightly blurred, so a head movement and the compression
  noise do not count and a glance of a few frames does: the eyes leave their position and the band changes.
- mouth: the same for the mouth band, against its shape at the end of the voice. The lips closing, pressing or smiling after
  the last syllable is a face change: the take is cut before it, even if that trims the tail of the final consonant.
A jump is a value above the threshold measured on the take itself while speaking, never under its floor: FRAME_JUMP times
the median of the frame over the last second of the voice, and EYES_JUMP times the 90th percentile of the eyes over its last
0.3 s (further back the expression of the sentence itself already differs from the reference and would raise the threshold).

Frames are read at the clip's own rate: resampling to another rate repeats frames, and the repeated ones measure zero.
They keep the clip's proportions, with the short side at 1080 px (frame_size): a vertical, a horizontal and a square
recording are measured the same way and the face is never stretched.

Usage as a script, to look at a clip: python gaze.py <video> <start> <end> <reference>
Requires: numpy, opencv-python-headless<5 (OpenCV 4: version 5 does not ship the face cascade).
"""
import json, subprocess, sys
import numpy as np
import cv2

FRAME_JUMP, EYES_JUMP, MOUTH_CHANGE = 2.0, 1.3, 0.5
FLOOR = {"frame": 1.0, "eyes": 6.0, "mouth": 0.4}
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def _fps(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", f],
                       capture_output=True, text=True, check=True).stdout.split()[0].strip(",").split("/")   # side data adds a trailing comma
    return float(r[0]) / float(r[1] if len(r) > 1 else 1)


def frame_size(f, short):
    """(width, height) of the clip as ffmpeg decodes it (rotation applied), scaled so the short side measures `short`."""
    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height:stream_tags=rotate:stream_side_data=rotation", "-of", "json", f],
                                   capture_output=True, text=True, check=True).stdout)["streams"][0]
    w, h = st["width"], st["height"]
    turn = [d["rotation"] for d in st.get("side_data_list", []) if "rotation" in d] or [st.get("tags", {}).get("rotate", 0)]
    if round(abs(float(turn[0]))) % 180 == 90: w, h = h, w
    k = short / min(w, h)
    return (short, max(short, round(h * k / 2) * 2)) if w <= h else (max(short, round(w * k / 2) * 2), short)


def _frames(f, a, b, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-an",
                          "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w), _fps(f)


class Gaze:
    """Signals of a clip between a and b, with the face taken at the instant ref."""

    def __init__(self, f, a, b, ref):
        W, H = frame_size(f, 1080)
        v, fps = _frames(f, a, b, W, H)
        self.t = a + np.arange(len(v)) / fps
        self.fps = fps
        small = v[:, ::10, ::10].astype(np.float32)                                    # a tenth of the size for the whole frame
        self.frame = np.r_[0, np.abs(np.diff(small, axis=0)).mean(axis=(1, 2))]
        self.eye_bands = None
        k = self._i(ref)
        faces = CASCADE.detectMultiScale(v[k], 1.1, 5, minSize=(180, 180))
        if not len(faces): return
        x, y, w, h = max(faces, key=lambda c: c[2] * c[3])
        face = v[k, y:y + h, x:x + w].astype(np.float32)
        window = cv2.createHanningWindow((w, h), cv2.CV_32F)
        y0, y1, x0, x1 = y + int(0.22 * h), y + int(0.52 * h), x + int(0.12 * w), x + int(0.88 * w)   # eye band
        m0, m1, n0, n1 = y + int(0.68 * h), min(H, y + int(1.02 * h)), x + int(0.25 * w), x + int(0.75 * w)   # mouth band
        self.eye_bands, self.mouth_bands = [], []
        for fr in v:
            (dx, dy), _ = cv2.phaseCorrelate(face, fr[y:y + h, x:x + w].astype(np.float32), window)
            al = cv2.warpAffine(fr.astype(np.float32), np.float32([[1, 0, -dx], [0, 1, -dy]]), (W, H))
            self.eye_bands.append(cv2.GaussianBlur(al[y0:y1, x0:x1], (0, 0), 2))
            self.mouth_bands.append(cv2.GaussianBlur(al[m0:m1, n0:n1], (0, 0), 2))

    def _i(self, s):
        return int(np.clip(round((s - self.t[0]) * self.fps), 0, len(self.t) - 1))

    def eyes(self, ref):
        """Difference of each frame's eye band from the band at the instant ref."""
        if self.eye_bands is None: return None
        b = self.eye_bands[self._i(ref)]
        return np.array([np.abs(x - b).mean() for x in self.eye_bands])

    def mouth_change(self, ref):
        """First instant after ref (the end of the voice) where the mouth leaves the shape of the last syllable: the lips
        closing, pressing or smiling once the word is over. The scale is how much the mouth moves in the 0.06 to 0.02 s
        before ref; the change counts from MOUTH_CHANGE times that scale, never under its floor. None without a face or a change."""
        if self.eye_bands is None: return None
        b = self.mouth_bands[self._i(ref)]
        d = np.array([np.abs(x - b).mean() for x in self.mouth_bands])
        before = d[(self.t >= ref - 0.065) & (self.t <= ref - 0.015)]
        if not len(before): return None
        threshold = max(MOUTH_CHANGE * float(np.median(before)), FLOOR["mouth"])
        hits = self.t[(self.t > ref + 1e-6) & (d > threshold)]
        return float(hits[0]) if len(hits) else None

    def first_jump(self, ref, voice0, since, until):
        """First instant in (since, until] where the frame or the eyes (compared with ref) jump; the thresholds come from the
        voice before ref. None if there is no jump."""
        t = self.t
        def stretch(s):
            h = (t >= max(voice0, ref - s)) & (t <= ref)
            return h if h.sum() > 2 else t <= ref
        jump = self.frame > max(FRAME_JUMP * np.median(self.frame[stretch(1.0)]), FLOOR["frame"])
        o = self.eyes(ref)
        if o is not None:
            jump |= o > max(EYES_JUMP * np.percentile(o[stretch(0.3)], 90), FLOOR["eyes"])
        hits = t[(t > since) & (t <= until) & jump]
        return float(hits[0]) if len(hits) else None


def audible_end(f, end, sr=48000):
    """Audible end of the last syllable, including a final "s": the energy above 4 kHz is followed from the end of the voice
    until it falls to 8 dB above the background, with gaps of up to 20 ms; at most 0.25 s later."""
    a, b = max(0, end - 0.2), end + 0.45
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-vn", "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, np.int16).astype(float) / 32768
    n = sr // 100
    if len(y) < 4 * n: return end
    Y = np.fft.rfft(y[: len(y) // n * n].reshape(-1, n) * np.hanning(n), axis=1)
    high = 10 * np.log10((np.abs(Y[:, np.fft.rfftfreq(n, 1 / sr) > 4000]) ** 2).sum(1) + 1e-12)
    t = a + np.arange(len(high)) * 0.01
    sounds = high > max(np.percentile(high, 10), high.max() - 50) + 8          # digital silence is not the room's background
    i, gap, last = int(np.searchsorted(t, end)), 0, None
    while i < len(t) and t[i] <= end + 0.25:
        if sounds[i]: last, gap = t[i] + 0.01, 0
        else:
            gap += 1
            if gap > 2: break
        i += 1
    return max(end, last) if last is not None else end


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Usage: python gaze.py <video> <start> <end> <reference>   (seconds)")
    f, a, b, ref = sys.argv[1], *map(float, sys.argv[2:5])
    m = Gaze(f, a, b, ref)
    o = m.eyes(ref)
    for i in range(len(m.t)):
        print(f"{m.t[i]:6.2f} frame {m.frame[i]:5.2f} eyes {'-' if o is None else f'{o[i]:5.2f}'}")
    print("first jump after the reference:", m.first_jump(ref, a, ref, b))
    print("mouth changes at:", m.mouth_change(ref))
