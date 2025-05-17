from binance.client import Client
from kafka import KafkaProducer
import json
import time

#  using API keys
api_key = 'giuBTEvNmtfaSuPpCZfmF7uXzRYfKzk7sAwC4ezjB3KbfGLS30UnQMDxcxs15WSB'
api_secret = 'SOmHSWFBuTa20grpf8r87c9qm9tym1oHkjktpu4mIwB9L08qvXW4W9HK7FSt1y6o'

client = Client(api_key, api_secret)

def get_historical_data(symbol, interval, lookback):
    """
    Fetch historical data from Binance for a given symbol and interval.
    :param symbol: The trading pair symbol (e.g., 'BTCUSDT').
    :param interval: The time interval for the data (e.g., '1m', '5m', '1h', '1d').
    :param lookback: The lookback period for the data (e.g., '1 day ago UTC', '1 hour ago UTC').
    """
    try:
        klines = client.get_historical_klines(symbol, interval, lookback)
        return klines
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Replace with your Kafka broker if different
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize to JSON bytes
)

topic = 'StreamQuant'

i = 0

keys = ["timestamp", "open", "high", "low", "close", "volume"]

while True:
    i +=1
    binance_data = get_historical_data('BTCUSDT', '1m', '1 minute ago UTC')
    values = [int(binance_data[0][0])] + [float(x) for x in binance_data[0][1:]]
    data_dict = dict(zip(keys, values))
    producer.send(topic, value=data_dict)
    print(f"Sent {topic} - {i}: {data_dict}")
    time.sleep(60)  # Sleep for 1 minute before fetching the next data point