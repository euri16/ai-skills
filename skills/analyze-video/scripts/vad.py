"""Speech detection with Silero VAD (local, ONNX), shared by takes.sh and cuts.py.

Silero tells speech from noise (breaths, mouth clicks, knocks, room noise) and does not depend on the recording
level. Its edges are not usable for cutting: it marks the in point with about 30 ms of error, the out point about 300 ms late and
sometimes misses a soft consonant at the start. That is why here it decides what has to be cut and the energy sets the edge.
Requires: uv run --with silero-vad --with onnxruntime --with numpy
"""
import numpy as np

SR = 16000
_model = None

def _m():
    global _model
    if _model is None:
        from silero_vad import load_silero_vad
        _model = load_silero_vad(onnx=True)
    return _model

def speech_segments(y, min_silence=0.6, min_speech=0.25):
    """Stretches (start, end) in seconds with speech, separated by at least min_silence without speech. y: float32 mono at 16 kHz."""
    from silero_vad import get_speech_timestamps
    ts = get_speech_timestamps(y, _m(), sampling_rate=SR, threshold=0.5, min_silence_duration_ms=int(min_silence * 1000),
                               min_speech_duration_ms=int(min_speech * 1000), speech_pad_ms=0)
    return [(s["start"] / SR, s["end"] / SR) for s in ts]

def speech_prob(y, t):
    """Silero speech probability (32 ms blocks) mapped to the instants t (seconds from the start of y)."""
    import torch
    m = _m(); m.reset_states()
    x = torch.from_numpy(np.pad(y.astype(np.float32), (0, (-len(y)) % 512)))
    p = np.array([float(m(x[k:k + 512], SR)) for k in range(0, len(x), 512)])
    return np.interp(t, (np.arange(len(p)) * 512 + 256) / SR, p)

def voice_edges(y, a, w0, w1, w0e):
    """Start and end of a take's voice, near Whisper's first (w0, ends at w0e) and last (w1) word.

    Energy in 10 ms windows marks the sound stretches (threshold: 32 dB under the peak and at least 6 dB above the background
    noise). A stretch counts as voice only if Silero hears speech somewhere in it: the consonant attached to the vowel
    comes in whole, and a click or a breath separated by silence stay out. a: second of the clip where y starts.
    """
    n = len(y) // 160
    rms = np.sqrt(np.mean(y[: n * 160].reshape(n, 160) ** 2, axis=1)) + 1e-9
    db = 20 * np.log10(rms)
    t = a + np.arange(n) * 0.01
    speech = speech_prob(y, t - a) >= 0.5
    threshold = max(np.percentile(rms, 10) * 10 ** (6 / 20), rms.max() * 10 ** (-32 / 20))
    sound = rms > threshold
    # stretches: 30 ms of continuous sound, and gaps of up to 40 ms do not split them (the consonant stays joined to its vowel)
    on = np.convolve(np.convolve(sound, np.ones(3), "same") >= 3, np.ones(5), "same") > 0
    d = np.diff(np.r_[0, on.astype(int), 0])
    voice = []
    for i, j in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1):
        k = i + np.flatnonzero(sound[i:j + 1])                         # the edge is the first and the last block with sound
        if len(k) and speech[i:j + 1].any(): voice.append((k[0], k[-1]))
    # Whisper tends to put the first word at 0.0 when the recording starts while speaking even if the voice arrives later:
    # the in-point window reaches the end of that first word
    ins = [k for k, (i, j) in enumerate(voice) if t[j] >= w0 - 0.3 and t[i] <= max(w0 + 0.2, w0e + 0.3)]
    outs = [k for k, (i, j) in enumerate(voice) if t[i] <= w1 + 0.4 and t[j] >= w1 - 0.3]   # a laugh or a comment afterwards does not come in
    if not ins or not outs: return w0, w1
    k0, k1 = min(ins), max(outs)
    # An edge stretch separated from the sentence by 150 ms of silence and 12 dB quieter than it is a sound before or
    # after (breath, murmur), not part of the sentence: the real start of a word does not sound that quiet or detached
    level = lambda k: np.percentile(db[voice[k][0]:voice[k][1] + 1], 95)
    sentence = max(level(k) for k in range(k0, k1 + 1))
    while k0 < k1 and t[voice[k0 + 1][0]] - t[voice[k0][1]] >= 0.15 and level(k0) < sentence - 12: k0 += 1
    while k1 > k0 and t[voice[k1][0]] - t[voice[k1 - 1][1]] >= 0.15 and level(k1) < sentence - 12: k1 -= 1
    return t[voice[k0][0]], min(t[voice[k1][1]], w1 + 0.6) + 0.01
