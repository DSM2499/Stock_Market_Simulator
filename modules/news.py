#Sentiment generator and dummy news shocks

import numpy as np
import yaml

class NewsGenerator:
    def __init__(self, num_days, config_path = "config.yml", config_override = None):
        if config_override:
            config = config_override
        else:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)

        self.mode = config['news'].get('mode', 'random')
        self.daily_vol = config['news'].get('daily_volatility', 0.2)
        self.shock_days = config['news'].get('shock_days', [])
        self.shock_magnitude = config['news'].get('shock_magnitude', -0.9)
        self.stocks = [s['symbol'] for s in config['stocks']]
        self.breaking_events = config['news'].get('breaking_events', [])
        self.market_events = config['news'].get('market_events', [])

        self.competitor_map = {
            "AAPL": "MSFT",
            "MSFT": "AAPL",
            "DSM": "SHOP",
            "SHOP": "DSM"
        }


        self.num_days = num_days
        self.sentiment_series = self._generate_sentiment_series()

    def _generate_sentiment_series(self):
        sentiment_series = []

        for day in range(self.num_days):
            daily_sentiment = {}

            for stock in self.stocks:
                if self.mode == 'neutral':
                    daily_sentiment[stock] = 0.0
                elif self.mode == 'random':
                    value = np.random.normal(0, self.daily_vol)
                    daily_sentiment[stock] = np.clip(value, -1, 1)
                elif self.mode == 'scripted':
                    if day in self.shock_days and stock == self.stocks[0]:
                        daily_sentiment[stock] = self.shock_magnitude
                        #Inject positive sentiment for competitor
                        rival = self.competitor_map.get(stock)
                        if rival:
                            daily_sentiment[rival] = abs(self.shock_magnitude)
                    else:
                        value = np.random.normal(0, self.daily_vol)
                        daily_sentiment[stock] = np.clip(value, -1, 1)
                else:
                    raise ValueError(f"Unknown news mode: {self.mode}")

            for event in self.breaking_events:
                if event['day'] == day:
                    target = event['stock']
                    impact = event['impact']
                    
                    daily_sentiment[target] = impact

                    rival = self.competitor_map.get(target)
                    if rival and 'spillover' in event:
                        daily_sentiment[rival] = event['spillover']
            
            for event in self.market_events:
                if event['day'] == day:
                    impact = event['impact']

                    if event.get('target') == 'market':
                        for stock in self.stocks:
                            daily_sentiment[stock] += impact
                    elif 'stock' in event:
                        daily_sentiment[event['stock']] += impact
            
            for stock in self.stocks:
                if stock not in daily_sentiment:
                    daily_sentiment[stock] = np.random.normal(0, self.daily_vol)
            
            for stock in self.stocks:
                daily_sentiment[stock] = np.clip(daily_sentiment[stock], -1, 1)

            sentiment_series.append(daily_sentiment)

        return sentiment_series
                        

    def get_sentiment(self, day, minute = None):
        if 0 <= day < self.num_days:
            return self.sentiment_series[day]
        return {stock: 0.0 for stock in self.stocks}
        