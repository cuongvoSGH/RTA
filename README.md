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
```

## 🧰 Tech Stack

| Component  | Technology          |
| ---------- | --------------------|
| API        | Binance Testnet API |
| Stream     | Apache Kafka        |
| Processing | Apache Spark        |
| Dashboard  | Streamlit           |
| Language   | Python, Spark       |

## 🧪 Features

* Real-time price and volume tracking of selected crypto pairs
* Provide Trading Signal
* Live dashboard to visualize market activity

## ⚙️ How to Run

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/realtime-crypto-analysis.git
cd realtime-crypto-analysis
```

2. **Start Kafka**

Make sure Zookeeper and Kafka services are running. Example using Docker:

```bash
$ cd /usr/local/kafka 
$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic StreamQuant
$ bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

3. **Run Kafka Producer (Binance API)**

```bash
$ python3 binance_producer.py
```

4. **Start Spark Streaming**

```bash
$ spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 ~/Realtime_Analytics/quant_consumer.py
```

5. **Launch Streamlit Dashboard**

```bash
streamlit run app.py
```

## 📁 Project Structure

```
.
├── .gitignore              
├── binance_producer.py     # Pulls real-time data from Binance and sends to Kafka
├── quant_consumer.py       # Spark job to process the stream
├── app.py                  # Streamlit UI for visualization
├── requirements.txt        # Python dependencies
├── RTA_final_project.html  # Jupyter notebook to explain about the task
└── README.md
```
