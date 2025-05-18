import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Real-Time Trading Dashboard", layout="wide")
st.title("📊 Real-Time Trading with Candlestick, EMA, RSI & Signals")

DATA_DIR = "/tmp/stream_output/"
# Refresh every 65 seconds
REFRESH_INTERVAL = 65

chart_placeholder = st.empty()

def load_data():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".parquet")]
    if not files:
        return pd.DataFrame()

    df = pd.concat([pd.read_parquet(os.path.join(DATA_DIR, f)) for f in files])
    return df

def compute_indicators(df):
    df["EMA_10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["EMA_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Generate basic Buy/Sell signals
    df["signal"] = np.where((df["RSI"] < 30) & (df["close"] > df["EMA_10"]), "Buy",
                     np.where((df["RSI"] > 70) & (df["close"] < df["EMA_10"]), "Sell", "Hold"))
    
    df["prev_EMA_20"] = df["EMA_20"].shift(1)
    df["prev_EMA_50"] = df["EMA_50"].shift(1)

    crossover_buy = (df["EMA_20"] > df["EMA_50"]) & (df["prev_EMA_20"] <= df["prev_EMA_50"])
    crossover_sell = (df["EMA_20"] < df["EMA_50"]) & (df["prev_EMA_20"] >= df["prev_EMA_50"])

    df.loc[crossover_buy, "signal"] = "Buy"
    df.loc[crossover_sell, "signal"] = "Sell"

    return df

def plot_price_chart(df):
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["datetime"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candlestick"
    ))

    # EMA
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["EMA_10"],
        line=dict(color="blue", width=2),
        name="EMA_10"
    ))

    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["EMA_20"],
        line=dict(color="green", width=2),
        name="EMA_20"
    ))

    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["EMA_50"],
        line=dict(color="red", width=2),
        name="EMA_50"
    ))

    # Buy/Sell markers
    buy_signals = df[df["signal"] == "Buy"]
    sell_signals = df[df["signal"] == "Sell"]

    fig.add_trace(go.Scatter(
        x=buy_signals["datetime"],
        y=buy_signals["close"],
        mode="markers",
        marker=dict(color="green", size=10, symbol="triangle-up"),
        name="Buy"
    ))

    fig.add_trace(go.Scatter(
        x=sell_signals["datetime"],
        y=sell_signals["close"],
        mode="markers",
        marker=dict(color="red", size=10, symbol="triangle-down"),
        name="Sell"
    ))

    fig.update_layout(title="📈 Price with EMA + Signals",
                      xaxis_title="Time", yaxis_title="Price",
                      xaxis_rangeslider_visible=False,
                      height=600)
    return fig

def plot_rsi(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["RSI"], line=dict(color="blue")))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(title="📉 RSI", height=300)
    return fig

while True:
    df = load_data()

    if df.empty:
        st.warning("⏳ Waiting for Spark to write streaming data...")
    else:
        df = compute_indicators(df)

        # Plot charts
        price_fig = plot_price_chart(df)
        rsi_fig = plot_rsi(df)

        # Layout
        st.plotly_chart(price_fig, use_container_width=True)
        st.plotly_chart(rsi_fig, use_container_width=True)

        with st.expander("📄 Latest Data"):
            st.dataframe(df.sort_values("datetime", ascending=False).tail(20))

    time.sleep(REFRESH_INTERVAL)