# Orchestrates the daily and minute-level simulation loop

import numpy as np
from collections import defaultdict
import pandas as pd
import requests

class Simulation:
    def __init__(self, agent, exchange,
                 news_generator,
                 num_days = 100,
                 minutes_per_day = 390):
        self.agents = agent
        self.exchange = exchange
        self.news_generator = news_generator
        self.num_days = num_days
        self.minutes_per_day = minutes_per_day
        self.sentiment_log = []
        self.wealth_log = []
        self.market_maker_trades = []
        self.strategy_stock_profit_log = []
        
        self.agent_dict = {a.agent_id: a for a in self.agents}
    
    def run(self):
        for day in range(self.num_days):
            print(f"Day {day+1} of {self.num_days}")

            self.run_day(day)
            self.exchange.log_day_close(day)
            self.exchange.reset_day()
        self.summarize_strategy_performance()

        all_ohlc = []
        for stock, ohlc_list in self.exchange.daily_ohlc.items():
            for ohlc in ohlc_list:
                ohlc['stock'] = stock
                all_ohlc.append(ohlc)
        
        df_ohlc = pd.DataFrame(all_ohlc)
        df_ohlc.to_csv("daily_ohlc.csv", index=False)
        print("✅ Logged OHLC data to ohlc_log.csv")

        switch_log = []
        for agent in self.agents:
            if hasattr(agent, 'strategy_switch_log'):
                switch_log.extend(agent.strategy_switch_log)
                print(f"Agent {agent.agent_id} switches: {len(agent.strategy_switch_log)}")
        
        if switch_log:
            df = pd.DataFrame(switch_log)
            df.to_csv("strategy_switch_log.csv", index=False)
            print("✅ Logged strategy switch to strategy_switch_log.csv")

        if self.strategy_stock_profit_log:
            df = pd.DataFrame(self.strategy_stock_profit_log)
            df.to_csv("strategy_stock_profit_log.csv", index=False)
            print("✅ Logged strategy-stock profit to strategy_stock_profit_log.csv")
        
        # Send data to API
        requests.post("http://localhost:8000/update/ohlc", json = self.exchange.daily_ohlc)
        requests.post("http://localhost:8000/update/wealth", json = self.wealth_log)
        requests.post("http://localhost:8000/update/sentiment", json = self.sentiment_log)

        
    def summarize_strategy_performance(self):
        import pandas as pd

        df = pd.DataFrame(self.wealth_log)
        last_day = df['day'].max()
        final_wealth = df[df['day'] == last_day]

        summary = final_wealth.groupby('strategy')['wealth'].agg(['mean', 'std', 'min', 'max'])
        print("\n📈 Strategy Performance Summary (Final Day):")
        print(summary)

        #Market Maker Tracker
        mm_df = final_wealth[final_wealth['is_market_maker'] == True]
        if not mm_df.empty:
            mm = mm_df.iloc[0]
            print(f"\n🏦 Market Maker Performance:\n  Final Wealth: ${mm['wealth']:.2f}\n  Cash: ${mm['cash']:.2f}")
        return
    
    def log_news_sentiment(self, day_idx, minute, sentiment_dict):
        for stock, value in sentiment_dict.items():
            self.sentiment_log.append({
                'day': day_idx,
                'minute': minute,
                'stock': stock,
                'sentiment': value
            })
    
    def log_agent_wealth(self, day_idx):
        for agent in self.agents:
            wealth = agent.cash
            for stock, shares in agent.portfolio.items():
                price = self.exchange.get_price(stock)
                wealth += shares * price
            
            self.wealth_log.append({
                'agent_id': agent.agent_id,
                'strategy': agent.strategy_type,
                'day': day_idx,
                'cash': agent.cash,
                **agent.portfolio,
                'wealth': wealth,
                'is_market_maker': agent.strategy_type == 'market_maker'
            })

            if hasattr(agent, 'update_performance'):
                agent.update_performance(wealth, day_idx)

    def run_day(self, day_idx):
        for event in self.news_generator.market_events:
            if event["day"] == day_idx:
                if "stock" in event:
                    print(f"📣 Impact Event: {event['type']} on {event['stock']} | Impact: {event['impact']:+.2f}")
                elif event.get("target") == "market":
                    print(f"🌍 Market Event: {event['type']} | Impact on all stocks: {event['impact']:+.2f}")
        
        for minute in range(self.minutes_per_day):
            sentiment = self.news_generator.get_sentiment(day_idx, minute)
            self.log_news_sentiment(day_idx, minute, sentiment)
            
            market_obs = self.exchange.get_observation()
            market_obs['sentiment'] = sentiment

            active_agents = np.random.choice(self.agents,
                                             size = int(0.1 * len(self.agents)),
                                             replace = False)
            
            # Separate HFTs for full-minute activation
            hft_agents = [a for a in self.agents if a.strategy_type == "hft"]
            active_agents = np.random.choice([a for a in self.agents if a.strategy_type != "hft"],
                                 size=int(0.1 * len(self.agents)), replace = False)
            
            active_agents = list(active_agents) + hft_agents
            
            for agent in active_agents:
                decisions = agent.decide_action(market_obs)
                if decisions:
                    for order in decisions:
                        self.exchange.submit_order(order['stock'], order)
            
            self.exchange.match_all(self.agent_dict)

            for trade in self.exchange.trades:
                if 99999 in [trade['buyer_id'], trade['seller_id']]:
                    self.market_maker_trades.append({
                        'day': day_idx,
                        'stock': trade['stock'],
                        'price': trade['price'],
                        'quantity': trade['quantity'],
                        'role': 'buy' if trade['buyer_id'] == 99999 else 'sell'
                    })
        
        price_summary = ", ".join([f"{s}: {p:.2f}" for s, p in self.exchange.prices.items()])
        print(f"Day {day_idx + 1} completed. Prices: {price_summary}")
        self.log_agent_wealth(day_idx)
        self.log_strategy_stock_profit(day_idx)

        # Send data to API
        requests.post("http://localhost:8000/update/ohlc", json = self.exchange.daily_ohlc)
        requests.post("http://localhost:8000/update/wealth", json = self.wealth_log)
        requests.post("http://localhost:8000/update/sentiment", json = self.sentiment_log)

        self.exchange.save_trade_log()
    
    def log_strategy_stock_profit(self, day_idx):
        '''
        Aggregates and logs the profit per strategy per stock for the current day.
        '''
        profit_data = {}

        for agent in self.agents:
            strategy = agent.strategy_type
            if strategy == 'market_maker':
                continue
            
            if hasattr(agent, 'strategy_type'):
                strategy = agent.strategy_type
            
            for stock, shares in agent.portfolio.items():
                price = self.exchange.get_price(stock)
                value = shares * price
                key = (strategy, stock)
                profit_data.setdefault(key, 0)
                profit_data[key] += value
        
        for (strategy, stock), total_value in profit_data.items():
            self.strategy_stock_profit_log.append({
                'day': day_idx,
                'strategy': strategy,
                'stock': stock,
                'profit': total_value
            })
            