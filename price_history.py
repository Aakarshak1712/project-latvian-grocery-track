import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import pandas as pd

class PriceHistoryViewer:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Product selection
        selection_frame = ttk.Frame(self.frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Select Product:").pack(side=tk.LEFT)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(selection_frame, textvariable=self.product_var)
        self.product_combo.pack(side=tk.LEFT, padx=5)
        
        # Time range selection
        range_frame = ttk.Frame(self.frame)
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(range_frame, text="Time Range:").pack(side=tk.LEFT)
        self.range_var = tk.StringVar(value="1 Month")
        ranges = ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"]
        range_combo = ttk.Combobox(range_frame, values=ranges, textvariable=self.range_var)
        range_combo.pack(side=tk.LEFT, padx=5)
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind events
        self.product_combo.bind('<<ComboboxSelected>>', self.update_graph)
        range_combo.bind('<<ComboboxSelected>>', self.update_graph)
        
    def load_products(self):
        """Load available products into combobox"""
        # Get products from database
        products = self.db_manager.get_all_products()
        self.product_combo['values'] = [f"{p['name']} ({p['store']})" for p in products]
        if products:
            self.product_combo.current(0)
            
    def update_graph(self, event=None):
        """Update the price history graph"""
        self.ax.clear()
        
        # Get selected product
        selected = self.product_var.get()
        if not selected:
            return
            
        # Parse product name and store
        product_name = selected.split(" (")[0]
        store = selected.split("(")[1].rstrip(")")
        
        # Get time range
        range_text = self.range_var.get()
        if range_text == "1 Week":
            days = 7
        elif range_text == "1 Month":
            days = 30
        elif range_text == "3 Months":
            days = 90
        elif range_text == "6 Months":
            days = 180
        else:  # 1 Year
            days = 365
            
        # Get price history data
        history = self.db_manager.get_product_price_history_by_name(product_name, store)
        
        if history:
            # Convert to pandas DataFrame
            df = pd.DataFrame(history, columns=['price', 'date'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter by time range
            start_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= start_date]
            
            # Plot data
            self.ax.plot(df['date'], df['price'], marker='o')
            self.ax.set_title(f"Price History: {product_name}")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Price (€)")
            self.ax.grid(True)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Adjust layout to prevent label cutoff
            self.figure.tight_layout()
            
        # Update canvas
        self.canvas.draw()
        
    def show(self):
        """Show the price history viewer"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_products()
        self.update_graph()
        
    def hide(self):
        """Hide the price history viewer"""
        self.frame.pack_forget()
