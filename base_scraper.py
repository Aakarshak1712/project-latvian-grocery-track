from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import logging

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    @abstractmethod
    def search_product(self, query: str) -> list:
        """Search for a product and return a list of results"""
        pass
    
    @abstractmethod
    def get_product_price(self, product_url: str) -> float:
        """Get the current price for a specific product"""
        pass
    
    @abstractmethod
    def get_discounts(self) -> list:
        """Get current discounts/promotions"""
        pass
    
    def _make_request(self, url: str) -> BeautifulSoup:
        """Make an HTTP request and return BeautifulSoup object"""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None
