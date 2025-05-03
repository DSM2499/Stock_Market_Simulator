from modules.agent_factory import create_agent
from modules.exchange import Exchange
from modules.news import NewsGenerator
from modules.simulation import Simulation
from analysis.visualization import plot_individual_candlestick_charts, plot_top_5_agent_wealth, plot_evolving_strategy_transitions
import yaml
import pandas as pd
def main():
    # Load configuration
    with open('/Users/dinakarmurthy/Desktop/Job Work/Projects/Stock_Market_Sim_ABM/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    num_agents = config["num_agents"]
    num_days = config["num_days"]
    minutes_per_day = config["minutes_per_day"]
    stocks = config["stocks"]

    #setup
    agents = create_agent(num_agents, config_override = config)
    exchange = Exchange(stock_config = stocks, transaction_cost_rate = 0.0005)
    news_generator = NewsGenerator(num_days, config_override = config)

    sim = Simulation(
        agent = agents,
        exchange = exchange,
        news_generator = news_generator,
        num_days = num_days,
        minutes_per_day = minutes_per_day
    )

    sim.run()

    pd.DataFrame(sim.market_maker_trades).to_csv("market_maker_trades.csv", index = False)
    pd.DataFrame(sim.wealth_log).to_csv("agent_wealth.csv", index = False)
    pd.DataFrame(sim.sentiment_log).to_csv("sentiment_log.csv", index = False)
    
    plot_individual_candlestick_charts(exchange.daily_ohlc)
    df_wealth = pd.read_csv("agent_wealth.csv")  # or use sim.wealth_log if still in memory
    plot_top_5_agent_wealth(df_wealth)
    plot_evolving_strategy_transitions()

    

if __name__ == "__main__":
    main()
