# Multi Agent Based Stock Market Simulator
This project presents a high-fidelity agent-based simulation of the stock market with multiple asset classes and heterogenous trading agents. This system integrates evolving strategies via genetic-like mutation, real-time sentiment analysis and RESTful APIs for streaming analytics, provinding a sandbox for exploring market microstructures, behavioral economics, and algorithmic trading strategies.

## Introduction
Modern financial markets are increasingly driven by algorithmic decision-making, with traders ranging from retail investors to high-frequency firms. Simulating such a system enables controlled experimentation, scenario testing, and behavioral analysis. The primary aim of this project was to build an agent-based stock market simulator that:
- Reflects real-world complexity via trader heterogeneity
- Supports strategic evolution based on feedback
- Real-time market monitoring with FASTAPI + Streamlit
- Incorporates macro-level sentiment effects
- Provides real-time insights via a responsive dashboard interface

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

## Agent Strategies
To replicate the diversity of real-world market participants, the simulation employs a range of trader archetypes—each with distinct decision heuristics and market behaviors. These agents embody classical strategies in behavioral finance, algorithmic trading, and market microstructure theory.
#### 1. Momentum Traders
- **Behavior**:  Buy assets that are rising in price, sell those declining—“ride the trend.”
- **Implementation**: Agents track price momentum over recent time windows (e.g., last 3–5 days). A strong positive trend increases buy probability; negative trend prompts selling.
- **Goal**: Capitalize on continuation patterns in price movement.
#### 2. Contrarian Traders
- **Behavior**: Do the opposite of the trend—buy low (on dips), sell high (on rallies).
- **Implementation**: Agents look for negative price momentum and place buy orders; conversely, they sell during rapid upticks.
- **Goal**: Profit from mean reversion and overreaction correction.
#### 3. Risk-Averse Traders
- **Behavior**: Trade infrequently, seek stable long-term returns, avoid volatility.
- **Implementation**: Allocate capital proportionally to stocks with lower recent volatility and avoid trading during high-sentiment fluctuations.
- **Goal**: Preserve capital while cautiously growing wealth.
#### 4. Noise Traders
- **Behavior**: Trade randomly without any rational basis, emulating retail traders or bots with imperfect info.
- **Implementation**: Randomly choose whether to buy, sell, or hold, regardless of fundamentals or sentiment.
- **Goal**: Introduce stochasticity and market liquidity. Often exploited by others.
#### 5. Mean-Reversion Traders
- **Behavior**: Assume prices will revert to a fair value after deviation.
- **Implementation**: Use a moving average to detect deviations. Buy when price < moving average; sell when price > moving average.
- **Goal**: Exploit oversold and overbought signals.
#### 6. Arbotrage Traders
- **Behavior**: Look for price discrepancies between correlated stocks.
- **Implementation**: rack spreads between stocks (e.g., AAPL vs. MSFT). If spread deviates from historical norm, take offsetting positions expecting convergence.
- **Goal**: Achieve market-neutral profits from inefficiencies.
#### 7. Evolving Agents
- **Behavior**: Begin with a base strategy, but periodically mutate to a new one based on performance.
- **Implementation**: At fixed intervals, underperforming evolving agents probabilistically switch to a new strategy (excluding their current one). All switches are logged.
- **Goal**: Simulate evolution of intelligence, learning, and dynamic adaptability in algorithmic systems.

This spectrum of strategies enables the simulation to study phenomena such as:
- Market bubbles and crashes
- Profitability under volatility
- Strategy dominance cycles
- Ecosystem diversity under pressure
- The emergence of collective behavior


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
