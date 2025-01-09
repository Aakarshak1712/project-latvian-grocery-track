import json
import os
from pathlib import Path

class PreferencesManager:
    def __init__(self):
        self.preferences_file = Path.home() / '.grocery_guru' / 'preferences.json'
        self.default_preferences = {
            'favorite_stores': [],
            'price_alerts': {},  # product_name: max_price
            'default_currency': '€',
            'language': 'lv',  # Latvian by default
            'theme': 'light',
            'export_format': 'pdf',
            'notification_enabled': True,
            'check_interval_hours': 24
        }
        self.load_preferences()
        
    def load_preferences(self):
        """Load user preferences from file"""
        try:
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    self.preferences = {**self.default_preferences, **json.load(f)}
            else:
                self.preferences = self.default_preferences
                self.save_preferences()
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.preferences = self.default_preferences
            
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            print(f"Error saving preferences: {e}")
            
    def get_preference(self, key):
        """Get a specific preference value"""
        return self.preferences.get(key, self.default_preferences.get(key))
        
    def set_preference(self, key, value):
        """Set a specific preference value"""
        self.preferences[key] = value
        self.save_preferences()
        
    def add_price_alert(self, product_name, max_price):
        """Add a price alert for a specific product"""
        self.preferences['price_alerts'][product_name] = max_price
        self.save_preferences()
        
    def remove_price_alert(self, product_name):
        """Remove a price alert for a specific product"""
        if product_name in self.preferences['price_alerts']:
            del self.preferences['price_alerts'][product_name]
            self.save_preferences()
            
    def toggle_favorite_store(self, store_name):
        """Toggle a store as favorite"""
        if store_name in self.preferences['favorite_stores']:
            self.preferences['favorite_stores'].remove(store_name)
        else:
            self.preferences['favorite_stores'].append(store_name)
        self.save_preferences()
        
    def get_price_alerts(self):
        """Get all price alerts"""
        return self.preferences['price_alerts']
        
    def get_favorite_stores(self):
        """Get list of favorite stores"""
        return self.preferences['favorite_stores']
