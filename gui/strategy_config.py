
import tkinter as tk
from tkinter import ttk, messagebox

class StrategyConfig:
    def __init__(self, parent, engine):
        self.engine = engine
        self.frame = ttk.Frame(parent)
        self.strategy_params = {}
        self.create_widgets()

    def create_widgets(self):
        # Strategy selection
        strategy_frame = ttk.Frame(self.frame)
        strategy_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(strategy_frame, text="Select Strategy:").pack(side='left')
        self.strategy_combo = ttk.Combobox(strategy_frame, values=["SentimentMomentumStrategy", "GridTradingStrategy", "BreakoutStrategy"])
        self.strategy_combo.pack(side='left', padx=(10, 0))
        self.strategy_combo.bind("<<ComboboxSelected>>", self.update_strategy_params)

        # Strategy activation
        self.strategy_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(strategy_frame, text="Active", variable=self.strategy_active).pack(side='left', padx=(10, 0))

        # Strategy parameters
        self.param_frame = ttk.Frame(self.frame)
        self.param_frame.pack(padx=10, pady=10, fill='x')

        # Risk management parameters
        risk_frame = ttk.LabelFrame(self.frame, text="Risk Management")
        risk_frame.pack(padx=10, pady=10, fill='x')

        self.risk_params = {
            "Max Position Size (%)": 1,
            "Stop Loss (%)": 5,
            "Take Profit (%)": 10,
            "Max Open Positions": 3,
            "Max Daily Trades": 10,
        }

        for param, value in self.risk_params.items():
            self.add_param(risk_frame, param, str(value))

        # Global parameters
        global_frame = ttk.LabelFrame(self.frame, text="Global Parameters")
        global_frame.pack(padx=10, pady=10, fill='x')

        self.global_params = {
            "Trading Frequency (seconds)": 60,
            "Update Interval (seconds)": 1,
            "Strategy Interval (seconds)": 5,
            "Optimize Parameters": False
        }

        for param, value in self.global_params.items():
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(global_frame, text=param, variable=var).pack(anchor='w')
                self.global_params[param] = var
            else:
                self.add_param(global_frame, param, str(value))

        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)

        save_button = ttk.Button(button_frame, text="Save Configuration", command=self.save_config)
        save_button.pack(side='left', padx=(0, 10))

        load_button = ttk.Button(button_frame, text="Load Configuration", command=self.load_config)
        load_button.pack(side='left', padx=(0, 10))

        reset_button = ttk.Button(button_frame, text="Reset to Default", command=self.reset_to_default)
        reset_button.pack(side='left')

        self.update_strategy_params()
        self.load_config()  # Load the current configuration when initializing

    def reset_to_default(self):
        self.update_strategy_params()
        for param, widget in self.risk_params.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, str(self.risk_params[param]))
        for param, widget in self.global_params.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, str(self.global_params[param]))
            elif isinstance(widget, tk.BooleanVar):
                widget.set(self.global_params[param])
        messagebox.showinfo("Reset", "Parameters have been reset to their default values.")

    def update_strategy_params(self, event=None):
        # Clear existing parameter widgets
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        strategy = self.strategy_combo.get()
        if strategy == "SentimentMomentumStrategy":
            self.strategy_params = {
                "RSI Period": 14,
                "RSI Overbought": 75,
                "RSI Oversold": 25,
                "MACD Fast": 12,
                "MACD Slow": 26,
                "MACD Signal": 9,
                "Sentiment Threshold": 0.15
            }
        elif strategy == "GridTradingStrategy":
            self.strategy_params = {
                "Grid Levels": 5,
                "Grid Size (%)": 2,
                "Total Investment (USDT)": 1000
            }
        elif strategy == "BreakoutStrategy":
            self.strategy_params = {
                "Lookback Period": 20,
                "Breakout Threshold": 2.5
            }

        for param, value in self.strategy_params.items():
            self.add_param(self.param_frame, param, str(value))

    def add_param(self, parent, label, default_value):
        param_frame = ttk.Frame(parent)
        param_frame.pack(fill='x', pady=5)
        ttk.Label(param_frame, text=label).pack(side='left')
        entry = ttk.Entry(param_frame, textvariable=tk.StringVar(value=default_value))
        entry.pack(side='right')
        return entry

    def save_config(self):
        strategy = self.strategy_combo.get()
        params = {}
        for widget in self.param_frame.winfo_children():
            label = widget.winfo_children()[0].cget("text")
            value = widget.winfo_children()[1].get()
            params[label] = float(value)
        
        risk_params = {}
        for param, widget in self.risk_params.items():
            if isinstance(widget, ttk.Entry):
                risk_params[param] = float(widget.get())
        
        global_params = {}
        for param, widget in self.global_params.items():
            if isinstance(widget, ttk.Entry):
                global_params[param] = float(widget.get())
            elif isinstance(widget, tk.BooleanVar):
                global_params[param] = widget.get()
        
        config = {
            "strategy": strategy,
            "active": self.strategy_active.get(),
            "strategy_params": params,
            "risk_params": risk_params,
            "global_params": global_params
        }
        
        try:
            self.engine.update_config(config)
            messagebox.showinfo("Configuration Saved", f"Configuration for {strategy} has been updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update configuration: {str(e)}")

    def load_config(self):
        config = self.engine.get_config()
        if config:
            self.strategy_combo.set(config["strategy"])
            self.strategy_active.set(config["active"])
            self.update_strategy_params()
            
            for param, value in config["strategy_params"].items():
                for widget in self.param_frame.winfo_children():
                    if widget.winfo_children()[0].cget("text") == param:
                        widget.winfo_children()[1].delete(0, tk.END)
                        widget.winfo_children()[1].insert(0, str(value))
            
            for param, value in config["risk_params"].items():
                if param in self.risk_params:
                    self.risk_params[param].delete(0, tk.END)
                    self.risk_params[param].insert(0, str(value))
            
            for param, value in config["global_params"].items():
                if param in self.global_params:
                    if isinstance(self.global_params[param], ttk.Entry):
                        self.global_params[param].delete(0, tk.END)
                        self.global_params[param].insert(0, str(value))
                    elif isinstance(self.global_params[param], tk.BooleanVar):
                        self.global_params[param].set(value)
