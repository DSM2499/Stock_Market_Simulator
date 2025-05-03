# Post-simulation reports & visualizations
# Candlestick and performance charts using Plotly

import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.subplots import make_subplots
import os



def plot_individual_candlestick_charts(ohlc_data_dict, output_dir = "candlestick_charts"):
    """
    Plots individual candlestick charts with volume overlays for each stock.
    """
    os.makedirs(output_dir, exist_ok=True)

    for stock, ohlc_list in ohlc_data_dict.items():
        df = pd.DataFrame(ohlc_list)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.8, 0.2],
                            subplot_titles=[f"{stock} - Candlestick Chart", "Volume"])

        # Candlestick plot (row 1)
        fig.add_trace(go.Candlestick(
            x=df['day'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=False
        ), row=1, col=1)

        # Volume bar chart (row 2)
        fig.add_trace(go.Bar(
            x=df['day'],
            y=df['volume'],
            marker_color='blue',
            name='Volume',
            showlegend=False
        ), row=2, col=1)

        # Layout tweaks
        fig.update_layout(
            height=600,
            width=800,
            template="plotly_white",
            margin=dict(t=40, b=40),
        )

        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        file_path = os.path.join(output_dir, f"{stock}_candlestick_volume.html")
        fig.write_html(file_path)
        print(f"✅ Saved {stock} chart with volume to {file_path}")

def plot_top_5_agent_wealth(wealth_log_df):
    """
    Plots the wealth evolution of the top 5 non-market-maker agents.
    """
    # Filter non-market-maker
    df = wealth_log_df[wealth_log_df["is_market_maker"] == False]

    # Get agent wealth on final day
    last_day = df["day"].max()
    final_wealth = df[df["day"] == last_day]

    # Select top 5 earners
    top_agents = final_wealth.nlargest(5, "wealth")[["agent_id", "strategy", "wealth"]]
    top_ids = top_agents["agent_id"].tolist()

    # Plot
    plt.figure(figsize=(12, 6))
    for _, row in top_agents.iterrows():
        agent_df = df[df["agent_id"] == row["agent_id"]]
        plt.plot(agent_df["day"], agent_df["wealth"],
                 label=f"Agent {row['agent_id']} ({row['strategy']})")

    plt.title("💰 Top 5 Agent Wealth Over Time (Excl. Market Makers)", fontsize=14)
    plt.xlabel("Day")
    plt.ylabel("Wealth ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_evolving_strategy_transitions(log_path="/Users/dinakarmurthy/Desktop/Job Work/Projects/Stock_Market_Sim_ABM/strategy_switch_log.csv"):
    """
    Visualizes strategy transitions of evolving agents over time.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    if not os.path.exists(log_path):
        print("⚠️ Strategy switch log not found.")
        return

    df = pd.read_csv(log_path)
    if df.empty:
        print("⚠️ No data in strategy switch log.")
        return

    plt.figure(figsize=(14, 6))
    for agent_id in df['agent_id'].unique():
        agent_df = df[df['agent_id'] == agent_id].sort_values("day")
        plt.plot(agent_df["day"], agent_df["to"], marker="o", label=f"Agent {agent_id}")

    plt.title("🧬 Strategy Transitions Over Time (Evolving Agents)")
    plt.xlabel("Day")
    plt.ylabel("Strategy")
    plt.yticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()