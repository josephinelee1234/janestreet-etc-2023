import SampleBot
import TickerTracker
import time

class AdrStrategy:
    def __init__(self, exchange: "SampleBot.ExchangeConnection", hello_message):
        self.exchange = exchange
        self.edge = 3
        self.limit = 10

        self.order_info = {}
        self.pending_orders = []
        self.order_id = 200000000

        self.tickers = {
            "VALBZ": TickerTracker.TickerTracker("VALBZ"),
            "VALE": TickerTracker.TickerTracker("VALE")
        }
        self.cur_quantity = {
            "VALBZ": 0,
            "VALE": 0
        }
        self.outstanding_buy = {
            "VALBZ": 0,
            "VALE": 0
        }
        self.outstanding_sell = {
            "VALBZ": 0,
            "VALE": 0
        }

        assert(hello_message["type"] == "hello")
        for symbol in hello_message["symbols"]:
            if symbol["symbol"] == "VALBZ":
                self.cur_quantity["VALBZ"] = symbol["position"]
            elif symbol["symbol"] == "VALE":
                self.cur_quantity["VALE"] = symbol["position"]

        self.dead = False
        self.is_converting = False
    
    def handle_message(self, message):
        if self.dead:
            return
        self.tickers["VALBZ"].handle_message(message)
        self.tickers["VALE"].handle_message(message)

        if message["type"] == "reject" and message["order_id"] in self.order_info:
            print("ADR Strategy ERROR: Order was rejected")
            print(message)
            print(self.cur_quantity)
            # self.dead = True
            self.process_order(self.order_info[message["order_id"]], self.order_info[message["order_id"]]["quantity"], success=False)
            return
    
        if message["type"] == "fill" and message["order_id"] in self.order_info:
            print("ADR Strategy: Our order {} filled!".format(message["order_id"]))
            self.process_order(self.order_info[message["order_id"]], message["size"],success=True)
        
        if message["type"] == "ack" and message["order_id"] in self.order_info:
            self.process_ack(self.order_info[message["order_id"]])
            return
        
        if message["type"] == "out" and message["order_id"] in self.order_info:
            self.process_out(self.order_info[message["order_id"]])
            return

        if not self.tickers["VALBZ"].ready() or not self.tickers["VALE"].ready():
            return
        
        self.convert_if_needed()
        self.estimated_price = self.tickers["VALBZ"].get_estimated_price()
        if self.estimated_price == -1:
            return
        
        nxt = []
        for order in self.pending_orders:
            if order["time"] < time.time() - 1:
                self.exchange.send_cancel_message(order["id"])
            else:
                nxt.append(order)
        self.pending_orders = nxt

        valbz_bid, valbz_ask = self.tickers["VALBZ"].get_best_bid_ask()
        vale_bid, vale_ask = self.tickers["VALE"].get_best_bid_ask()

        valbz = (self.cur_quantity["VALBZ"] + self.outstanding_buy["VALBZ"] - self.outstanding_sell["VALBZ"])
        vale = (self.cur_quantity["VALE"] + self.outstanding_buy["VALE"] - self.outstanding_sell["VALE"])

        # Check if we should buy one VALBZ and sell one VALE
        if -self.estimated_price + vale_bid[0] >= self.edge:
            # Do it!
            self.execute("VALBZ", "VALE", min(valbz_ask[1], vale_bid[1]))
        
        # Check if we should buy one VALE and sell one VALBZ
        elif -vale_ask[0] + self.estimated_price >= self.edge:
            # Do it!
            self.execute("VALE", "VALBZ", min(vale_ask[1], valbz_bid[1]))
        
        # Check if we should do stuff with VALBZ to equalize VALE
        else:
            more_needed = - vale - valbz
            if more_needed > 0:
                self.buy("VALBZ", min(more_needed, valbz_ask[1]))
            elif more_needed < 0:
                self.sell("VALBZ", min(-more_needed, valbz_bid[1]))
        
    
    def process_order(self, order_info, quantity, success):
        if order_info["type"] == "BUY":
            self.outstanding_buy[order_info["ticker"]] -= quantity
            order_info["quantity"] -= quantity
            if success:
                self.cur_quantity[order_info["ticker"]] += quantity
        elif order_info["type"] == "SELL":
            self.outstanding_sell[order_info["ticker"]] -= quantity
            order_info["quantity"] -= quantity
            if success:
                self.cur_quantity[order_info["ticker"]] -= quantity
    
    def process_ack(self, order_info):
        if order_info["type"] == "CONVERT":
            self.is_converting = False
            self.cur_quantity[order_info["ticker"]] -= order_info["quantity"]
            self.cur_quantity["VALE" if order_info["ticker"] == "VALBZ" else "VALBZ"] += order_info["quantity"]
            print("Converted; we now have {} VALBZ and {} VALE".format(self.cur_quantity["VALBZ"], self.cur_quantity["VALE"]))
    
    def process_out(self, order_info):
        self.process_order(order_info, order_info["quantity"], success=False)
    
    def has_outstanding_orders(self):
        return self.outstanding_buy["VALBZ"] > 0 or self.outstanding_buy["VALE"] > 0 or self.outstanding_sell["VALBZ"] > 0 or self.outstanding_sell["VALE"] > 0
    
    def convert_if_needed(self):
        if self.is_converting:
            return
        mx = min(abs(self.cur_quantity["VALBZ"]), abs(self.cur_quantity["VALE"]))
        if mx > 7:
            self.is_converting = True
            dir = "BUY" if self.cur_quantity["VALBZ"] > 0 else "SELL"
            print("Attempting to convert {} to {}".format(dir, self.cur_quantity["VALBZ"]))
            self.exchange.send_convert_message(
                self.order_id,
                "VALE",
                dir,
                mx
            )
            self.order_info[self.order_id] = {
                "type": "CONVERT",
                "ticker": "VALBZ" if dir == "BUY" else "VALE",
                "quantity": mx
            }
            self.order_id += 1

    def execute(self, to_buy: str, to_sell: str, quantity: int) -> None:
        quantity = min(quantity, self.limit - (self.cur_quantity[to_buy] + self.outstanding_buy[to_buy] - self.outstanding_sell[to_buy]))
        quantity = min(quantity, self.limit + (self.cur_quantity[to_sell] + self.outstanding_buy[to_sell] - self.outstanding_sell[to_sell]))
        if quantity == 0:
            return
        # print("Executing buy {} sell {} for {}".format(to_buy, to_sell, quantity))
        if to_buy == "VALE": self.buy(to_buy, quantity)
        if to_sell == "VALE": self.sell(to_sell, quantity)
    
    def buy(self, ticker, quantity):
        price = self.tickers[ticker].get_price_to_buy(quantity)

        self.exchange.send_add_message(order_id=self.order_id, symbol=ticker, dir=SampleBot.Dir.BUY, price=price, size=quantity)
        self.outstanding_buy[ticker] += quantity
        self.order_info[self.order_id] = {
            "type": "BUY",
            "ticker": ticker,
            "quantity": quantity
        }
        self.order_id += 1
        self.pending_orders.append({
            "time": time.time(),
            "id": self.order_id - 1
        })
    
    def sell(self, ticker, quantity):
        price = self.tickers[ticker].get_price_to_sell(quantity)

        self.exchange.send_add_message(order_id=self.order_id, symbol=ticker, dir=SampleBot.Dir.SELL, price=price, size=quantity)
        self.outstanding_sell[ticker] += quantity
        self.order_info[self.order_id] = {
            "type": "SELL",
            "ticker": ticker,
            "quantity": quantity
        }
        self.order_id += 1
        self.pending_orders.append({
            "time": time.time(),
            "id": self.order_id - 1
        })