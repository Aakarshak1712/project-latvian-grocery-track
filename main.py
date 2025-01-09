import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from scrapers.rimi_scraper import RimiScraper
from scrapers.maxima_scraper import MaximaScraper
from scrapers.lidl_scraper import LidlScraper
from database.db_manager import DatabaseManager
from utils.price_history import PriceHistoryViewer
from utils.preferences import PreferencesManager
from utils.export import ShoppingListExporter
from tkinter import filedialog, messagebox

class GroceryGuruApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Guru Latvia")
        self.root.geometry("1024x768")
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.preferences = PreferencesManager()
        self.exporter = ShoppingListExporter(self.db_manager)
        self.scrapers = {
            'Rimi': RimiScraper(),
            'Maxima': MaximaScraper(),
            'Lidl': LidlScraper()
        }
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure(".", font=('Helvetica', 10))
        self.style.configure("Title.TLabel", font=('Helvetica', 16, 'bold'))
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create menu
        self.create_menu()
        
        # Create header
        header = ttk.Label(
            self.main_container, 
            text="Grocery Guru Latvia", 
            style="Title.TLabel"
        )
        header.grid(row=0, column=0, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup tabs
        self.setup_price_comparison_tab()
        self.setup_shopping_list_tab()
        self.setup_discounts_tab()
        self.setup_preferences_tab()
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Shopping List", command=self.export_shopping_list)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Price History", command=self.show_price_history)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Preferences", command=self.show_preferences)
        tools_menu.add_command(label="Price Alerts", command=self.manage_price_alerts)
        
    def setup_price_comparison_tab(self):
        # Search frame
        search_frame = ttk.Frame(self.price_comparison_frame)
        search_frame.grid(row=0, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        ttk.Label(search_frame, text="Search Products:").grid(row=0, column=0)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_products).grid(row=0, column=2)
        
        # Results table
        columns = ('Product', 'Rimi', 'Maxima', 'Lidl')
        self.price_tree = ttk.Treeview(self.price_comparison_frame, columns=columns, show='headings')
        
        for col in columns:
            self.price_tree.heading(col, text=col)
            self.price_tree.column(col, width=150)
            
        self.price_tree.grid(row=1, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        # Price history button
        ttk.Button(
            self.price_comparison_frame,
            text="View Price History",
            command=self.show_price_history
        ).grid(row=2, column=0, pady=5)
        
    def search_products(self):
        query = self.search_entry.get()
        if not query:
            return
            
        # Clear existing items
        for item in self.price_tree.get_children():
            self.price_tree.delete(item)
            
        # Search across all stores
        all_products = {}
        for store_name, scraper in self.scrapers.items():
            products = scraper.search_product(query)
            for product in products:
                name = product['name']
                if name not in all_products:
                    all_products[name] = {'Product': name, 'Rimi': '-', 'Maxima': '-', 'Lidl': '-'}
                all_products[name][store_name] = f"€{product['price']:.2f}"
                
                # Save to database
                self.db_manager.add_product(
                    name=name,
                    store=store_name,
                    price=product['price'],
                    url=product.get('url')
                )
                
        # Update treeview
        for product_data in all_products.values():
            self.price_tree.insert('', 'end', values=(
                product_data['Product'],
                product_data['Rimi'],
                product_data['Maxima'],
                product_data['Lidl']
            ))
            
    def show_price_history(self):
        # Get selected item
        selected = self.price_tree.selection()
        if not selected:
            return
            
        # Create price history window
        history_window = tk.Toplevel(self.root)
        history_window.title("Price History")
        history_window.geometry("800x600")
        
        # Create and show price history viewer
        viewer = PriceHistoryViewer(history_window, self.db_manager)
        viewer.show()
        
    def setup_shopping_list_tab(self):
        # Add item frame
        add_frame = ttk.Frame(self.shopping_list_frame)
        add_frame.grid(row=0, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        ttk.Label(add_frame, text="Add Item:").grid(row=0, column=0)
        ttk.Entry(add_frame).grid(row=0, column=1, padx=5)
        ttk.Button(add_frame, text="Add").grid(row=0, column=2)
        
        # Shopping list
        columns = ('Item', 'Quantity', 'Estimated Price')
        self.shopping_tree = ttk.Treeview(self.shopping_list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.shopping_tree.heading(col, text=col)
            self.shopping_tree.column(col, width=150)
            
        self.shopping_tree.grid(row=1, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
    def setup_discounts_tab(self):
        # Store selection
        store_frame = ttk.Frame(self.discounts_frame)
        store_frame.grid(row=0, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        ttk.Label(store_frame, text="Select Store:").grid(row=0, column=0)
        store_combo = ttk.Combobox(store_frame, values=['All Stores', 'Rimi', 'Maxima', 'Lidl'])
        store_combo.grid(row=0, column=1, padx=5)
        store_combo.set('All Stores')
        
        # Discounts list
        columns = ('Product', 'Store', 'Original Price', 'Discount Price', 'Valid Until')
        self.discounts_tree = ttk.Treeview(self.discounts_frame, columns=columns, show='headings')
        
        for col in columns:
            self.discounts_tree.heading(col, text=col)
            self.discounts_tree.column(col, width=120)
            
        self.discounts_tree.grid(row=1, column=0, pady=10, padx=10, sticky=(tk.W, tk.E))

    def setup_preferences_tab(self):
        """Setup preferences tab"""
        self.preferences_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preferences_frame, text="Preferences")
        
        # Favorite stores
        store_frame = ttk.LabelFrame(self.preferences_frame, text="Favorite Stores")
        store_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for store in self.scrapers.keys():
            var = tk.BooleanVar(value=store in self.preferences.get_favorite_stores())
            cb = ttk.Checkbutton(
                store_frame,
                text=store,
                variable=var,
                command=lambda s=store: self.preferences.toggle_favorite_store(s)
            )
            cb.pack(anchor=tk.W, padx=5, pady=2)
            
        # Notification settings
        notif_frame = ttk.LabelFrame(self.preferences_frame, text="Notifications")
        notif_frame.pack(fill=tk.X, padx=10, pady=5)
        
        enable_var = tk.BooleanVar(value=self.preferences.get_preference('notification_enabled'))
        ttk.Checkbutton(
            notif_frame,
            text="Enable Price Alert Notifications",
            variable=enable_var,
            command=lambda: self.preferences.set_preference('notification_enabled', enable_var.get())
        ).pack(anchor=tk.W, padx=5, pady=2)
        
    def export_shopping_list(self):
        """Export current shopping list to PDF"""
        # Get current shopping list ID (you'll need to track this)
        list_id = 1  # For demonstration, you should track the active list ID
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Shopping List"
        )
        
        if file_path:
            if self.exporter.export_to_pdf(list_id, file_path):
                messagebox.showinfo(
                    "Success",
                    f"Shopping list exported to {file_path}"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to export shopping list"
                )
                
    def manage_price_alerts(self):
        """Open price alert management window"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Manage Price Alerts")
        alert_window.geometry("400x500")
        
        # Product selection
        product_frame = ttk.Frame(alert_window)
        product_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(product_frame, text="Product:").pack(side=tk.LEFT)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(
            product_frame,
            textvariable=product_var,
            values=[p['name'] for p in self.db_manager.get_all_products()]
        )
        product_combo.pack(side=tk.LEFT, padx=5)
        
        # Price entry
        price_frame = ttk.Frame(alert_window)
        price_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(price_frame, text="Max Price (€):").pack(side=tk.LEFT)
        price_var = tk.StringVar()
        price_entry = ttk.Entry(price_frame, textvariable=price_var)
        price_entry.pack(side=tk.LEFT, padx=5)
        
        # Add button
        def add_alert():
            try:
                product = product_var.get()
                price = float(price_var.get())
                self.preferences.add_price_alert(product, price)
                update_alerts_list()
                price_var.set("")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price")
                
        ttk.Button(
            alert_window,
            text="Add Alert",
            command=add_alert
        ).pack(pady=5)
        
        # Alerts list
        alerts_frame = ttk.Frame(alert_window)
        alerts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        alerts_tree = ttk.Treeview(
            alerts_frame,
            columns=('Product', 'Max Price'),
            show='headings'
        )
        alerts_tree.heading('Product', text='Product')
        alerts_tree.heading('Max Price', text='Max Price (€)')
        
        def update_alerts_list():
            for item in alerts_tree.get_children():
                alerts_tree.delete(item)
            for product, price in self.preferences.get_price_alerts().items():
                alerts_tree.insert('', 'end', values=(product, f"€{price:.2f}"))
                
        update_alerts_list()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryGuruApp(root)
    root.mainloop()
