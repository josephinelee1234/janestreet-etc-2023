import SampleBot
import random
import math

class EtfStrategy:
    def __init__(self, exchange: "SampleBot.ExchangeConnection", hello_message):
        self.exchange = exchange
        self.gs_fair = 0
        self.ms_fair = 0
        self.wfc_fair = 0
        self.etf = 0
        self.things_added = 0
        self.count = 0
        self.position = 0
        
        assert(hello_message["type"] == "hello")
        for symbol in hello_message["symbols"]:
            if symbol["symbol"] == "XLF":
                self.position = symbol["position"]

        
    
    def handle_message(self, message):
        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        
        if message["type"] == "book" or message["type"] == "BOOK":
            if message["symbol"] == "GS":

                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                gs_bid_price = best_price("buy")
                gs_ask_price = best_price("sell")
                
                if gs_ask_price is not None and gs_bid_price is not None:
                    self.gs_fair = (gs_ask_price + gs_bid_price)/2
                    self.things_added += 1
            
            if message["symbol"] == "MS":

                def best_price(side):
                     if message[side]:
                         return message[side][0][0]


                ms_bid_price = best_price("buy")
                ms_ask_price = best_price("sell")
                
                if ms_ask_price is not None and ms_bid_price is not None:
                    self.ms_fair = (ms_ask_price + ms_bid_price)/2
                    self.things_added += 1
            
            if message["symbol"] == "WFC":
                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                

                wfc_bid_price = best_price("buy")
                wfc_ask_price = best_price("sell")
                if wfc_ask_price is not None and wfc_bid_price is not None:
                    self.wfc_fair = (wfc_ask_price + wfc_bid_price)/2
                    self.things_added += 1
            
            self.etf = (3000 + 2*self.gs_fair + 3*self.ms_fair + 2*self.wfc_fair)/10            
            
            if message["symbol"] == "XLF":
                if self.things_added >= 3:
                    def best_price_etf(side):
                        if message[side]:
                            return message[side][0][0]    
                    # def best_price_size(side):
                    #     if message[side]:
                    #         return math.ceil(message[side][0][1]/2)
                            
                    if self.position <= 97:
                        if best_price_etf("buy") is not None and best_price_etf("buy") < self.etf:
                            print("buying")
                            self.position += 3
                            self.count += 1
                            self.exchange.send_add_message(self.count , "XLF", SampleBot.Dir.BUY,  best_price_etf("buy"), 3)
                            print(self.position)

                    if self.position >= -97:
                        if best_price_etf("sell") is not None and best_price_etf("sell") > self.etf:
                            print("selling")
                            self.position -= 3
                            self.count += 1
                            self.exchange.send_add_message(self.count , "XLF", SampleBot.Dir.SELL, best_price_etf("sell"), 3)
                            print(self.position)
                
    
        
