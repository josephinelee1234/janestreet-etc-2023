from SampleBot import ExchangeConnection

class BondStrategy:
    def __init__(self, exchange: ExchangeConnection):
        self.exchange = exchange
    
    def handle_message(self, message):
        print("Bond Strategy: {}".format(message))