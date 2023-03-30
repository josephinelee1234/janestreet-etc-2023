import SampleBot
import random

class EtfStrategy:
    def __init__(self, exchange: "SampleBot.ExchangeConnection", hello_message):
        self.exchange = exchange
        self.gs_fair = 0
        self.ms_fair = 0
        self.wfc_fair = 0
        self.etf = 0
        self.things_added = 0
        
    
    def handle_message(self, message):
        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "book" or message["type"] == "BOOK":
            count = 0
            if message["symbol"] == "GS":
                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.gs_fair

                gs_bid_price = best_price("buy")
                gs_ask_price = best_price("sell")
                self.gs_fair = (gs_ask_price + gs_bid_price)/2
                self.etf += self.gs_fair
                self.things_added += 1
            
            if message["symbol"] == "MS":
                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.ms_fair

                ms_bid_price = best_price("buy")
                ms_ask_price = best_price("sell")
                self.ms_fair = (ms_ask_price + ms_bid_price)/2
                self.etf += self.ms_fair
                self.things_added += 1
            
            if message["symbol"] == "WFC":
                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.gs_fair

                wfc_bid_price = best_price("buy")
                wfc_ask_price = best_price("sell")
                self.wfc_fair = (gs_ask_price + gs_bid_price)/2
                self.etf += self.wfc_fair
                self.things_added += 1

            if self.things_added >= 3:
                self.etf = (3000 + 2*self.gs_fair + 3*self.ms_fair + 3*self.wfc_fair)/10
                
                while message["symbol"] != "XLF":
                    continue
                
                def best_price_etf(side):
                        if message[side]:
                            return message[side][0][0]
                
                if self.etf > best_price_etf("sell"):
                    self.exchange.send_add_message(count, "XLF", SampleBot.Dir.SELL, best_price_etf("sell"), 1)
                    count += 1
                elif self.etf < best_price_etf("buy"):
                    self.exchange.send_add_message(count, "XLF", SampleBot.Dir.BUY, best_price_etf("buy"), 1)
                    count += 1
    
        