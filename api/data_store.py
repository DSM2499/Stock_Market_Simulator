class DataStore:
    def __init__(self):
        self.ohlc_data = {}         # key: stock symbol → list of dicts
        self.wealth_data = []       # list of dicts
        self.sentiment_data = []    # list of dicts

    def update_ohlc(self, new_ohlc):
        for stock, entries in new_ohlc.items():
            if stock not in self.ohlc_data:
                self.ohlc_data[stock] = []
            self.ohlc_data[stock].extend(entries)

    def update_wealth(self, entries):
        self.wealth_data.extend(entries)

    def update_sentiment(self, entries):
        self.sentiment_data.extend(entries)

    def get_ohlc(self):
        return self.ohlc_data

    def get_wealth(self):
        return self.wealth_data

    def get_sentiment(self):
        return self.sentiment_data