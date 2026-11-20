# Evidence behind the hook decisions

This file summarizes what justifies each rule of the skill, so the agent can explain a recommendation or settle a doubt without redoing the research. Sources consulted on 2026-10-26; links checked on 2026-11-20. A source named without a link is given as reported: verify it before quoting it in public.

## Time window

- Instagram: its creators blog asks to start with an engaging hook in the first three seconds and to watch what share of viewers is still there after them ([Instagram for Creators, 2025-02-26](https://creators.instagram.com/blog/helping-creators-of-all-sizes-break-through)).
- TikTok for Business (last updated June 2025): "Introduce your content proposition in the first 3 seconds", "Prioritize your hook in the first 6 seconds" and "We recommend displaying 5-10 words per second when using text" ([creative best practices](https://ads.tiktok.com/help/article/creative-best-practices?lang=en)). As a reading pace the last figure is implausible: Netflix's subtitle guides set a ceiling per language for adult programs, for example [17 characters per second in one guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997-Castilian-Latin-American-Spanish-Timed-Text-Style-Guide) and [20 in another](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-Timed-Text-Style-Guide), roughly 3 to 4 words. Read TikTok's figure as "short blocks of text"; the length of a hook's on-screen text is set in step 3 of "Choose the hook" in `SKILL.md`.
- YouTube Shorts: the "Stayed to watch" metric is "the percentage of times viewers stayed to watch past the initial seconds of a Short" ([YouTube Help](https://support.google.com/youtube/answer/12220281?hl=en)). No official threshold.
- LinkedIn: "Grab attention in the first 3 seconds", and "blurry visuals or poor audio will immediately lose credibility" ([LinkedIn marketing blog, 2025-04-08](https://www.linkedin.com/business/marketing/blog/linkedin-ads/your-one-stop-shop-for-linkedin-video-ad-tips), written for video ads). A figure of six seconds is attributed to LinkedIn's 2024 B2B benchmark, reported by [AFP Relaxnews, 2025-06-11](https://www.thestar.com.my/tech/tech-news/2025/06/11/to-make-your-mark-on-linkedin-focus-on-short-videos).
- The 3-second retention thresholds that circulate (50 %, 70 %, 80 %) have no platform source. Calibrate with the account's data.

## Why they work (psychology with evidence)

- **Information gap** ([Loewenstein 1994](https://stafforini.com/works/loewenstein-1994-psychology-curiosity-review/)): curiosity is a deprivation that arises from perceiving a gap in knowledge. Without prior knowledge there is no gap: that is why the question must be one the audience already has.
- **Inverted U** ([Kang et al. 2009](https://www.cmu.edu/dietrich/sds/docs/loewenstein/WickCandleLearning.pdf)): curiosity peaks when the person gives themselves about a 50 % chance of knowing the answer, activates reward circuits and improves recall of surprising answers. Implication: an initial dose of information (result first, data point) increases the hunger; there is no need to hide everything.
- **Importance, salience and surprise** ([Golman and Loewenstein 2016](https://www.cmu.edu/dietrich/sds/docs/golman/Information%20Gaps--Golman%20and%20Loewenstein.pdf)): attention to a question rises with how much the answer matters to the person, how salient the question is and how much the answer may contradict what they believed. Explains A1, A2, B4, C1, C4 and D2.
- **Negativity bias** ([Rozin and Royzman 2001](https://pdodds.w3.uvm.edu/files/papers/others/2001/rozin2001a.pdf); [Robertson et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10202797/)): in 22,743 randomized headline trials, each additional negative word in a headline of average length raised the click-through rate by 2.3 %. "Mistake", "stop", "don't" and "risk" work; the cost is reputational if overused or if the risk is not real.
- **Self-reference** (Rogers et al. 1977, on memory): information related to oneself is encoded and recalled better. In headlines, Lai and Farbrot (2014) found that self-referencing questions got more clicks than statements: 257 % in a test with classified ads and 175 % on Twitter, where the difference with other questions was not significant ([British Psychological Society summary](https://www.bps.org.uk/research-digest/are-you-more-likely-click-headlines-are-phrased-question)). Explains D1.
- **Questions**: more clicks (Lai and Farbrot) but more negative reactions and a lower expectation of the story (Scacco and Muddiman 2016, 2,057 adults, reported by [journalism.co.uk](https://www.journalism.co.uk/readers-perceive-question-based-headlines-more-negatively-study-shows/)). Specific yes, rhetorical no.
- **Zeigarnik does not support open loops**: the meta-analysis by [Ghibellini and Meier (2025)](https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-05000-w.html) finds no memory advantage for the unfinished, only a tendency to resume tasks. The loop works because it keeps a question active, and in a feed the "task" is abandoned with a swipe. That is why the gap must close soon.
- **Pattern interrupt**: the term comes from NLP (neuro-linguistic programming) and has no direct evidence. The closest study ([Lang et al. 2000](https://scholars.cityu.edu.hk/en/publications/the-effects-of-edits-on-arousal-attention-and-memory-for-televisi/)) found that a faster rate of edits raised arousal and memory for television messages. An abrupt change at the start triggers orientation, but it does not replace the question or the promise.

## Honesty and platforms

- Recommendation, common among practitioners: the hook sets an expectation and the video meets it. A hook that does not match the content erodes trust and sinks the second half of the video.
- YouTube removes "egregious clickbait" (titles or thumbnails that promise what the video does not deliver), starting in India and without a strike at first ([Google India blog, 2024-12-18](https://blog.google/intl/en-in/products/platforms/strengthening-enforcement-against-egregious-clickbait-on-youtube/)).
- Instagram: engagement bait is trying to maximize interactions to "hack" reach, for example "asking people to comment with a specific word, number, or emoji". Open questions and CTAs the creator really engages with are not (June 2024 clarification, reported by [Social Media Today](https://www.socialmediatoday.com/news/instagram-clarifies-advice-single-word-ctas-longer-reels/718151/)).
- TikTok (guidelines in force since 2026-09-24): "Content that tries to manipulate people into giving gifts or inflating likes or follows isn't eligible for the FYF", the For You feed ([Community Guidelines](https://www.tiktok.com/community-guidelines/en/integrity-authenticity)).
- Academic evidence: clickbait headlines lower perceived credibility ([Molyneux and Coddington 2020](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1080/17512786.2019.1628658?fields=title,year,abstract,venue); [Kaushal and Vemuri 2021](https://iiithf.github.io/rnd-showcase-2021/CogSci/07.%20Clickbait%20--%20Credibility%20of%20Digital%20News.pdf)). For a brand built on trust the cost accumulates piece after piece.
- Operating rule: every recommended hook carries the identified point in the script where it is paid off. If it does not exist, change the hook.

## Formula fatigue

- Creators and agencies name worn-out openings: "stop scrolling", "nobody's talking about this" and "I was today years old" ([Muthership podcast, 2026-07-10](https://share.transistor.fm/s/2173a763)); the ring-light testimonial and forced enthusiasm ([Pixis, 2026-03-25](https://pixis.ai/blog/ugc-in-2026-whats-working-whats-stale-and-how-to-refresh-your-hook-library/), a vendor blog). When many creators open the same way, the viewer recognizes it as selling.
- There is no independent study on the shelf life of a formula. Treat it as a signal: rotate templates, open with the strongest point of the video itself, write for the loyal audience.
- Do not ask for generic "hook lists": every creator gets the same ones. The hook comes from the concrete payoff of the piece.

## Evidence about one audience

This file keeps evidence that holds for any audience. What is known about one audience (how it reacts to urgency, to superlatives, to a credential) belongs to the workspace: write it in `brand-guide/audiences.md`, with its sources and dates, and this skill reads it there. For example, a workspace whose audience is professionals of one trade would note there which promises that trade distrusts and which kinds of proof it accepts.

## Sketch hooks

- Compressed structure, as taught by improv schools (UCB, Second City): base reality in 1 to 2 seconds, first unusual thing framed immediately, escalation, button. The text headline ("When...", "POV:") does the exposition in zero seconds.
- The "POV:" format has no known origin; one of its earliest known TikTok videos dates from February 2019 ([Know Your Meme](https://knowyourmeme.com/memes/pov-roleplays)). It works because it anticipates a reveal and puts the viewer in the scene. Descriptive evidence, not experimental.
- Evidence for one language and one country: in 914 TikTok videos by five comedy creators from Spain, the most successful humor was affiliative humor about everyday situations ([Molina-Fuster and Díaz-Lucena 2024](https://revistascientificas.us.es/index.php/Ambitos/article/download/24546/22552/121249)). Recognizable premise over format; check it against the account's data for other audiences.
- For an audience spread over several countries that share a language: adapt only very local references, keep the rest in the creator's own voice, as the voice guide describes it, and use universal premises with local detail as texture (recommendation).

## Origin of the formula library

The formulas of `hook-library.md` and the template names of `hook-templates.md` describe structures in common use among short-video creators. They are written in this skill's own words, with invented examples, and no claim is made about who originated any of them or how any of them performs. Hooks from creators the user wants to learn from are analyzed in the workspace's `editorial/hook-references.md`, with their links.

## Metrics to evaluate a hook

- Instagram: skip rate, "the percentage of views where viewers skip a Reel within the first 3 seconds" ([Meta for Developers, 2025-12-03](https://developers.facebook.com/blog/post/2025/12/03/instragram-api-updates/)), shown in the app's insights with the retention chart; it is reported not to cover trial reels ([Social Media Today, 2026-04-26](https://www.socialmediatoday.com/news/instagram-improves-insights-ui-adds-new-metrics/818504/)), where the retention curve is read instead. What creators call "hook rate" is its complement.
- Instagram, whole video: average watch time, likes per reach and sends per reach (Mosseri, January 2025, reported by [Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/)).
- Trial Reels are shown to non-followers first, and their metrics appear about 24 hours after sharing ([Meta, 2024-12-10](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers/)): they serve to compare two hooks.
- YouTube: "Stayed to watch", engaged views, average duration. Since 2025-03-31 a Shorts view counts every time the Short starts to play ([YouTube Help](https://support.google.com/youtube/answer/10059070)), so raw views do not measure retention.
- Look at rates, not totals (Mosseri, September 2026, as paraphrased by [Social Media Today](https://www.socialmediatoday.com/news/instagram-chief-shares-algorithm-insights-and-posting-tips/831326/)).
- Curve diagnosis (inference widespread among agencies, no study): if retention drops in the first 3 to 5 seconds, the problem is the hook; if it drops later, the problem is the content or the broken promise. First criterion to decide whether to rework the hook or the script.
