# Pacing: words, speech and visual cadence

Sources are linked where each figure is used; links checked on 2026-11-20. A source named without a link is given as reported.

## Words per minute depend on the language and on the creator

Languages carry a similar amount of information per second but pack it differently, so the same script takes a different time in each one, and a script translated or adapted between languages without trimming almost always runs over time. Two languages as examples ([Pellegrino, Coupé and Marsico 2011](https://www.gwern.net/doc/cs/algorithm/information/2011-pellegrino.pdf) for the syllable rates):

| | Example: English | Example: Spanish |
|---|---|---|
| Syllables per second | 6.19, with more information per syllable | 7.82, with less information per syllable |
| Reference pace | Mean of 156 words per minute in educational videos; 160 is a common recommendation for presentations ([Guo, Kim and Rubin 2014](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf)) | 126 to 179 words per minute perceived as "normal", mean 152 (Wainschenker et al. 2002, cited in [Schwab 2015](https://www.redalyc.org/pdf/332/33267121002.pdf)) |
| News presenters | About 168 words per minute (BBC bulletins, Rodero 2012 as reported) | 207 words per minute (Rodero 2012, cited in Schwab 2015) |

For any other language, look for a published reference for that language. In every case the figure that rules is the creator's measured pace: if there is a timed transcript of an earlier video (`social/<piece>/source/recording/transcript.srt` or `edit/analysis/final-video/transcript.srt`), divide its words by the spoken minutes and budget with that value.

In educational video, speaking faster correlates with more engagement, but because speed is a proxy for enthusiasm: "speeding up an unenthusiastic instructor might not improve engagement" (Guo, Kim and Rubin 2014, 6.9 million video sessions). Forcing speed does not help; editing out filler words and empty pauses does.

## Word budget by length

Words are seconds times words per minute divided by 60. The middle column is the band where both example languages sit; replace it with the creator's measured pace when it is known.

| Length | Slow (130 wpm) | Middle (150 to 170 wpm) | Fast (190 wpm) | What fits |
|---|---|---|---|---|
| 15 s | ~32 | 38 to 42 | ~48 | One idea, hook and payoff |
| 30 s | ~65 | 75 to 85 | ~95 | Hook, two beats, payoff |
| 45 s | ~98 | 112 to 128 | ~143 | Hook, three beats, payoff, short CTA |
| 60 s | ~130 | 150 to 170 | ~190 | Up to three points with an example |
| 90 s | ~195 | 225 to 255 | ~285 | Explanation with a demo |
| 120 s | ~260 | 300 to 340 | ~380 | Explanation with a demo and a second example |
| 180 s | ~390 | 450 to 510 | ~570 | Mini explainer; only with a demo or story that sustains it |

These figures are arithmetic, not measurements of real scripts. Without the creator's pace, aim for the center of the middle band and deliver an ordered list of cuts, because what gets cut when time runs over is the ending, which is where the payoff and the CTA are. Count the words of the spoken script when delivering. The re-hooks each length needs follow the rule in `structures.md`.

On-screen text: TikTok's ad guide says "We recommend displaying 5-10 words per second when using text" ([TikTok for Business](https://ads.tiktok.com/help/article/creative-best-practices?lang=en)), which as a reading speed equals 300 to 600 words per minute. Netflix's subtitle guides are the readability reference: 42 characters per line, two lines at most and, for adult programs, a ceiling of characters per second set per language: for example, [20 in one guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-Timed-Text-Style-Guide) and [17 in another](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997-Castilian-Latin-American-Spanish-Timed-Text-Style-Guide), roughly 3 to 4 words per second. Read the TikTok figure as "short blocks", not as a pace: subtitles of 3 to 5 words and headlines of 2 to 6.

On-screen budget of a visual video without voice. The text is read, not heard, so the budget is counted in characters: a screen needs its characters divided by 17 (the conservative default of `edit-short-video`, the lower of the two example ceilings above; it is configurable per language, so use the published ceiling of the piece's language when it has one), never under 1 second, plus about half a second for the scene to arrive and the time its visual needs to act. Over a whole piece that leaves about two thirds of the length for reading: roughly 170 characters in 15 s, 340 in 30 s and 510 in 45 s at the default ceiling, which in English is about 30, 60 and 90 words. These figures are arithmetic from the reading ceiling, not measurements of real pieces. A screen that stays after it has been read feels slow, so the fix for a long piece is fewer words, not longer screens. A narrated visual video is budgeted like any spoken script, with the table above.

Everything counted in words in this file assumes a language written with spaces between words. For a language without them, budget in characters or syllables with a published reference for that language, and keep the creator's measured pace as the figure that rules.

## Visual cadence: change with a purpose

The variable with backing is not the number of cuts but the speed at which new information comes in. Mario Joos, retention strategist: "It's not the cutting speed, it's the speed at which you introduce progressive novel information" ([interview with Vidpros](https://vidpros.com/retention-editing-what-you-can-learn-from-mario-joos/)). He distinguishes progressive content (advances the video's goal) from non-progressive (jokes, decoration): do not stack several non-progressive items in a row; one playful moment at a time.

For educational and opinion talking heads (recommendations, not measured thresholds):

- One visual change with a purpose every 5 to 10 seconds: example on screen, a close-up or screenshot, term pinned in text, change of framing when the beat changes, going from camera to supporting material or back.
- Held shot when the explanation demands precision or when a pause is the device.
- A static talking head for more than 30 to 40 seconds with no change is a risk worth checking against the account's retention curve.
- Interleaving camera and functional material retains more than material alone; in the study by Guo, Kim and Rubin, students engaged 1.5 to 2 times as long with tutorials drawn while explaining as with slides.

For sketches: in a study of 914 TikTok videos by five comedy creators from Spain, the pieces built for a faster pace, with hurried acting and editing by cuts, were the most rewarded ([Molina-Fuster and Díaz-Lucena 2024](https://revistascientificas.us.es/index.php/Ambitos/article/download/24546/22552/121249)). That is acting speed and cuts with a comic function, not effects, flashes or shouting, and it is evidence for one language and one country.

## What over-editing is

The "retention editing" style (a cut every second or two, loud sound effects, flashes, no pauses) was abandoned by its leading exponent. MrBeast in March 2024: "This past year i've slowed down our videos, focused on story telling, let scenes breathe, yelled less, more personality, longer videos" and "our views have skyrocketed" ([Tubefilter](https://tubefilter.com/2024/03/04/mrbeast-editing-style-number-of-cuts-per-video/), which counted 38 cuts in a sampled minute of a 2023 video and 23 in one from 2024). An editor of large channels, Dan Hinz: "Fast cuts and lots of graphics won't fix a bad story" ([Descript](https://descript.com/blog/article/advice-for-video-editors-from-youtube-video-editors)).

Signs of over-editing in a script or edit plan:

- Cuts or zooms without new information.
- Sound effects or flashes as a substitute for a beat.
- Several jokes or non-progressive devices in a row.
- On-screen text that literally repeats what is said, in every sentence.
- Filler b-roll that explains nothing.

The argument against over-editing is about credibility and clarity; this skill makes no claim about cognitive harm.

## Rhythm in waves

Jenny Hoyos describes the rhythm of a Short that retains as a roller coaster: a quick hook, a medium-paced middle, and the reminder that people remember their favorite part and the ending ([vidIQ interview](https://rosetta.to/u/vidiq/how-jenny-hoyos-actually-makes-viral-shorts)). Her advice on speed: "do not talk fast, just talk more concise". That is why the payoff and the CTA close the video and the last cut is hard, with no outro.

## Retention curve

Consistent shape across the sources with data: steep drop at the start (the "nose"), gentle descent in the body and another break at the end. Wistia measures an average drop of 4.9 % in the nose for videos of 1 to 2 minutes ([Wistia](https://wistia.com/blog/understanding-audience-retention)); Vidyard, 65 % of viewers reaching the end of business videos under one minute ([Vidyard benchmark](https://www.vidyard.com/video-benchmark/)). There is no public per-second data for Reels, TikTok or Shorts: the "at 3 seconds" percentages that circulate have no source. Use the account's curves from Instagram Insights and YouTube Studio to know where this audience leaves and adjust the re-hooks to that point. Quick reading: drop in the first 3 to 5 seconds, the problem is the hook; drop later, the problem is the script or the broken promise.

## Writing for the ear

- One idea per sentence; active voice; verbs.
- Few figures in a row; one figure per sentence and on screen.
- Read aloud as a test of time and naturalness.
- Hook and payoff word for word; the body in sentences the creator can say in their own words. There is no evidence that a teleprompter or bullets are better; the hybrid stance is reasonable.
- Edit out filler words and empty pauses in post-production; pauses with a purpose (before a punchline, after a figure) are kept.
- Subtitles always; design so it works with and without sound.
