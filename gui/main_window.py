
import tkinter as tk
from tkinter import ttk, messagebox
from gui.dashboard import Dashboard
from gui.strategy_config import StrategyConfig
from gui.chart_view import ChartView
import asyncio

class MainWindow:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("Bot de Trading Crypto")
        self.root.geometry("1024x768")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        self.dashboard = Dashboard(self.notebook, self.engine)
        self.strategy_config = StrategyConfig(self.notebook, self.engine)
        self.chart_view = ChartView(self.notebook, self.engine)

        self.notebook.add(self.dashboard.frame, text="Dashboard")
        self.notebook.add(self.strategy_config.frame, text="Configuration des Stratégies")
        self.notebook.add(self.chart_view.frame, text="Graphiques")

        self.create_menu()
        self.create_toolbar()
        self.update_loop()
        self.update_button_states()

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.start_button = ttk.Button(toolbar, text="Démarrer", command=self.start_trading_wrapper)
        self.start_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.stop_button = ttk.Button(toolbar, text="Arrêter", command=self.stop_trading_wrapper)
        self.stop_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.refresh_button = ttk.Button(toolbar, text="Rafraîchir", command=self.refresh_data)
        self.refresh_button.pack(side=tk.LEFT, padx=2, pady=2)

    def start_trading_wrapper(self):
        asyncio.create_task(self.start_trading())

    def stop_trading_wrapper(self):
        asyncio.create_task(self.stop_trading())

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self.root.quit)

        trading_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trading", menu=trading_menu)
        trading_menu.add_command(label="Démarrer", command=self.start_trading_wrapper)
        trading_menu.add_command(label="Arrêter", command=self.stop_trading_wrapper)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    async def start_trading(self):
        try:
            await self.engine.start()
            messagebox.showinfo("Trading", "Le trading a démarré.")
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de démarrer le trading: {str(e)}")

    async def stop_trading(self):
        try:
            await self.engine.stop()
            messagebox.showinfo("Trading", "Le trading a été arrêté.")
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'arrêter le trading: {str(e)}")

    def refresh_data(self):
        try:
            self.engine.refresh_data()
            self.dashboard.update()
            self.chart_view.update()
            messagebox.showinfo("Rafraîchissement", "Les données ont été mises à jour.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de rafraîchir les données: {str(e)}")

    def update_button_states(self):
        if self.engine.running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("À propos")
        about_window.geometry("300x200")
        
        label = tk.Label(about_window, text="Bot de Trading Crypto\nVersion 1.0\n\nDéveloppé par OpenAI Assistant")
        label.pack(expand=True)

    def run(self):
        self.root.mainloop()

    def update_loop(self):
        self.dashboard.update()
        self.chart_view.update()
        self.update_button_states()
        self.root.after(1000, self.update_loop)  # Update every second
