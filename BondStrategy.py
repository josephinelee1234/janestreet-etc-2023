import SampleBot
import random

class BondStrategy:
    def __init__(self, exchange: "SampleBot.ExchangeConnection", hello_message):
        self.exchange = exchange
        self.edge = 1
        self.fair_value = 1000
        self.limit = 100

        self.cur_quantity = 0
        self.outstanding_buy = 0
        self.outstanding_sell = 0
        self.order_id = 100000000

        self.order_info = {}

        assert(hello_message["type"] == "hello")
        for symbol in hello_message["symbols"]:
            if symbol["symbol"] == "BOND":
                self.cur_quantity = symbol["position"]

        self.update_orders()
    
    def handle_message(self, message):
        if message["type"] == "reject":
            order_id = message["order_id"]
            if message["error"] == "LIMIT:OPEN_ORDERS" and order_id in self.order_info:
                if self.order_info[order_id]["type"] == "BUY":
                    self.outstanding_buy -= self.order_info[order_id]["quantity"]
                else:
                    self.outstanding_sell -= self.order_info[order_id]["quantity"]
                self.update_orders()

        if message["type"] == "fill":
            if message["symbol"] != "BOND":
                return
            if message["dir"] == "BUY":
                self.cur_quantity += message["size"]
                self.outstanding_buy -= message["size"]
                print("We bought {} shares of BOND for {} and have {} shares now".format(message["size"], message["price"], self.cur_quantity))
                self.update_orders()
            elif message["dir"] == "SELL":
                self.cur_quantity -= message["size"]
                self.outstanding_sell -= message["size"]
                print("We sold {} shares of BOND for {} and have {} shares now".format(message["size"], message["price"], self.cur_quantity))
                self.update_orders()
    
    def update_orders(self):
        to_buy = self.limit-self.cur_quantity-self.outstanding_buy
        to_sell = self.limit+self.cur_quantity-self.outstanding_sell
        if to_buy > 0:
            print("Buying an additional {} shares of BOND".format(to_buy))
            self.buy(to_buy)
        if to_sell > 0:
            print("Selling an additional {} shares of BOND".format(to_sell))
            self.sell(to_sell)
    
    def buy(self, quantity):
        self.exchange.send_add_message(order_id=self.order_id, symbol="BOND", dir=SampleBot.Dir.BUY, price=self.fair_value - self.edge, size=quantity)
        self.outstanding_buy += quantity
        self.order_info["" + self.order_id] = {
            "type": "BUY",
            "amount": quantity
        }
        self.order_id += 1
    
    def sell(self, quantity):
        self.exchange.send_add_message(order_id=self.order_id, symbol="BOND", dir=SampleBot.Dir.SELL, price=self.fair_value + self.edge, size=quantity)
        self.outstanding_sell += quantity
        self.order_info["" + self.order_id] = {
            "type": "SELL",
            "amount": quantity
        }
        self.order_id += 1