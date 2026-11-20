# Find a gesture or an expression in the takes

When a specific instant is needed (a gesture, a hand in a certain place, an expression, an object in view) for a cover, a graphic or a shot of the edit, search for it in all the takes before asking for a new photo or editing one with AI. The gesture lasts tenths of a second and usually repeats across several takes with variations: the best version does not have to be in the take chosen for the video.

## Steps

1. **Locate the stretch in each take.** With the per-word transcription (`takes.json` in a recording by sentences, `words.json` in a video), find in which seconds of each take the gesture happens (usually right after a word or after the sentence).
2. **Go through each take.** One sheet per take with about 3 s around that moment at 6 fps:

   ```bash
   uv run -q --with pillow python scripts/frame-sheet.py <video> <work>/sheet-<take>.png <start> 3
   ```

   Look at all the sheets and note in which take and at what time it comes closest to what was asked.
3. **See the instant frame by frame.** In the candidate takes, a 0.8 s stretch at 12.5 fps cropped to the area that matters (for example the face and the hand), stacked in a single image to compare:

   ```bash
   uv run -q --with pillow python scripts/frame-sheet.py <video> <work>/fine-<take>.png <start> 0.84 --fps 12.5 --crop <x,y,w,h> --width 300 --cols 11
   ```

4. **Present the candidates.** Extract 3 to 4 frames at full resolution (`ffmpeg -ss <t> -i <video> -frames:v 1`), compose them side by side with their number, take and time, open the image with `open` and recommend one saying what is seen (where the hand is, how the mouth is, the eyes).
5. **If it does not exist.** Say precisely what does not appear in any take (for example, "while the finger points at the screen the eyes look down; they come back to the camera only when the hand has dropped") and propose the ways out: a new photo taken for the piece or an AI edit of the closest take with `generate-ai-images`.

Everything goes in the piece's folder (`cover-src/frames/` for a cover, `edit/tests/` for the edit).
