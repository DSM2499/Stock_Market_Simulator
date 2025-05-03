import numpy as np
from collections import defaultdict

class Exchange:
    def __init__(self, stock_config, transaction_cost_rate = 0.005):
        self.order_books = {
            s['symbol']: {'buy': [], 'sell': []} for s in stock_config
        }
        self.prices = {
            s['symbol']: s['initial_price'] for s in stock_config
        }
        self.floats = {
            s['symbol']: s['float'] for s in stock_config
        }
        self.daily_ohlc = {
            s['symbol']: [] for s in stock_config
        }
        self.trades = []
        self.transaction_cost_rate = transaction_cost_rate
        self.trade_log = []

    def submit_order(self, stock, order):
        self.order_books[stock][order['type']].append(order)

    def match_all(self, agents):
        for stock, books in self.order_books.items():
            buys = sorted(books['buy'], key = lambda o: -o['quantity'])
            sells = sorted(books['sell'], key = lambda o: o['quantity'])

            matched = min(len(buys), len(sells))
            price = self.prices[stock]
            trades_this_stock = []

            for i in range(matched):
                buyer = agents[buys[i]['agent_id']]
                seller = agents[sells[i]['agent_id']]
                qty = min(buys[i]['quantity'], sells[i]['quantity'])

                cost = qty * price
                fee = cost * self.transaction_cost_rate

                if buyer.cash >= qty * price and seller.portfolio[stock] >= qty:
                    buyer.cash -= (cost + fee)
                    seller.cash += (cost - fee)
                    
                    buyer.portfolio[stock] += qty
                    seller.portfolio[stock] -= qty

                    trades_this_stock.append({
                        'stock': stock,
                        'price': price,
                        'quantity': qty,
                        'buyer_id': buyer.agent_id,
                        'seller_id': seller.agent_id,
                        'fee_paid': round(2 * fee, 4)
                    })

                    self.log_trade({
                        'stock': stock,
                        'price': price,
                        'quantity': qty,
                        'buyer_id': buyer.agent_id,
                        'seller_id': seller.agent_id,
                        'fee_paid': round(2 * fee, 4)
                    })
            
            self.trades.extend(trades_this_stock)

            #Update prices
            if trades_this_stock:
                self.prices[stock] += np.random.normal(0, 0.1)
            else:
                self.prices[stock] += np.random.normal(0, 0.01)
            self.order_books[stock] = {'buy': [], 'sell': []}
    
    def get_price(self, stock):
        return self.prices.get(stock, None)
    
    def get_observation(self):
        return {
            'prices': self.prices.copy(),
            'price_history': {s: [] for s in self.prices}
        }
    
    def get_price_history_dict(self):
        return {
            stock: [ohlc['close'] for ohlc in self.daily_ohlc[stock]]
            for stock in self.daily_ohlc
        }
    
    def reset_day(self):
        self.trades = []
        return
    
    
    def log_day_close(self, day_idx):
        """
        Generate OHLC and volume for each stock based on trades during the day.
        """
        # First, collect trades per stock

        trade_data = defaultdict(list)
        for trade in self.trades:
            stock = trade['stock']
            price = trade['price']
            qty = trade['quantity']
            trade_data[stock].append((price, qty))

        for stock in self.prices:
            trades = trade_data.get(stock, [])
            if not trades:
                # No trades today; use current price as flat OHLC
                price = self.prices[stock]
                ohlc = {
                    "day": day_idx,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 0
                    }
            else:
                prices = [t[0] for t in trades]
                volumes = [t[1] for t in trades]
                ohlc = {
                    "day": day_idx,
                    "open": prices[0],
                    "high": max(prices),
                    "low": min(prices),
                    "close": prices[-1],
                    "volume": sum(volumes)
                }

            self.daily_ohlc[stock].append(ohlc)
    
    def log_trade(self, trade):
        self.trade_log.append(trade)
    
    def save_trade_log(self, path = 'trade_log.csv'):
        import pandas as pd
        if self.trade_log:
            df = pd.DataFrame(self.trade_log)
            df.to_csv(path, index=False)