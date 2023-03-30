class TickerTracker:
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.last_book = None

    def ready(self) -> bool:
        if self.last_book == None:
            return False
        if len(self.last_book["buy"]) == 0 or len(self.last_book["sell"]) == 0:
            # print("WOW, this ticker {} has no bid ({}) / ask ({}) orders! unexpected.".format(self.ticker, len(self.last_book["buy"]), len(self.last_book["sell"])))
            return False
        return True
    
    def handle_message(self, message):
        if message["type"] == "book":
            if message["symbol"] == self.ticker:
                self.last_book = message
    
    def get_best_bid_ask(self):
        assert(self.ready())
        return (self.last_book["buy"][0], self.last_book["sell"][0])
    
    def get_price_to_buy(self, quantity: int):
        assert(self.ready())
        assert(self.last_book["sell"][0][1] >= quantity)
        return self.last_book["sell"][0][0]
    
    def get_price_to_sell(self, quantity: int):
        assert(self.ready())
        assert(self.last_book["buy"][0][1] >= quantity)
        return self.last_book["buy"][0][0]