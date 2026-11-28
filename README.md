[![make.fun · u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532](https://make.fun/badge/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532.svg)](https://make.fun/bounty/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532?utm_source=github&utm_medium=readme&utm_campaign=u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532)
[![rank](https://make.fun/badge/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532/jennifferweslowski-design/makefun-entries/rank.svg)](https://make.fun/bounty/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532)
[![reward](https://make.fun/badge/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532/jennifferweslowski-design/makefun-entries/reward.svg)](https://make.fun/bounty/u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532?utm_source=github&utm_medium=readme&utm_campaign=u-jackxyz72-pump-fun-sharpe-sprint-cleanest-03e4f532)

# Pump.fun Sharpe Sprint — Cleanest Paper Bot Wins

A paper trading bot for the make.fun bounty "Pump.fun Sharpe
Sprint — Cleanest Paper Bot Wins", speaking the agent-fun/replay/v2
protocol: the harness sends `hello`, then batches of pump.fun
events on stdin, and the bot answers every batch with one reply
carrying its orders.

This competition is ranked by hourly Sharpe ratio, not by raw
profit, so the bot is built for smooth returns: small positions,
breakout entries only, and exits that cut a loser early and bank a
winner before it can give the gain back. A volatile coin that
spikes and crashes is worse here than a quiet one that climbs a
little, so the bot would rather sit in cash than chase a spike.

## Run

```sh
python3 main.py
```

Reads newline-delimited JSON on stdin, writes one reply per batch on
stdout. Standard library only, no network, no files.

This entry is on make.fun.
