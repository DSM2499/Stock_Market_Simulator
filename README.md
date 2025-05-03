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

---

### 2.2 Agent Strategies
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

---

### 2.3 Exchange Layer - Simulated Market Microstructure
The Exchange Layer is the central market simulation engine that emulates a realistic multi-asset trading environment. It is built around the mechanics of a limit order book, inspired by real-world stock exchanges. This layer governs how agents interact with the market and how asset prices evolve. It supports key market functionalities:
#### 1. Order Aggregation and Matching
- Agents submit buy or sell orders per stock during each time step.
- These orders include the following details:
    - Desired stock
    - Order Type (buy/sell)
    - Quantity
    - Agent ID
- The exchange does not simulate order price levels directly; instead, it sorts and matches orders using heuristics (e.g., highest buyer matched with lowest seller).
- Matching is done stock-wise with quantity-based prioritization, simulating order book depth behavior.

#### 2. Trade Execution and Settlement
- For matched trades:
    - The buyer’s cash is debited.
    - The seller’s portfolio is reduced.
    - Both agents are charged a transaction fee, simulating brokerage or liquidity costs.
- Executed trades are recorded in a central `trade_log`, including fields like stock, price, quantity, buyer/seller IDs and fees.
- Trading volume and trade count are updated in real time.

#### 3. OHLC Generation (Per Stock)
At the end of each day, the exchange calculates:
- Open: Price of the first trade of the day
- High: Maximum price among trades that day
- Low: Minimum price
- Close: Last trade price of the day
- Volume: Sum of all quantities traded for that stock
This OHLC + Volume data is appended to a per-stock history (`daily_ohlc`) and serves as the visual and analytical foundation for price tracking, sentiment impact analysis amd technical strategies.

#### 4. Price Drift and Market Impact
- If trades occurred, a larger Gaussian noise (𝜎 ~ 0.1) is added to simulate liquidity and volatility-driven drift.
- If no trades occurred, smaller noise (𝜎 ~ 0.01) simulates time decay and random walk behavior.
- This introduces realistic price variance even in the absence of trades, enabling agents to respond to passive signals.

#### 5. Transaction Fee System
- A configurable `transaction_cost_rate` simulates liquidity access costs.
- Total fees collected are logged, and can be used to:
    - Analyze market profitability
    - Study sustainability of liquidity provision
    - Compare strategy costs under various fee models

---

### 2.4 Sentiment Engine - Modeling Exogenous Shocks
The Sentiment Engine introduces external news, earnings reports, and macro events as probabilistic, unstructured influences on market behavior. This is crucial to simulate the “irrational” or sudden volatility seen in real markets.

#### 1. Event Scheduling and Randomization
- At each simulation step (day and/or minute), the engine decides—using a configurable probability—whether a sentiment event occurs.
- If triggered:
    - A stock is randomly selected.
    - The magnitude of sentiment (positive or negative) is sampled from a distribution (e.g., normal or uniform).
    - The direction (bullish/bearish) is also randomized unless otherwise constrained.
This mimics the unpredictability of breaking news, earnings beats/misses, or regulatory shifts.

#### 2. Sentiment Broadcasting to Agents
- Once generated, the sentiment shock is broadcasted to all agents
- How each agent interprets the news depends on their strategy type:
    - Momentum agents may aggressively buy on positive sentiment.
    - Risk-averse agents may reduce trading in volatile (positive or negative) conditions.
    - Arbitrage traders might act only if spreads widen in response.
This introduces an element of agent heterogeneity and allows the study of behavioral propagation of information through the market.

#### 3. Logging and Analysis
- All sentiment events are timestamped and logged in `sentiment_log.csv`, recording:
    - `day`, `minute`
    - `stock`
    - `sentiment`
- This log is used post-simulation to:
    - Correlate agent reactions to sentiment spikes
    - Visualize sentiment trends alongside price movement
    - Compare strategy robustness under high-sentiment conditions

---
### 2.5 Real-Time Visualization via REST API Architecture
In traditional simulations, visualization is often performed after the simulation ends. However, this system introduces a modular, real-time visualization architecture using a REST API server (FastAPI) and a web-based dashboard (Streamlit), fully decoupling simulation from frontend rendering.

#### 1. FastAPI as Middleware
The FastAPI server acts as a real-time middleware between the simulation engine and the visualization interface. It is responsible for receiving updates from the simulation loop, storing them in memory, and exposing them via endpoints consumable by the frontend. This modular architecture promotes parallel development and makes the system suitable for remote or distributed execution.

##### Simulation → API (POST Updates)
At each simulation time stamp (daily)
- The simulation calls:
    - `POST /update/ohlc` with OHLC + volume per stock
    - `POST /update/wealth` with agent-level wealth updates
    - `POST /update/sentiment` with market sentiment data
These routes receive structured payloads validated via Pydantic schemas, ensuring data consistency and schema adherence.

##### API → Dashboard (GET Queries)
The dashboard issues:
- `GET /data/ohlc` - Fetches historical price/volume data
- `GET /data/wealth` - Fetches agent wealth history
- `GET /data/sentiment` - Fetches the stream of sentiment events
These endpoints allow the dashboard to refresh data without needing direct access to simulation memory or log files, enabling asynchronous and scalable real-time visualization.

##### In-Memory Data Management with `DataStore`
The `DataStore` class acts as the temporary in-memory database within the API:
- Stores OHLC, wealth, and sentiment data in structured Python lists.
- Converts these to pandas DataFrames on-the-fly for visualization.
- Supports dynamic extension and querying with minimal performance overhead.
- Ensures no disk I/O bottleneck, thus maintaining the speed required for real-time updates.
This approach ensures flexibility while keeping the system lightweight and fast.

---
### 2.6 Real-Time Interactive Dashboard (Streamlit Frontend)
The Streamlit dashboard offers a dynamic web interface for real-time simulation monitoring. It fetches simulation data from the FastAPI endpoints and renders it with high-performance plotting tools like Plotly and Matplotlib.

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
