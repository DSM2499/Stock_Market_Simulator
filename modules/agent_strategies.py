# Logic for momentum, contrarian, etc.
#Order Structure
'''
{
    "agent_id": agent.agent_id,
    "type": "buy" or "sell",
    "quantity": int,
    "price": float,  # Limit price (or None for market order)
}
'''

import numpy as np
import random

TRADE_FRACTION = 0.1  #Fraction of cash/shares used per trade
LOOKBACK_WINDOW = 5   #Minutes for moving average

class MomentumStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def decide(self, market_obs, agent):
       decisions = []
       prices = market_obs['prices']
       sentiment = market_obs['sentiment']
       
       for stock, price in prices.items():
           #Dummy momentum singal: sentiment boost
            if sentiment.get(stock, 0) > 0.1:
               budget = agent.cash * TRADE_FRACTION
               qty = int(budget // price)
               if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'buy',
                        'quantity': qty,
                        'price': None
                    })
            elif sentiment.get(stock, 0) < -0.1 and agent.portfolio[stock] > 0:
                qty = int(agent.portfolio[stock] * TRADE_FRACTION)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'sell',
                        'quantity': qty,
                        'price': None
                    })
       return decisions
        
    
class ContrarianStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def decide(self, market_obs, agent):
        decisions = []
        prices = market_obs['prices']
        sentiment = market_obs['sentiment']

        for stock, price in prices.items():
            if sentiment.get(stock, 0) < -0.1:
                budget = agent.cash * TRADE_FRACTION
                qty = int(budget // price)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'buy',
                        'quantity': qty,
                        'price': None
                    })
            elif sentiment.get(stock, 0) > 0.1 and agent.portfolio[stock] > 0:
                qty = int(agent.portfolio[stock] * TRADE_FRACTION)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'sell',
                        'quantity': qty,
                        'price': None
                    })
        return decisions
                 
class RiskAverseStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def decide(self, market_obs, agent):
        decisions = []
        prices = market_obs['prices']
        sentiment = market_obs['sentiment']

        for stock, price in prices.items():
            sent = sentiment.get(stock, 0)
            if sent > 0.2:
                budget = agent.cash * TRADE_FRACTION
                qty = int(budget // price)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'buy',
                        'quantity': qty,
                        'price': None
                    })
            elif sent < -0.2 and agent.portfolio[stock] > 0:
                qty = int(agent.portfolio[stock] * TRADE_FRACTION)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'sell',
                        'quantity': qty,
                        'price': None
                    })
        return decisions
    
class NoiseStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def decide(self, market_obs, agent):
        decisions = []
        prices = market_obs['prices']
        
        for stock, price in prices.items():
            if random.random() < 0.2:
                action = random.choice(['buy', 'sell'])
                if action == 'buy':
                    budget = agent.cash * TRADE_FRACTION
                    qty = int(budget // price)
                    if qty > 0:
                        decisions.append({
                            'agent_id': agent.agent_id,
                            'stock': stock,
                            'type': 'buy',
                            'quantity': qty,
                            'price': None
                        })
                elif action == 'sell' and agent.portfolio[stock] > 0:
                    qty = int(agent.portfolio[stock] * TRADE_FRACTION)
                    if qty > 0:
                        decisions.append({
                            'agent_id': agent.agent_id,
                            'stock': stock,
                            'type': 'sell',
                            'quantity': qty,
                            'price': None
                        })
        return decisions

class MarketMakerAgent:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def __init__(self, agent_id, stock_list, cash = 10_000_000.00, inventory = 10_000):
        self.agent_id = agent_id
        self.strategy_type = 'market_maker'
        self.cash = cash
        self.portfolio = {stock['symbol']: inventory for stock in stock_list}
        self.history = []
    
    def decide_action(self, market_obs):
        decisions = []
        prices = market_obs['prices']

        spread_pct = 0.005
        trade_qty = 25

        for stock, price in prices.items():
            if price <= 0:
                continue

            ask_price = price * (1 + spread_pct)
            bid_price = price * (1 - spread_pct)

            if self.portfolio[stock] >= trade_qty:
                decisions.append({
                    'agent_id': self.agent_id,
                    'stock': stock,
                    'type': 'sell',
                    'quantity': trade_qty,
                    'price': ask_price
                })
            
            if self.cash >= bid_price * trade_qty:
                decisions.append({
                    'agent_id': self.agent_id,
                    'stock': stock,
                    'type': 'buy',
                    'quantity': trade_qty,
                    'price': bid_price
                })
        return decisions

class MeanReversionStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def __init__(self, lookback = 5, trade_fraction = 0.2, threshold = 0.01):
        self.lookback = lookback
        self.trade_fraction = trade_fraction
        self.threshold = threshold
    
    def decide(self, market_obs, agent):
        decisions = []
        prices = market_obs['prices']
        price_history = market_obs.get('price_history', {})

        for stock, price in prices.items():
            history = price_history.get(stock, [])
            if len(history) < self.lookback:
                continue

            avg_price = sum(history[-self.lookback:]) / self.lookback
            deviation = (price - avg_price) / avg_price

            if deviation < -self.threshold:
                budget = agent.cash * self.trade_fraction
                qty = int(budget // price)
                if qty > 0:
                    decisions.append({
                        'agent_id': agent.agent_id,
                        'stock': stock,
                        'type': 'buy',
                        'quantity': qty,
                        'price': None
                    })
            
            elif deviation > self.threshold and agent.portfolio[stock] > 0:
                qty = int(agent.portfolio[stock] * self.trade_fraction)
                if qty > 0:
                    decisions.append({
                        "agent_id": agent.agent_id,
                        "stock": stock,
                        "type": "sell",
                        "quantity": qty,
                        "price": None
                    })
        return decisions

class ArbitrageStrategy:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def __init__(self, stock_pair = ('AAPL', 'MSFT'), lookback = 5,
                 threshold = 0.02, trade_fraction = 0.2):
        self.stock_a, self.stock_b = stock_pair
        self.lookback = lookback
        self.threshold = threshold
        self.trade_fraction = trade_fraction
    
    def decide(self, market_obs, agent):
        decisions = []
        prices = market_obs['prices']
        price_history = market_obs.get('price_history', {})

        price_a = prices.get(self.stock_a)
        price_b = prices.get(self.stock_b)

        hist_a = price_history.get(self.stock_a, [])
        hist_b = price_history.get(self.stock_b, [])

        if not price_a or not price_b or len(hist_a) < self.lookback or len(hist_b) < self.lookback:
            return decisions
        
        ratio_series = [a / b for a, b in zip(hist_a[-self.lookback:], hist_b[-self.lookback:]) if b != 0]
        if not ratio_series:
            return decisions
        
        avg_ratio = sum(ratio_series) / len(ratio_series)
        current_ratio = price_a / price_b
        deviation = (current_ratio - avg_ratio) / avg_ratio

        qty = int((agent.cash * self.trade_fraction) // min(price_a, price_b))
        if qty <= 0:
            return decisions
        
        if deviation > self.threshold and agent.portfolio.get(self.stock_a, 0) >= qty:
            decisions.append({
                'agent_id': agent.agent_id,
                'stock': self.stock_a,
                'type': 'sell',
                'quantity': qty,
                'price': None
            })
            decisions.append({
                'agent_id': agent.agent_id,
                'stock': self.stock_b,
                'type': 'buy',
                'quantity': qty,
                'price': None
            })
        elif deviation < -self.threshold and agent.portfolio.get(self.stock_b, 0) >= qty:
            decisions.append({
                'agent_id': agent.agent_id,
                'stock': self.stock_b,
                'type': 'sell',
                'quantity': qty,
                'price': None
            })
            decisions.append({
                'agent_id': agent.agent_id,
                'stock': self.stock_a,
                'type': 'buy',
                'quantity': qty,
                'price': None
            })
        return decisions

class HFTAgent:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def __init__(self, agent_id, stock_list, cash = 500_000, inventory_per_stock = 150):
        self.agent_id = agent_id
        self.strategy_type = 'hft'
        self.cash = cash
        self.portfolio = {s['symbol']: inventory_per_stock for s in stock_list}
        self.history = []

    def decide_action(self, market_obs):
        decisions = []
        prices = market_obs['prices']
        spread_pct = 0.001
        trade_size = 20

        for stock, price in prices.items():
            if price <= 0:
                continue

            ask_price = price * (1 + spread_pct)
            bid_price = price * (1 - spread_pct)

            if self.portfolio.get(stock, 0) >= trade_size:
                decisions.append({
                    'agent_id': self.agent_id,
                    'stock': stock,
                    'type': 'sell',
                    'quantity': trade_size,
                    'price': ask_price
                })
            
            if self.cash >= bid_price * trade_size:
                decisions.append({
                    'agent_id': self.agent_id,
                    'stock': stock,
                    'type': 'buy',
                    'quantity': trade_size,
                    'price': bid_price
                })
        return decisions

class EvolvingAgent:

    def get_params(self):
        return {'threshold': 0.1}
    
    def set_params(self, params):
        pass

    def __init__(self, agent_id, stock_list, initial_strategy = 'momentum', cash = 500_000):
        self.agent_id = agent_id
        self.stock_list = stock_list
        self.cash = cash
        self.portfolio = {s['symbol']: 0 for s in stock_list}
        self.strategy_type = 'evolving'

        self.performance_history = []
        self.history = []
        self.evolution_log = []
        self.strategy_name = initial_strategy

        self.strategy_switch_log = []

        self.strategy = self._initialize_strategy(self.strategy_name)

    def _initialize_strategy(self, name, params = None):
        if name == "momentum":
            strat = MomentumStrategy()
        elif name == "contrarian":
            strat = ContrarianStrategy()
        elif name == "mean_reversion":
            strat = MeanReversionStrategy()
        elif name == "arbitrage":
            strat = ArbitrageStrategy()
        elif name == "noise":
            strat = NoiseStrategy()
        elif name == "risk_averse":
            strat = RiskAverseStrategy()
        else:
            raise ValueError(f"Unknown strategy: {name}")
        
        if params and hasattr(strat, 'set_params'):
            strat.set_params(params)
        
        return strat
    
    def get_genome(self):
        """Returns the current strategy parameters as a 'genome' dictionary"""
        if hasattr(self.strategy, "get_params"):
            return {
                'strategy_name': self.strategy_name,
                'params': self.strategy.get_params()
            }
        return {
            'strategy_name': self.strategy_name,
            'params': {}
        }
    
    def mutate_genome(self, genome):
        '''
        Apply mutation to strategy parameters
        '''
        mutated = dict(genome)
        mutated['strategy_name'] = genome['strategy_name']

        # Mutate parameters if available
        if genome['params']:
            mutated_params = {}
            for k, v in genome['params'].items():
                if isinstance(v, (float, int)):
                    mutated_params[k] = v + np.random.nomral(0, 0.1 * abs(v + 1e-6))
                else:
                    mutated_params[k] = v
            mutated['params'] = mutated_params
        
        return mutated
     
    def clone_from(self, parent):
        genome = parent.get_genome()
        new_genome = self.mutate_genome(genome)

        self.strategy_name = new_genome['strategy_name']
        self.strategy = self._initialize_strategy(self.strategy_name, new_genome['params'])

        self.cash = 700_000
        self.portfolio = {s: 0 for s in self.portfolio}

        self.evolution_lop.append({
            'from': parent.agent_id,
            'strategy': self.strategy_name,
            'day': len(self.performance_history)
        })

    def decide_action(self, market_obs):
        return self.strategy.decide(market_obs, self)
    
    def update_performance(self, wealth, day_idx):
        self.performance_history.append({'day': day_idx, 'wealth': wealth})

        if len(self.performance_history) > 10:
            #Check 10-day slope
            past = self.performance_history[-10]['wealth']
            current = wealth
            growth = (current - past) / past

            #Evolve if declining
            if growth < 0.0001:
                self.evolve_strategy()
            
            #print(f"[DEBUG] Agent {self.agent_id} growth over 10 days: {growth:.4f}")

    
    def evolve_strategy(self):
        candidates = ["momentum", "contrarian", "mean_reversion", "arbitrage", "risk_averse"]
        

        current = self.strategy_name
        candidates.remove(current)
        new_strategy = random.choice(candidates)

        self.strategy_name = new_strategy
        self.strategy_type = 'evolving'
        self.strategy = self._initialize_strategy(new_strategy)

        #Log the evolution
        self.strategy_switch_log = getattr(self, 'strategy_switch_log', [])
        self.strategy_switch_log.append({
            'agent_id': self.agent_id,
            "day": self.performance_history[-1]['day'],
            "from": current,
            "to": new_strategy
        })

        #print(f"🧬 Agent {self.agent_id} evolved from {current} to {new_strategy}")
        
