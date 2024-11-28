
import pandas as pd
from typing import Dict, Any
import os
import json
from datetime import datetime, timedelta

class HistoricalData:
    def __init__(self, exchange_handler):
        self.exchange_handler = exchange_handler
        self.data = {}

    async def fetch_historical_data(self, symbol: str, timeframe: str, since: int = None, limit: int = None):
        ohlcv = await self.exchange_handler.get_ohlcv(symbol, timeframe, since, limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        self.data[f"{symbol}_{timeframe}"] = df
        return df

    def get_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        return self.data.get(f"{symbol}_{timeframe}", pd.DataFrame())

    async def update_data(self, symbol: str, timeframe: str):
        existing_data = self.get_data(symbol, timeframe)
        if not existing_data.empty:
            since = int(existing_data.index[-1].timestamp() * 1000)
        else:
            since = None
        new_data = await self.fetch_historical_data(symbol, timeframe, since)
        updated_data = pd.concat([existing_data, new_data]).drop_duplicates().sort_index()
        self.data[f"{symbol}_{timeframe}"] = updated_data

    def get_missing_data_ranges(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> list:
        data = self.get_data(symbol, timeframe)
        if data.empty:
            return [(start_date, end_date)]

        missing_ranges = []
        current_date = start_date

        while current_date < end_date:
            if current_date not in data.index:
                range_start = current_date
                while current_date < end_date and current_date not in data.index:
                    current_date += timedelta(minutes=1)  # Assume 1-minute timeframe, adjust as needed
                missing_ranges.append((range_start, current_date))
            else:
                current_date += timedelta(minutes=1)

        return missing_ranges

    def get_data_info(self) -> Dict[str, Any]:
        info = {}
        for key, data in self.data.items():
            if not data.empty:
                info[key] = {
                    "start_date": data.index[0].strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": data.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
                    "num_records": len(data)
                }
        return info
