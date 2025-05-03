# Multi Agent Based Stock Market Simulator
This project presents a high-fidelity agent-based simulation of the stock market with multiple asset classes and heterogenous trading agents. This system integrates evolving strategies via genetic-like mutation, real-time sentiment analysis and RESTful APIs for streaming analytics, provinding a sandbox for exploring market microstructures, behavioral economics, and algorithmic trading strategies.

## Introduction
Financial markets are complex systems with diverse participants exhibiting variying motivations and cognitive models. Traditional models often assume rational agents and equilibrium, but empirical market behavior (e.g., bubbles, crashes) often violates these assumptions. o model such emergent phenomena, we developed a simulation that leverages:
- Agent-based Modeling (ABM)
- Evolutionary strategy switching
- Real-time market monitoring with FASTAPI + Streamlit
- Sentiment-triggered trading
- REST APIs for dashboard decoupling

The simulation behavior is governed by a structured YAML configuration file, enabling dynamic control over agent behaviors, market environment, stock properties and logging.

## System Architecture

### 2.1 Configuration Layer
The key configurable areas are:

#### 1. Simulation Duration
- `num_days`: Total number of days to be simulated
- `minutes_per_day`: Represents trading session durations in minutes

#### 2. Agent Configuration
- `num_agents`: TOtal number of regular trading agents
- `num_hft_agents`: Number of High-Frequency_Trader agents
- `agent_distribution`: Specifies the percentage share of agents following each strategy.
    - MomentumL Buys on upward trends.
    - Contrarian: Buys dips and sells highs.
    - Risk-averse: Conservative investm ent logic.
    - Noise: Random, irrational trades.
    - Mean-reversion: Buys low, expecting reversal.
    - Arbitrage: Exploits cross-stock price inefficiencies.
    - Evolving: Adpats strategy fynamically over time (mimics learning agents).

#### 3. News and Sentiment Engine
- `mode`: `random`, `scripted`, `neutral` - controls how news is generated.
- `daily_volatility`: Magnitude of daily sentiment noise affecting decisions.
- `shock_days` & `shock_magnitude`: Introduces exogenous events like crashes or rallies.
- `breaking_events`: Targeted stock events with direct and spillover impact.
- `market_events`: Macro-level events (e.g., interest rate cuts, geopolotical crises)
This allows realistic modeling of sentiment-driven volatility and reactions.

#### 4. Market
- `transaction_fees`: Applied to every trade as cost.

#### Stock Definitions:
- `symbol`: Ticker Name
- `float`: Total available shares
- `initial_price`: Starting price at day 0.
These parameters define market microstructure, liquidity, and diversity.

#### This configuration model enables:
- Rapid tuning of simulation scale (e.g., 10K to 100K agents).
- Stress testing strategies with news shocks.
- Controlled testing of evolving agents under volatility.
- Designing specific experimental market conditions.
- Integration with ML training loops (via logs).

## Simulation Statistics
#### Statistics
- Average Trades Executed Per Day: 32,444 trades
- Average Volume Traded per Day: 88,672 shares
- Average Trade Size: 2.73 shares
- Total Fees Collected: $1,284,194.70
- Top Buyer Traded Volume: ~81,000 shares
- Time for Simulating a Day of Trading: ~25 Seconds


#### Insights
- The model successfully simulates a high-frequency trading environment, with millions of micro-trades reflecting realistic market microstructure. The small average trade size matches HFT and market-making behaviors, confirming that agents are reacting to short-term signals.
- The simulation includes realistic transaction costs. This fee structure acts as both a market friction and an incentive modifier — encouraging efficient trading strategies over random or volume-based ones. This also provides a hook for future features like fee redistribution or taxation policies.
