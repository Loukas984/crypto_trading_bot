
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ChartView:
    def __init__(self, parent, engine):
        self.engine = engine
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        # Sélection du symbole
        symbol_frame = ttk.Frame(self.frame)
        symbol_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(symbol_frame, text="Symbole:").pack(side='left')
        self.symbol_var = tk.StringVar()
        self.symbol_combobox = ttk.Combobox(symbol_frame, textvariable=self.symbol_var)
        self.symbol_combobox['values'] = self.engine.get_available_symbols()
        self.symbol_combobox.pack(side='left', padx=5)
        self.symbol_combobox.bind('<<ComboboxSelected>>', self.on_symbol_selected)

        # Graphique
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_symbol_selected(self, event):
        self.update_chart()

    def update_chart(self):
        symbol = self.symbol_var.get()
        if not symbol:
            return

        self.ax.clear()
        
        # Récupérer les données historiques
        historical_data = self.engine.get_historical_data(symbol)
        
        if historical_data is not None and len(historical_data) > 0:
            # Tracer le graphique des prix
            dates = [candle['timestamp'] for candle in historical_data]
            closes = [candle['close'] for candle in historical_data]
            self.ax.plot(dates, closes, label='Prix de clôture')
            
            # Ajouter les moyennes mobiles
            ma20 = self.calculate_ma(closes, 20)
            ma50 = self.calculate_ma(closes, 50)
            self.ax.plot(dates[-len(ma20):], ma20, label='MA20')
            self.ax.plot(dates[-len(ma50):], ma50, label='MA50')
            
            # Ajouter les indicateurs techniques (exemple avec RSI)
            rsi = self.calculate_rsi(closes)
            ax2 = self.ax.twinx()
            ax2.plot(dates[-len(rsi):], rsi, color='orange', label='RSI')
            ax2.set_ylim(0, 100)
            ax2.set_ylabel('RSI')
            
            # Ajouter les positions ouvertes
            for position in self.engine.get_open_positions(symbol):
                self.ax.axhline(y=position['entry_price'], color='g', linestyle='--')
            
            self.ax.set_title(f"Graphique {symbol}")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Prix")
            self.ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            self.canvas.draw()

    def calculate_ma(self, data, window):
        return [sum(data[i:i+window]) / window for i in range(len(data) - window + 1)]

    def calculate_rsi(self, prices, period=14):
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        seed = sum(deltas[:period]) / period
        up = [max(d, 0) for d in deltas]
        down = [-min(d, 0) for d in deltas]
        rs = self.calculate_ma(up, period)[0] / self.calculate_ma(down, period)[0]
        return [100 - (100 / (1 + rs))]

    def update(self):
        self.update_chart()
