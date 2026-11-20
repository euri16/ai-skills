# Generation prompts

Generation is done with Codex (`codex exec`) and its image tool. The prompt can be in English, whatever language the user speaks: it is followed better. Every prompt states the output files, that no other file is touched and that it must not finish until they exist.

## How to run it

`scripts/generate.sh <folder> <prompt.txt> <output1.png> [output2.png ...] [-- image1 image2 ...]`

- The prompt goes through standard input: `-i` of `codex exec` accepts several images and swallows whatever comes after, so a prompt passed as an argument after the images does not arrive.
- It runs in the working folder with `-s workspace-write`, so it writes only there.
- The script stops before running Codex if the folder, the prompt file or an attached image is missing. Sometimes Codex finishes without saving (it cuts off halfway); the script detects it because an output file is missing, exits with an error and keeps Codex's log in the folder: read it and relaunch.
- It takes one to several minutes per image: run it in the background and move on to something else.

## Mode 1: edit a real photo of the creator

```
Use your image generation tool ($imagegen) to EDIT the first attached photo (<base>).
Keep the person exactly identical: same face and features, skin, hair, <accessories>, <expression>, clothes, <objects they hold>,
room, lighting, framing, aspect ratio and resolution.
Change ONLY <what changes, described with physical detail: position, shape, distance, direction>.
Use the second photo (<reference>) only as reference for <what to take from it>.
Photorealistic, natural anatomy, five fingers, no text, no effects.
Make <n> versions: <name1> with <variant 1>; <name2> with <variant 2>.
Save them in the current directory. Do not modify any other file and do not finish until the files exist.
```

- Describe what changes with relative measures and positions ("the hand raised to shoulder height, palm toward the camera", "the cup tilted about 30 degrees toward the lens") instead of loose adjectives.
- Ask for the same aspect ratio and resolution as the base: the face check compares the result against it.
- If the user shares a reference photo (a gesture, a pose, an object), it is passed as the second image and the prompt says what to take from it.
- For a variant very close to one already approved, edit the approved one (not the original) and ask that only the detail change: that way the face stays the same across versions.

## Mode 2: effects and elements to composite

```
Use your image generation tool ($imagegen) to CREATE a new photorealistic image, <width>x<height>, PURE BLACK background (#000000),
nothing else in the image: no people, no objects, no text<, no smoke clouds>.
<The phenomenon with its physical traits>. Colors only: <brand palette colors that fit>.
<Variants if any>. Save as <name>.png in the current directory. Do not modify any other file and do not finish until the file exists.
```

The palette colors come from the workspace's `brand-guide/visual-identity.md`.

Describe the phenomenon, do not just name it:

| Request | Traits that make it recognizable |
|---|---|
| Explosion | White flash at the center, short shockwave halo, particles and fragments going out in all directions (360 degrees) with trails pointing outward, shorter near the center, some blurred embers |
| Welding or angle-grinder sparks | Fan-shaped jet from a point, long thin trails in one direction |
| Smoke or steam | Soft wisps with variable density, diffuse edges, no glow of its own. Light smoke on pure black; dark smoke on pure white |
| Confetti | Flat colored pieces with spin and motion blur, falling with gravity |

The background follows from how the element will be blended (`compose-effects.md`), and the image tool is never asked for transparency:

| Element | Background to ask for | How it is blended |
|---|---|---|
| Emits light, or is light and translucent (fire, sparks, flashes, white smoke, steam, a flour puff) | Pure black (`#000000`), with the template above | Screen mode: the black disappears |
| Dark and translucent (dark smoke, a shadow, dust) | Pure white (`#FFFFFF`): the template above with the background changed | Multiply mode: the white disappears |
| Opaque (an object, a prop, confetti pieces, a texture patch) | One plain color the element does not contain, with the template below | Cut out with `design-reel-cover/scripts/cutout.py --model isnet-general-use` |

```
Use your image generation tool ($imagegen) to CREATE a new photorealistic image, <width>x<height>:
<the object with its material, angle and light>, whole and centered, with free space around it, on a PLAIN UNIFORM
<color the object does not contain> background with no shadow on the background, no gradient and no floor line.
No people, no text, no logos, no brand names.
Save as <name>.png in the current directory. Do not modify any other file and do not finish until the file exists.
```

The cutout runs with `uv` from the `design-reel-cover` skill, with the general model because the script's default one is trained for people:

```bash
uv run --python 3.11 --with "rembg[cpu]" python <skills>/design-reel-cover/scripts/cutout.py <work>/<name>.png <work>/<name>-cut.png --model isnet-general-use
```

Review the cutout at full size: no halo of the background color, no bitten edge and no missing thin parts.

## Mode 3: general images

```
Use your image generation tool ($imagegen) to CREATE a new <photorealistic | illustrated in style X> image, <width>x<height>:
<scene, objects, light, framing>. <If there are people: fictional people who do not resemble any real person>.
No text, no logos, no brand names. Colors: <palette if applicable>.
Save as <name>.png in the current directory. Do not modify any other file and do not finish until the file exists.
```
