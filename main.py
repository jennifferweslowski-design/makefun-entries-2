"""Pump.fun Bot Sprint: Make Bot And Win.

A replay bot for the agent-fun/replay/v2 protocol: the harness sends
hello, then batches of pump.fun events on stdin, and this bot answers
every batch with one reply carrying its orders on stdout.

Strategy: catch young coins in their first sharp climb and get out
fast. A mint is bought only while it is young, its price is climbing
on buy-heavy flow, and the book has room; every position carries a
take-profit, a stop-loss and a maximum hold, so no coin is ever left
to drift. Fees are about 1.25% a side, so a trade needs a real move
to pay -- the entry bar is set above the round-trip fee.
"""

import json
import sys
from collections import deque

LAMPORTS_PER_SOL = 1_000_000_000

# Entry: a mint younger than this many slots may be bought. Only the
# first minutes count: after that the early buyers are already leaving.
YOUNG_SLOTS = 1200
# Entry: price must have climbed at least this much over the lookback.
# A weak climb is usually noise; the bar sits above it.
CLIMB = 0.10
# How far back the climb is measured, in slots.
LOOKBACK_SLOTS = 240
# Entry: buys must clearly dominate the recent flow.
MIN_BUY_SHARE = 0.65
# Size: this fraction of starting capital per new position.
SIZE_FRACTION = 0.03
# Exits. Memecoin momentum mean-reverts fast and the round trip costs
# about 2.5% in fees, so the win target is set where a climb usually
# still has room, and the loss cut where a fade is already confirmed.
TAKE_PROFIT = 0.15
STOP_LOSS = 0.08
GIVE_BACK = 0.06
MAX_HOLD_SLOTS = 1200
SLIPPAGE_BPS = 100


class Coin:
    """What the bot remembers about one mint."""

    def __init__(self, first_slot):
        self.first_slot = first_slot
        self.prices = deque(maxlen=64)  # (slot, price in SOL per token)
        self.buys = 0
        self.sells = 0
        self.peak = 0.0
        self.bought_at = 0.0
        self.bought_slot = 0

    def note_price(self, slot, price):
        if price > 0:
            self.prices.append((slot, price))
            if price > self.peak:
                self.peak = price

    def price_now(self):
        return self.prices[-1][1] if self.prices else 0.0

    def price_then(self, slot):
        """Latest recorded price at or before the given slot."""
        found = 0.0
        for seen_slot, price in self.prices:
            if seen_slot <= slot:
                found = price
            else:
                break
        return found

    def buy_share(self):
        total = self.buys + self.sells
        if total == 0:
            return 0.0
        return self.buys / total


class Bot:
    def __init__(self):
        self.capital = 0
        self.max_positions = 10
        self.max_order_bps = 1000
        self.max_orders = 10
        self.latency = 0
        self.coins = {}
        self.held = {}  # mint -> token amount (from the harness account)
        self.pending = {}  # mint -> (order-time price, slot) while a buy is unfilled
        self.cash = 0
        self.order_no = 0
        self.slot = 0

    def next_id(self, kind):
        self.order_no += 1
        return "%s-%d" % (kind, self.order_no)

    def handle_hello(self, msg):
        self.capital = int(msg["capital"]["lamports"])
        caps = msg.get("caps", {})
        self.max_positions = int(caps.get("max_open_positions", 10))
        self.max_order_bps = int(caps.get("max_order_bps_of_real_reserve", 1000))
        self.max_orders = int(caps.get("max_orders_per_batch", 10))
        self.latency = int(msg.get("latency_slots", 0))
        self.cash = self.capital

    def handle_batch(self, msg):
        self.slot = int(msg["slot"])
        self.remember_account(msg.get("account", {}))
        self.remember_fills(msg.get("fills", []))
        for mark in msg.get("marks", []):
            self.remember_mark(mark)
        for event in msg.get("events", []):
            self.remember_event(event)
        orders = []
        orders += self.plan_exits()
        orders += self.plan_entries(msg)
        return {"type": "reply", "seq": msg["seq"], "orders": orders[: self.max_orders]}

    def remember_fills(self, fills):
        """Entry prices come from fills, not from the order: an order
        may fill late, partly, or not at all, and the exit maths must
        use the price actually paid."""
        for fill in fills or []:
            if fill.get("status") != "filled":
                continue
            mint = fill.get("mint")
            coin = self.coins.get(mint)
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
                paid = quote / amount / LAMPORTS_PER_SOL
                if paid > 0:
                    coin.bought_at = paid
                    coin.bought_slot = int(fill.get("decided_slot", self.slot))
                    coin.peak = paid
                self.pending.pop(mint, None)
            elif fill.get("side") == "sell":
                coin.bought_at = 0.0
                coin.bought_slot = 0
                coin.peak = 0.0

    def remember_account(self, account):
        try:
            self.cash = int(account.get("cash_lamports", self.cash))
        except (TypeError, ValueError):
            pass
        self.held = {}
        for pos in account.get("positions", []) or []:
            try:
                self.held[pos["mint"]] = int(pos["token_amount"])
            except (KeyError, TypeError, ValueError):
                continue

    def remember_mark(self, mark):
        mint = mark.get("mint")
        if not mint:
            return
        coin = self.coins.setdefault(mint, Coin(int(mark.get("slot", self.slot))))
        price = self.mark_price(mark)
        coin.note_price(int(mark.get("slot", self.slot)), price)

    @staticmethod
    def mark_price(mark):
        try:
            quote = int(mark["virtual_quote_reserves"])
            tokens = int(mark["virtual_token_reserves"])
        except (KeyError, TypeError, ValueError):
            return 0.0
        if tokens <= 0:
            return 0.0
        return quote / tokens / LAMPORTS_PER_SOL

    def remember_event(self, event):
        kind = event.get("event")
        mint = event.get("mint")
        if not mint:
            return
        slot = int(event.get("slot", self.slot))
        if kind == "CreateEvent":
            self.coins.setdefault(mint, Coin(slot))
            return
        coin = self.coins.setdefault(mint, Coin(slot))
        if kind == "TradeEvent":
            try:
                quote = int(event["virtual_sol_reserves"])
                tokens = int(event["virtual_token_reserves"])
            except (KeyError, TypeError, ValueError):
                return
            if tokens > 0:
                coin.note_price(slot, quote / tokens / LAMPORTS_PER_SOL)
            if event.get("is_buy"):
                coin.buys += 1
            else:
                coin.sells += 1

    def plan_exits(self):
        orders = []
        for mint, amount in list(self.held.items()):
            if amount <= 0:
                continue
            coin = self.coins.get(mint)
            if coin is None:
                continue
            if coin.bought_at <= 0 and mint in self.pending:
                # No fill arrived: fall back to the order-time price so
                # the position can still be exited instead of stranding.
                price0, slot0 = self.pending[mint]
                if self.slot - slot0 > 10:
                    coin.bought_at = price0
                    coin.bought_slot = slot0
                    coin.peak = price0
            price = coin.price_now()
            if price <= 0 or coin.bought_at <= 0:
                continue
            gain = price / coin.bought_at - 1.0
            held_long = self.slot - coin.bought_slot >= MAX_HOLD_SLOTS
            fell_back = coin.peak > 0 and price < coin.peak * (1.0 - GIVE_BACK)
            if gain >= TAKE_PROFIT or gain <= -STOP_LOSS or held_long or fell_back:
                orders.append(
                    {
                        "side": "sell",
                        "client_id": self.next_id("s"),
                        "mint": mint,
                        "token_amount": str(amount),
                        "max_slippage_bps": SLIPPAGE_BPS,
                    }
                )
        return orders

    def plan_entries(self, msg):
        orders = []
        if len(self.held) >= self.max_positions:
            return orders
        size = int(self.capital * SIZE_FRACTION)
        if size <= 0 or self.cash < size:
            return orders
        for mint, coin in self.coins.items():
            if len(orders) + len(self.held) >= self.max_positions:
                break
            if mint in self.held:
                continue
            if self.slot - coin.first_slot > YOUNG_SLOTS:
                continue
            if coin.buy_share() < MIN_BUY_SHARE:
                continue
            now = coin.price_now()
            then = coin.price_then(self.slot - LOOKBACK_SLOTS)
            if then <= 0 or now <= 0:
                continue
            if now / then - 1.0 < CLIMB:
                continue
            quote = self.capped_size(mint, size, msg)
            if quote <= 0:
                continue
            orders.append(
                {
                    "side": "buy",
                    "client_id": self.next_id("b"),
                    "mint": mint,
                    "quote_lamports": str(quote),
                    "max_slippage_bps": SLIPPAGE_BPS,
                }
            )
            self.pending[mint] = (now, self.slot)
        return orders

    def capped_size(self, mint, size, msg):
        """Keep the order inside the harness cap on real reserves."""
        real_quote = 0
        for mark in msg.get("marks", []):
            if mark.get("mint") == mint:
                try:
                    real_quote = int(mark.get("real_quote_reserves", 0))
                except (TypeError, ValueError):
                    real_quote = 0
                break
        if real_quote > 0:
            cap = real_quote * self.max_order_bps // 10000
            size = min(size, cap)
        return size

    def run(self):
        bot = self
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            kind = msg.get("type")
            if kind == "hello":
                bot.handle_hello(msg)
            elif kind == "batch":
                try:
                    reply = bot.handle_batch(msg)
                except Exception:
                    reply = {"type": "reply", "seq": msg.get("seq", 0), "orders": []}
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()
            elif kind == "done":
                break


if __name__ == "__main__":
    Bot().run()
