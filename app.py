import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

from dam_scraper import get_dam_data
from rtm_scraper import get_rtm_data
from gdam_scraper import get_gdam_data

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Open Access Power Market Dashboard", layout="wide")

# 🔄 Auto-refresh every 15 minutes (900000 ms)
st_autorefresh(interval=15 * 60 * 1000, key="refresh")

# 🔧 Sidebar Controls
st.sidebar.header("⚙️ Filter Settings")
max_blocks = st.sidebar.slider("How many recent time blocks to show?", min_value=5, max_value=96, value=20)
mcp_alert_threshold = st.sidebar.number_input("MCP Alert Threshold (₹/MWh)", min_value=1000, max_value=10000, value=8000)

# 🧾 Header
st.title("🔌 Real-Time Open Access Power Market Dashboard")
st.caption("Live data from IEX for DAM, RTM, and GDAM | Auto-refresh every 15 minutes")

# 📁 Tabs for Market Types
tabs = st.tabs(["📊 DAM", "⏱️ RTM", "🌱 GDAM"])

# 🔍 Utility: Analyze and Plot
def display_market_data(df, market_name, time_col="Time Block", mcp_col="MCP (Rs/MWh)", vol_col="Final Scheduled Volume (MW)"):
    if df.empty:
        st.warning(f"No data found for {market_name}.")
        return

    # Show last N rows
    df_filtered = df.tail(max_blocks)
    st.dataframe(df_filtered, use_container_width=True)

    # Convert columns
    df_filtered[mcp_col] = pd.to_numeric(df_filtered[mcp_col], errors="coerce")
    if vol_col in df_filtered.columns:
        df_filtered[vol_col] = pd.to_numeric(df_filtered[vol_col], errors="coerce")

    # 🚨 Alert if high MCP
    if df_filtered[mcp_col].max() >= mcp_alert_threshold:
        st.error(f"⚠️ Alert: MCP exceeded ₹{mcp_alert_threshold}/MWh!")

    # 📈 MCP Trend
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_filtered[time_col], df_filtered[mcp_col], marker='o', label="MCP")
    ax.set_title(f"{market_name} MCP Trend")
    ax.set_xlabel("Time Block")
    ax.set_ylabel("MCP (₹/MWh)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    st.pyplot(fig)

    # 📊 Aggregate Stats
    avg_mcp = df_filtered[mcp_col].mean()
    st.metric(label="📉 Avg MCP", value=f"₹{avg_mcp:,.0f}/MWh")
    if vol_col in df_filtered.columns:
        total_volume = df_filtered[vol_col].sum()
        st.metric(label="⚡ Total Volume", value=f"{total_volume:,.0f} MW")

# 📊 DAM Tab
with tabs[0]:
    st.subheader("📊 Day-Ahead Market (DAM)")
    try:
        dam_df = get_dam_data()
        display_market_data(dam_df, "DAM")
    except Exception as e:
        st.error(f"Error loading DAM data: {e}")

# ⏱️ RTM Tab
with tabs[1]:
    st.subheader("⏱️ Real-Time Market (RTM)")
    try:
        rtm_df = get_rtm_data()
        display_market_data(rtm_df, "RTM", time_col="Time Block", vol_col="Final Scheduled Volume (MW)")
    except Exception as e:
        st.error(f"Error loading RTM data: {e}")

# 🌱 GDAM Tab
with tabs[2]:
    st.subheader("🌱 Green Day-Ahead Market (GDAM)")
    try:
        gdam_df = get_gdam_data()
        display_market_data(gdam_df, "GDAM", time_col="Time Block", vol_col="Final Scheduled Total (MWh)")
    except Exception as e:
        st.error(f"Error loading GDAM data: {e}")


