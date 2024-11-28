
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Dashboard:
    def __init__(self, parent, engine):
        self.engine = engine
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        # Informations générales
        general_frame = ttk.LabelFrame(self.frame, text="Informations générales")
        general_frame.pack(padx=10, pady=10, fill='x')

        self.status_label = ttk.Label(general_frame, text="Statut: Arrêté")
        self.status_label.pack(anchor='w')

        self.balance_label = ttk.Label(general_frame, text="Solde total: 0 USDT")
        self.balance_label.pack(anchor='w')

        # Performances
        performance_frame = ttk.LabelFrame(self.frame, text="Performances")
        performance_frame.pack(padx=10, pady=10, fill='x')

        self.profit_loss_label = ttk.Label(performance_frame, text="Profit/Perte: 0 USDT")
        self.profit_loss_label.pack(anchor='w')

        self.roi_label = ttk.Label(performance_frame, text="ROI: 0%")
        self.roi_label.pack(anchor='w')

        self.sharpe_ratio_label = ttk.Label(performance_frame, text="Sharpe Ratio: 0")
        self.sharpe_ratio_label.pack(anchor='w')

        self.max_drawdown_label = ttk.Label(performance_frame, text="Max Drawdown: 0%")
        self.max_drawdown_label.pack(anchor='w')

        # Graphique d'évolution du solde
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10, fill='both', expand=True)

        # Positions ouvertes
        positions_frame = ttk.LabelFrame(self.frame, text="Positions ouvertes")
        positions_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.positions_tree = ttk.Treeview(positions_frame, columns=('Symbol', 'Amount', 'Entry Price', 'Current Price', 'PNL'), show='headings')
        self.positions_tree.heading('Symbol', text='Symbole')
        self.positions_tree.heading('Amount', text='Montant')
        self.positions_tree.heading('Entry Price', text="Prix d'entrée")
        self.positions_tree.heading('Current Price', text='Prix actuel')
        self.positions_tree.heading('PNL', text='PNL')
        self.positions_tree.pack(fill='both', expand=True)

        # Dernières transactions
        transactions_frame = ttk.LabelFrame(self.frame, text="Dernières transactions")
        transactions_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.transactions_tree = ttk.Treeview(transactions_frame, columns=('Time', 'Symbol', 'Type', 'Amount', 'Price'), show='headings')
        self.transactions_tree.heading('Time', text='Heure')
        self.transactions_tree.heading('Symbol', text='Symbole')
        self.transactions_tree.heading('Type', text='Type')
        self.transactions_tree.heading('Amount', text='Montant')
        self.transactions_tree.heading('Price', text='Prix')
        self.transactions_tree.pack(fill='both', expand=True)

    def update(self):
        # Mettre à jour les informations générales
        self.status_label.config(text=f"Statut: {'En cours' if self.engine.running else 'Arrêté'}")
        self.balance_label.config(text=f"Solde total: {self.engine.portfolio.get_total_value():.2f} USDT")

        # Mettre à jour les performances
        metrics = self.engine.get_performance_metrics()
        self.profit_loss_label.config(text=f"Profit/Perte: {metrics['total_return']:.2f} USDT")
        self.roi_label.config(text=f"ROI: {metrics['roi']:.2f}%")
        self.sharpe_ratio_label.config(text=f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        self.max_drawdown_label.config(text=f"Max Drawdown: {metrics['max_drawdown']:.2f}%")

        # Mettre à jour le graphique
        self.ax.clear()
        self.ax.plot(self.engine.portfolio.value_history)
        self.ax.set_title("Évolution du solde total")
        self.ax.set_xlabel("Temps")
        self.ax.set_ylabel("Solde (USDT)")
        self.canvas.draw()

        # Mettre à jour les positions ouvertes
        self.positions_tree.delete(*self.positions_tree.get_children())
        for symbol, position in self.engine.portfolio.positions.items():
            current_price = self.engine.exchange_data.get_latest_price(symbol)
            pnl = (current_price - position['entry_price']) * position['amount']
            self.positions_tree.insert('', 'end', values=(symbol, position['amount'], position['entry_price'], current_price, f"{pnl:.2f}"))

        # Mettre à jour les dernières transactions
        self.transactions_tree.delete(*self.transactions_tree.get_children())
        for transaction in self.engine.portfolio.trade_history[-10:]:  # Afficher les 10 dernières transactions
            self.transactions_tree.insert('', 0, values=(transaction['timestamp'], transaction['symbol'], transaction['type'], transaction['amount'], transaction['price']))
