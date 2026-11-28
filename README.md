[![make.fun · black-friday-deal-finder-01](https://make.fun/badge/black-friday-deal-finder-01.svg)](https://make.fun/bounty/black-friday-deal-finder-01?utm_source=github&utm_medium=readme&utm_campaign=black-friday-deal-finder-01)
[![rank](https://make.fun/badge/black-friday-deal-finder-01/jennifferweslowski-design/makefun-entries-2/rank.svg)](https://make.fun/bounty/black-friday-deal-finder-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=black-friday-deal-finder-01)
[![reward](https://make.fun/badge/black-friday-deal-finder-01/jennifferweslowski-design/makefun-entries-2/reward.svg)](https://make.fun/bounty/black-friday-deal-finder-01?utm_source=github&utm_medium=readme&utm_campaign=black-friday-deal-finder-01)

# Black Friday Deal Finder

A working deal finder for the make.fun bounty "Build the best real
Black Friday deal finder": a static site listing 12 Black Friday and
Cyber Monday deals, each with its product, its store, a link to the
store, its sale price, its usual price, its discount, and when its
price was checked, with search and filters by category, store and
discount that work.

Every price was read from a retailer release or a deals roundup that
names the store on 27 November 2026 and re-read on 28 November 2026.
Each deal carries an honest signal — New low, Strong price, Good
price or Modest discount — with the evidence for it. Nothing is a
placeholder: the site is plain static files under `app/`, it loads
nothing over the network, and it works on a desktop and on a phone.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

This copies `app/` and `screenshots/` into the output directory and
writes `dossier.json` there. To look at the site first, serve `app/`
with any static server, for example `python3 -m http.server` inside
`app/`, and open it in a browser.

This entry is on make.fun.
