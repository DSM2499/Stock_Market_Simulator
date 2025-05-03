# Multi Agent Based Stock Market Simulator

## Simulation Statistics
#### Statistics
- Total Trades Executed Per Day: 32,444 trades
- Total Volume Traded per Day: 88,672 shares
- Average Trade Size: 2.73 shares
- Total Fees Collected: $1,284,194.70
- Top Buyer Traded Volume: ~81,000 shares
- Time for Simulating a Day of Trading: ~25 Seconds


#### Insights
- The model successfully simulates a high-frequency trading environment, with millions of micro-trades reflecting realistic market microstructure. The small average trade size matches HFT and market-making behaviors, confirming that agents are reacting to short-term signals.
- The simulation includes realistic transaction costs. This fee structure acts as both a market friction and an incentive modifier — encouraging efficient trading strategies over random or volume-based ones. This also provides a hook for future features like fee redistribution or taxation policies.
