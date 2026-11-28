[![make.fun · u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed](https://make.fun/badge/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed.svg)](https://make.fun/bounty/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed?utm_source=github&utm_medium=readme&utm_campaign=u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed)
[![rank](https://make.fun/badge/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed/jennifferweslowski-design/makefun-entries/rank.svg)](https://make.fun/bounty/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed)
[![reward](https://make.fun/badge/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed/jennifferweslowski-design/makefun-entries/reward.svg)](https://make.fun/bounty/u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed?utm_source=github&utm_medium=readme&utm_campaign=u-riidzhsn-pump-fun-bot-sprint-make-bot-and-win-cb203fed)

# Pump.fun Bot Sprint: Make Bot And Win

A paper trading bot for the make.fun bounty "Pump.fun Bot Sprint:
Make Bot And Win", speaking the agent-fun/replay/v2 protocol: the
harness sends `hello`, then batches of pump.fun events on stdin, and
the bot answers every batch with one reply carrying its orders.

Strategy: catch young coins in their first sharp climb and get out
fast. A mint is bought only while it is young, its price is climbing
on buy-heavy flow, and the book has room; every position carries a
take-profit, a stop-loss, a give-back exit and a maximum hold, so no
coin is ever left to drift. Fees run about 1.25% a side, so the entry
bar sits above the round-trip fee — a trade needs a real move to pay.

## Run

```sh
python3 main.py
```

Reads newline-delimited JSON on stdin, writes one reply per batch on
stdout. Standard library only, no network, no files.

This entry is on make.fun.
