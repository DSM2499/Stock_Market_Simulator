import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests

from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("📊 Stock Market ABM Simulation Dashboard")

# API Base Url
API_URL = 'http://localhost:8000'

# Fetch and Flatten OHLC Data
def fetch_ohlc():
    response = requests.get(f"{API_URL}/data/ohlc")
    if response.status_code != 200:
        st.error("Failed to fetch OHLC data")
        return pd.DataFrame()
    
    raw = response.json()
    records = []
    
    for stock, entries in raw.items():
        for entry in entries:
            entry["stock"] = stock
            records.append(entry)
    
    return pd.DataFrame(records)

# Fetch and Flatten Wealth Data
def fetch_wealth():
    response = requests.get(f"{API_URL}/data/wealth")
    if response.status_code != 200:
        st.error("Failed to fetch wealth data")
        return pd.DataFrame()
    return pd.DataFrame(response.json())

#Sidebar Settings
st.sidebar.header("Options")
refresh = st.sidebar.button("🔄 Refresh Data")
refresh_interval = st.sidebar.slider("Auto-refresh every N seconds", 5, 60, 10)

# Initial Load
ohlc_data = fetch_ohlc()
wealth_data = fetch_wealth()

# Auto Refresh
if refresh:
    st_autorefresh(interval = refresh_interval * 1000)


#Stock Selection
if ohlc_data.empty or "stock" not in ohlc_data.columns:
    st.warning("No OHLC data loaded.")
    st.stop()

stocks = sorted(ohlc_data['stock'].unique())
selected_stock = st.sidebar.selectbox("Select Stock", stocks)

#Candlestick Chart
st.subheader(f"📈 Price Chart for {selected_stock}")
stock_df = ohlc_data[ohlc_data["stock"] == selected_stock]

fig = go.Figure(data=[
    go.Candlestick(
        x = stock_df["day"],
        open = stock_df["open"],
        high = stock_df["high"],
        low = stock_df["low"],
        close = stock_df["close"],
        name = "OHLC"
    )
])
fig.update_layout(
    xaxis_title = "Day",
    yaxis_title = "Price",
    height = 500,
    template = "plotly_dark"
)
st.plotly_chart(fig, use_container_width = True)

# Wealth Plot for Top 5 Agents
st.subheader("💰 Top 5 Agent Wealth Over Time (Excl. Market Makers)")
if wealth_data.empty or "is_market_maker" not in wealth_data.columns:
    st.warning("Wealth data not available.")
    st.stop()

non_mm_df = wealth_data.query("is_market_maker == False")
last_day = non_mm_df["day"].max()
top_agents = (
    non_mm_df[non_mm_df["day"] == last_day]
    .nlargest(5, "wealth")[["agent_id", "strategy", "wealth"]]
)
top_ids = top_agents["agent_id"].tolist()

fig2, ax = plt.subplots(figsize=(12, 5))
for _, row in top_agents.iterrows():
    agent_id = row["agent_id"]
    agent_df = non_mm_df[non_mm_df["agent_id"] == agent_id]
    ax.plot(
        agent_df["day"],
        agent_df["wealth"],
        label = f"Agent {agent_id} ({row['strategy']})",
        linewidth = 2,
    )

ax.set_title("Top 5 Agent Wealth Over Time")
ax.set_xlabel("Day")
ax.set_ylabel("Wealth ($)")
ax.grid(True)
ax.legend()
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

# To sort by wealth in legend:
handles, labels = ax.get_legend_handles_labels()
sorted_pairs = sorted(zip(top_agents["wealth"], handles, labels), reverse=True)
_, handles_sorted, labels_sorted = zip(*sorted_pairs)
ax.legend(handles_sorted, labels_sorted)

st.pyplot(fig2)




