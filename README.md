# RTA
# 📈 Real-Time Crypto Market Analysis

This project performs real-time data streaming, processing, and visualization of cryptocurrency market data using:

* 🛰️ **Binance API** for live market data
* ⚡ **Apache Kafka** for real-time data ingestion
* 🔥 **Apache Spark (Structured Streaming)** for processing
* 🧠 **(Optional)** Machine learning for anomaly detection
* 🌐 **Streamlit** for interactive data visualization

## 🚀 Project Overview

The goal of this project is to build a real-time analytics pipeline that can detect and visualize anomalies or unusual patterns in the cryptocurrency market (e.g., Bitcoin, Ethereum) by streaming live data from Binance.

## 📊 Architecture

```
Binance API → Kafka Producer → Kafka Topic → Spark Structured Streaming → Streamlit Dashboard
                                            ↓
                                   (Optional ML Model)
```

## 🧰 Tech Stack

| Component  | Technology        |
| ---------- | ----------------- |
| API        | Binance WebSocket |
| Stream     | Apache Kafka      |
| Processing | Apache Spark      |
| Dashboard  | Streamlit         |
| Language   | Python            |

## 🧪 Features

* Real-time price and volume tracking of selected crypto pairs
* Anomaly detection based on statistical or ML models *(optional)*
* Live dashboard to visualize market activity
* Scalable architecture for handling high-frequency data

## ⚙️ How to Run

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/realtime-crypto-analysis.git
cd realtime-crypto-analysis
```

2. **Start Kafka**

Make sure Zookeeper and Kafka services are running. Example using Docker:

```bash
docker-compose up
```

3. **Run Kafka Producer (Binance API)**

```bash
python kafka_producer.py
```

4. **Start Spark Streaming**

```bash
spark-submit spark_streaming.py
```

5. **Launch Streamlit Dashboard**

```bash
streamlit run dashboard.py
```

## 📁 Project Structure

```
.
├── kafka_producer.py       # Pulls real-time data from Binance and sends to Kafka
├── spark_streaming.py      # Spark job to process the stream
├── dashboard.py            # Streamlit UI for visualization
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Setup for Kafka and Zookeeper
└── README.md
```
