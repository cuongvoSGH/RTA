# Libraries import
import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import plotly.graph_objects as go
from pyspark.sql.types import StructType, DoubleType, StructField, LongType
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from  pyspark.sql.functions import *

# Define the Spark session and schema
spark = SparkSession.builder.appName("TradingDashboard").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
  StructField('timestamp', LongType()),
  StructField('open', DoubleType()),
  StructField('high', DoubleType()),
  StructField('low', DoubleType()),
  StructField('close', DoubleType()),
  StructField('volume', DoubleType())
])

# Streamlit app
st.set_page_config(page_title="📈 Real-Time Trading Dashboard", layout="wide")
st.title("📊 Real-Time Trading with Candlestick, EMA, RSI & Signals")

DATA_DIR = "/tmp/stream_output/"
# Refresh every 65 seconds
REFRESH_INTERVAL = 65

chart_placeholder = st.empty()

def load_data():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".parquet")]
    if not files:
        return spark.createDataFrame([], schema)

    df = spark.read.parquet(f"{DATA_DIR}*.parquet")
    df = df.dropDuplicates().orderBy("timestamp")
    return df

def compute_indicators(df):
    window_spec_20 = Window.orderBy("datetime").rowsBetween(-19, 0)  
    window_spec_50 = Window.orderBy("datetime").rowsBetween(-49, 0)

    df = df.withColumn("MA20", avg("close").over(window_spec_20))
    df = df.withColumn("MA50", avg("close").over(window_spec_50))

    window_spec = Window.orderBy("datetime")
    df = df.withColumn("prev_close", lag("close", 1).over(window_spec))
    df = df.withColumn("change", col("close") - col("prev_close"))
    df = df.withColumn("gain", when(col("change") > 0, col("change")).otherwise(0))
    df = df.withColumn("loss", when(col("change") < 0, -col("change")).otherwise(0))

    rsi_window = Window.orderBy("datetime").rowsBetween(-13, 0)
    df = df.withColumn("avg_gain", avg("gain").over(rsi_window))
    df = df.withColumn("avg_loss", avg("loss").over(rsi_window))

    df = df.withColumn("rs", col("avg_gain") / col("avg_loss"))
    df = df.withColumn("RSI", 100 - (100 / (1 + col("rs"))))

    df = df.withColumn("prev_MA20", lag("MA20", 1).over(window_spec))
    df = df.withColumn("prev_MA50", lag("MA50", 1).over(window_spec))

    df = df.withColumn("ma_crossover_up", 
                   when((col("prev_MA20") < col("prev_MA50")) & (col("MA20") > col("MA50")), lit(1)).otherwise(0))

    df = df.withColumn("ma_crossover_down", 
                   when((col("prev_MA20") > col("prev_MA50")) & (col("MA20") < col("MA50")), lit(1)).otherwise(0))
    
    df = df.withColumn("signal", 
                    when((col("RSI") > 50) & (col("ma_crossover_up") == 1) & (col("RSI") < 70), lit("BUY"))
                    .when((col("RSI") > 70) & (col("ma_crossover_down") == 1), lit("SELL"))
                    .otherwise("HOLD")
                    )                       
    df = df.drop("prev_close", "gain", "loss", "avg_gain", "avg_loss", "rs", "change", "ma_crossover_down", "ma_crossover_up", "prev_MA20", "prev_MA50")
    df = df.orderBy(col("timestamp").desc()).limit(240)

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

    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["MA20"],
        line=dict(color="green", width=2),
        name="MA_20"
    ))

    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["MA50"],
        line=dict(color="red", width=2),
        name="MA_50"
    ))

    fig.update_layout(title="📈 Price with MA + Signals",
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

def plot_total_asset(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["total_value"], line=dict(color="blue")))
    fig.add_hline(y=10000, line_dash="dash", line_color="red")
    fig.update_layout(title="📉 Total Asset", height=300)
    return fig

crypto = 0
budget = 10000

def trading_strategy(df):
    global budget, crypto
    latest = df.iloc[0]
    price = latest["close"]
    signal = latest["signal"]
    datetime_str = latest["datetime"]

    if signal == "BUY" and crypto == 0:
        amount = budget // price
        crypto += amount
        budget -= amount * price
        action = "BUY"
    elif signal == "SELL" and crypto > 0:
        amount = crypto
        crypto -= amount
        budget += amount * price
        action = "SELL"
    else:
        action = "HOLD"

    log = pd.DataFrame([{   "timestamp": datetime_str, 
                            "action": action,
                            "crypto": crypto,
                            "price": price,
                            "budget": budget,   
                            "total_value": budget + (crypto * price)                        
                        }])
    
    return log

price_chart_container = st.empty()
rsi_chart_container = st.empty()
lastest_container = st.empty()
pnl = st.empty()

portfolio_log = pd.DataFrame(columns=["timestamp", "action", "crypto", "price", "budget", "total_value"])

while True:
    df = load_data()

    if df.count() == 0:
        st.warning("⏳ Waiting for Spark to write streaming data...")
    else:
        df = compute_indicators(df)
        df = df.toPandas()

        log = trading_strategy(df)
        portfolio_log = pd.concat([portfolio_log, log], ignore_index=True)

        # Plot charts
        price_fig = plot_price_chart(df)
        pnl_fig = plot_total_asset(portfolio_log)
        rsi_fig = plot_rsi(df)

        # Layout
        price_chart_container.plotly_chart(price_fig, use_container_width=True)
        pnl.plotly_chart(pnl_fig, use_container_width=True)
        rsi_chart_container.plotly_chart(rsi_fig, use_container_width=True)

        with lastest_container.expander("📄 Latest Data"):
            lastest_container.dataframe(df.sort_values("datetime", ascending=False).tail(10))

    time.sleep(REFRESH_INTERVAL)