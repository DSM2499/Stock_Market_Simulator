# Generates the population of agents

import random
import numpy as np
import yaml

from modules.agent_strategies import (
    MomentumStrategy,
    ContrarianStrategy,
    RiskAverseStrategy,
    NoiseStrategy,
    MarketMakerAgent,
    MeanReversionStrategy,
    ArbitrageStrategy,
    HFTAgent,
    EvolvingAgent
)

#Define the Agent Class
class Agent:
    def __init__(self, agent_id, strategy_type, strategy, stock_list, cash = 1_000_000.00):
        self.agent_id = agent_id
        self.strategy_type = strategy_type
        self.strategy = strategy

        #Portfolio State
        self.cash = cash
        self.portfolio = {stock['symbol']: 0 for stock in stock_list}
        #History
        self.history = []

    def decide_action(self, market_observation):
        return self.strategy.decide(market_observation, self)
    
def create_agent(num_agents, config_path = "config.yml", config_override = None):
    if config_override:
        config = config_override
    else:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

    dist = config['agent_distribution']
    stock_list = config['stocks']
    agent_list = []
    agent_counter = 0
    num_hft_agents = config['num_hft_agents']

    #Create HFT agents
    for i in range(num_hft_agents):
        hft = HFTAgent(agent_id = 9990 + i, stock_list = stock_list, cash = 700_000)
        agent_list.append(hft)

    # Prevent ID overlap
    agent_counter = 9990 + num_hft_agents

    def assign_strategy(agent_id, strategy_type):
        if strategy_type == "momentum":
            return Agent(agent_id, strategy_type, MomentumStrategy(), stock_list)
        elif strategy_type == "contrarian":
            return Agent(agent_id, strategy_type, ContrarianStrategy(), stock_list)
        elif strategy_type == "risk_averse":
            return Agent(agent_id, strategy_type, RiskAverseStrategy(), stock_list)
        elif strategy_type == "noise":
            return Agent(agent_id, strategy_type, NoiseStrategy(), stock_list, cash = 500_000)
        elif strategy_type == "mean_reversion":
            return Agent(agent_id, strategy_type, MeanReversionStrategy(), stock_list)
        elif strategy_type == "arbitrage":
            return Agent(agent_id, strategy_type, ArbitrageStrategy(), stock_list)
        elif strategy_type == "evolving":
            return EvolvingAgent(agent_id, stock_list, cash = 1_000_000)
        else:
            raise ValueError(f"Invalid strategy type: {strategy_type}")
        
    #Determine counts
    for strategy, proportion in dist.items():
        count = int(num_agents * proportion)
        for _ in range(count):
            agent = assign_strategy(agent_counter, strategy)
            agent_list.append(agent)
            agent_counter += 1
        
    while len(agent_list) < num_agents:
        agent = assign_strategy(agent_counter, random.choice(list(dist.keys())))
        agent_list.append(agent)
        agent_counter += 1
    
    mm_agent = MarketMakerAgent(agent_id = 99999, stock_list = stock_list, cash = 10_000_000, inventory = 1000)
    agent_list.append(mm_agent)

    random.shuffle(agent_list)

    #Distribute stock floats
    distribute_initial_holdings(agent_list, stock_list)

    return agent_list

def distribute_initial_holdings(agents, stock_config):
    for stock in stock_config:
        symbol = stock['symbol']
        total_shares = stock['float']
        price = stock['initial_price']

        while total_shares > 0:
            agent = random.choice(agents)
            qty = min(10, total_shares)

            if agent.cash >= qty * price:
                agent.portfolio[symbol] += qty
                agent.cash -= qty * price
                total_shares -= qty
