# Questions about the engine

Does the offline build really cost zero tokens?
Yes. The offline planner maps your copy files into sections with deterministic rules, and the renderer assembles the HTML from code. No model is called.

What does an AI build cost?
One planning call, plus at most one repair retry if the reply is not valid JSON. On the Gemini free tier the estimated cost is zero dollars; the ledger in report.json records the exact token counts.

Can the AI invent content?
No. The planning prompt restricts the model to facts and wording present in your source copy. It may reorganize and tighten, but it may not invent facts, prices, names or claims.

How do I change something without tokens?
Edit sites/NAME/site.json by hand and rebuild with forge build --from. The renderer is deterministic, so the rebuild is free.

How does this fit the fleet checks?
The built-in forge check mirrors the fleet content markers, the hotlink blocklist and the noindex rail, so a site that passes forge check is aligned with website_checker content rules before any deploy conversation starts.
