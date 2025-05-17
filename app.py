import streamlit as st
import pandas as pd
import time
import os

st.title("📈 Live Trading Feed (EMA/RSI Ready)")

DATA_DIR = "/tmp/stream_output/"

# Refresh every 5 seconds
REFRESH_INTERVAL = 65

