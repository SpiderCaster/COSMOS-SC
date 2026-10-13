# Questions

Does the offline draft really cost nothing?
Yes. No model runs. The words are sorted into sections by fixed rules, and the page is assembled from code. The ledger records the run at zero tokens.

What does the AI pass cost?
One planning call, with one retry if the answer comes back broken. On the free tier the cost is zero dollars. The ledger writes down the exact count either way.

Can the AI make things up?
No. It works only from the words in your files. It can reorder and shorten, but it cannot add facts, prices, or names.

What if I do not have a domain or webhost yet?
You can preview locally on port 4173. You can also deploy to free cloud staging with a single click, or download the self-contained static files to host anywhere for free.

How does the free agent work without an account?
SpiderCaster automatically provisions a free background model chain so you can chat and plan immediately. No API keys, credit cards, or accounts are needed.

How do I change one thing?
Edit the site.json file and rebuild from it with build --from. The rebuild costs nothing. Small fixes beat full rebuilds.

How does a site go live?
A person runs the bind command for the site and the mold. There is no publish button. A mold that is already live somewhere else is refused.

What do I need on my machine?
Python 3.11 or newer. That is all. The offline path needs no keys and no accounts.
