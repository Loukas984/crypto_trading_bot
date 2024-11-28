
from collections import OrderedDict

class DataCache:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.cache = OrderedDict()

    def add(self, symbol, data):
        if symbol not in self.cache:
            self.cache[symbol] = []
        self.cache[symbol].append(data)
        self.cache.move_to_end(symbol)
        if len(self.cache[symbol]) > self.max_size:
            self.cache[symbol].pop(0)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get(self, symbol, limit=None):
        if symbol not in self.cache:
            return []
        data = self.cache[symbol]
        if limit is not None:
            return data[-limit:]
        return data

    def clear(self):
        self.cache.clear()
