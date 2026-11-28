"""Pump.fun Sharpe Sprint -- Cleanest Paper Bot Wins.

A replay bot for the agent-fun/replay/v2 protocol. The harness sends
hello and then batches of pump.fun events on stdin; the bot answers
every batch with one reply carrying its orders on stdout.

This competition is ranked by hourly Sharpe ratio, not by raw profit,
so the bot is built for smooth returns: small positions, breakout
entries only, and exits that cut a loser early and bank a winner
before it can give the gain back. A volatile coin that spikes and
crashes is worse here than a quiet one that climbs a little, so the
bot would rather sit in cash than chase a spike.
"""

import json
import sys

LAMPORTS = 1_000_000_000

ENTRY_FRACTION = 0.015
MAX_AGE_SLOTS = 1800
BREAKOUT_GAIN = 0.08
LOOKBACK = 120
BUY_SHARE_MIN = 0.60
PROFIT_TAKE = 0.10
LOSS_CUT = 0.04
TRAIL_BACK = 0.04
HOLD_LIMIT = 600
SLIPPAGE = 100

state = {
    "capital": 0,
    "cash": 0,
    "max_positions": 10,
    "max_order_bps": 1000,
    "max_orders": 10,
    "slot": 0,
    "counter": 0,
    "coins": {},
    "held": {},
    "awaiting": {},
}


def coin_for(mint, slot):
    coins = state["coins"]
    coin = coins.get(mint)
    if coin is None:
        coin = {
            "born": slot,
            "history": [],
            "buys": 0,
            "sells": 0,
            "entry": 0.0,
            "entry_slot": 0,
            "top": 0.0,
        }
        coins[mint] = coin
    return coin


def record_price(coin, slot, price):
    if price <= 0:
        return
    history = coin["history"]
    history.append((slot, price))
    if len(history) > 96:
        del history[: len(history) - 96]
    if price > coin["top"]:
        coin["top"] = price


def price_at(coin, slot):
    found = 0.0
    for seen, price in coin["history"]:
        if seen <= slot:
            found = price
        else:
            break
    return found


def latest_price(coin):
    history = coin["history"]
    return history[-1][1] if history else 0.0


def reserve_price(mark):
    try:
        quote = int(mark["virtual_quote_reserves"])
        tokens = int(mark["virtual_token_reserves"])
    except (KeyError, TypeError, ValueError):
        return 0.0
    if tokens <= 0:
        return 0.0
    return quote / tokens / LAMPORTS


def absorb_hello(message):
    state["capital"] = int(message["capital"]["lamports"])
    state["cash"] = state["capital"]
    caps = message.get("caps", {})
    state["max_positions"] = int(caps.get("max_open_positions", 10))
    state["max_order_bps"] = int(caps.get("max_order_bps_of_real_reserve", 1000))
    state["max_orders"] = int(caps.get("max_orders_per_batch", 10))


def absorb_account(account):
    try:
        state["cash"] = int(account.get("cash_lamports", state["cash"]))
    except (TypeError, ValueError):
        pass
    held = {}
    for position in account.get("positions", []) or []:
        try:
            held[position["mint"]] = int(position["token_amount"])
        except (KeyError, TypeError, ValueError):
            continue
    state["held"] = held


def absorb_fills(fills):
    for fill in fills or []:
        if fill.get("status") != "filled":
            continue
        mint = fill.get("mint")
        coin = state["coins"].get(mint)
        if coin is None:
            continue
        try:
            quote = int(fill["quote_lamports"])
            amount = int(fill["token_amount"])
        except (KeyError, TypeError, ValueError):
            continue
        if amount <= 0:
            continue
        if fill.get("side") == "buy":
            paid = quote / amount / LAMPORTS
            if paid > 0:
                coin["entry"] = paid
                coin["entry_slot"] = int(fill.get("decided_slot", state["slot"]))
                coin["top"] = paid
            state["awaiting"].pop(mint, None)
        else:
            coin["entry"] = 0.0
            coin["entry_slot"] = 0
            coin["top"] = 0.0


def absorb_marks(marks):
    for mark in marks or []:
        mint = mark.get("mint")
        if not mint:
            continue
        slot = int(mark.get("slot", state["slot"]))
        record_price(coin_for(mint, slot), slot, reserve_price(mark))


def absorb_events(events):
    for event in events or []:
        mint = event.get("mint")
        if not mint:
            continue
        slot = int(event.get("slot", state["slot"]))
        kind = event.get("event")
        coin = coin_for(mint, slot)
        if kind == "TradeEvent":
            try:
                quote = int(event["virtual_sol_reserves"])
                tokens = int(event["virtual_token_reserves"])
            except (KeyError, TypeError, ValueError):
                continue
            if tokens > 0:
                record_price(coin, slot, quote / tokens / LAMPORTS)
            if event.get("is_buy"):
                coin["buys"] += 1
            else:
                coin["sells"] += 1


def fresh_id(prefix):
    state["counter"] += 1
    return "%s%d" % (prefix, state["counter"])


def choose_exits():
    orders = []
    slot = state["slot"]
    for mint, amount in list(state["held"].items()):
        if amount <= 0:
            continue
        coin = state["coins"].get(mint)
        if coin is None:
            continue
        if coin["entry"] <= 0 and mint in state["awaiting"]:
            price0, slot0 = state["awaiting"][mint]
            if slot - slot0 > 10:
                coin["entry"] = price0
                coin["entry_slot"] = slot0
                coin["top"] = price0
        price = latest_price(coin)
        if price <= 0 or coin["entry"] <= 0:
            continue
        change = price / coin["entry"] - 1.0
        faded = coin["top"] > 0 and price < coin["top"] * (1.0 - TRAIL_BACK)
        stale = slot - coin["entry_slot"] >= HOLD_LIMIT
        if change >= PROFIT_TAKE or change <= -LOSS_CUT or faded or stale:
            orders.append(
                {
                    "side": "sell",
                    "client_id": fresh_id("x"),
                    "mint": mint,
                    "token_amount": str(amount),
                    "max_slippage_bps": SLIPPAGE,
                }
            )
    return orders


def choose_entries(marks):
    orders = []
    slot = state["slot"]
    if len(state["held"]) >= state["max_positions"]:
        return orders
    size = int(state["capital"] * ENTRY_FRACTION)
    if size <= 0 or state["cash"] < size:
        return orders
    real_reserve = {}
    for mark in marks or []:
        try:
            real_reserve[mark.get("mint")] = int(mark.get("real_quote_reserves", 0))
        except (TypeError, ValueError):
            continue
    for mint, coin in state["coins"].items():
        if len(orders) + len(state["held"]) >= state["max_positions"]:
            break
        if mint in state["held"]:
            continue
        if slot - coin["born"] > MAX_AGE_SLOTS:
            continue
        total = coin["buys"] + coin["sells"]
        if total < 5:
            continue
        if coin["buys"] / total < BUY_SHARE_MIN:
            continue
        if len(coin["history"]) < 5:
            continue
        now = latest_price(coin)
        before = price_at(coin, slot - LOOKBACK)
        if before <= 0 or now <= 0:
            continue
        if now / before - 1.0 < BREAKOUT_GAIN:
            continue
        recent_top = 0.0
        for seen, price in coin["history"]:
            if seen >= slot - 60 and price > recent_top:
                recent_top = price
        if now < recent_top:
            continue
        quote = size
        reserve = real_reserve.get(mint, 0)
        if reserve > 0:
            quote = min(quote, reserve * state["max_order_bps"] // 10000)
        if quote <= 0:
            continue
        orders.append(
            {
                "side": "buy",
                "client_id": fresh_id("e"),
                "mint": mint,
                "quote_lamports": str(quote),
                "max_slippage_bps": SLIPPAGE,
            }
        )
        state["awaiting"][mint] = (now, slot)
    return orders


def handle_batch(message):
    state["slot"] = int(message["slot"])
    absorb_account(message.get("account", {}))
    absorb_fills(message.get("fills", []))
    absorb_marks(message.get("marks", []))
    absorb_events(message.get("events", []))
    orders = choose_exits() + choose_entries(message.get("marks", []))
    return {"type": "reply", "seq": message["seq"], "orders": orders[: state["max_orders"]]}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        kind = message.get("type")
        if kind == "hello":
            absorb_hello(message)
        elif kind == "batch":
            try:
                reply = handle_batch(message)
            except Exception:
                reply = {"type": "reply", "seq": message.get("seq", 0), "orders": []}
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()
        elif kind == "done":
            break


if __name__ == "__main__":
    main()
