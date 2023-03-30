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
        self.count = 0
        
    
    def handle_message(self, message):
        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "book" or message["type"] == "BOOK":
            print("A")
            if message["symbol"] == "GS":
                print("B")

                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.gs_fair

                
                gs_bid_price = best_price("buy")
                gs_ask_price = best_price("sell")
                
                if gs_ask_price is not None and gs_bid_price is not None:
                    self.gs_fair = (gs_ask_price + gs_bid_price)/2
                    self.etf += self.gs_fair
                    self.things_added += 1
                
                print("gs")
                print(self.etf)
            
            if message["symbol"] == "MS":

                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.ms_fair

                ms_bid_price = best_price("buy")
                ms_ask_price = best_price("sell")
                
                if ms_ask_price is not None and ms_bid_price is not None:
                    self.ms_fair = (ms_ask_price + ms_bid_price)/2
                    self.etf += self.ms_fair
                    self.things_added += 1
                
                print("ms")
                print(self.etf)
            
            if message["symbol"] == "WFC":
                def best_price(side):
                     if message[side]:
                         return message[side][0][0]
                
                if self.things_added >= 3:
                    self.etf -= self.gs_fair

                wfc_bid_price = best_price("buy")
                wfc_ask_price = best_price("sell")
                if wfc_ask_price is not None and wfc_bid_price is not None:
                    self.wfc_fair = (wfc_ask_price + wfc_bid_price)/2
                    self.etf += self.wfc_fair
                    self.things_added += 1
                
                print("ms")
                print(self.etf)

            if self.things_added >= 3:
                print("C")

                self.etf = (3000 + 2*self.gs_fair + 3*self.ms_fair + 3*self.wfc_fair)/10
                
                # while message["symbol"] != "XLF":
                #     continue
                
                def best_price_etf(side):
                        if message[side]:
                            return message[side][0][0]
                if best_price_etf("sell") is not None:
                    if self.etf > best_price_etf("sell"):
                        print("self.etf")
                        print(best_price_etf("sell"))
                        self.count += 1
                        self.exchange.send_add_message(self.count , "XLF", SampleBot.Dir.SELL, self.etf, 1)
                elif best_price_etf("buy") is not None:
                    if self.etf < best_price_etf("buy"):
                        print(best_price_etf("buy"))
                        print("self.etf")
                        self.count += 1
                        self.exchange.send_add_message(self.count , "XLF", SampleBot.Dir.BUY,  self.etf, 1)
                        
                
    
        
