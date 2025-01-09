from .base_scraper import BaseScraper
import logging
import json

class MaximaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.maxima.lv"
        self.search_url = f"{self.base_url}/api/products/search"
        
    def search_product(self, query: str) -> list:
        """
        Search for products on Maxima Latvia
        Returns list of products with their prices
        """
        try:
            params = {
                'q': query,
                'page': 1,
                'limit': 20
            }
            
            response = self.session.get(
                self.search_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data.get('items', []):
                try:
                    products.append({
                        'name': item['name'],
                        'price': float(item['price']),
                        'store': 'Maxima',
                        'url': f"{self.base_url}/products/{item['slug']}"
                    })
                except Exception as e:
                    logging.error(f"Error parsing product: {str(e)}")
                    continue
                    
            return products
        except Exception as e:
            logging.error(f"Error searching Maxima products: {str(e)}")
            return []
            
    def get_product_price(self, product_url: str) -> float:
        """Get current price for a specific product"""
        try:
            soup = self._make_request(product_url)
            if not soup:
                return None
                
            price_elem = soup.find('span', class_='product-price')
            if price_elem:
                price_text = price_elem.text.strip().replace('€', '').replace(',', '.')
                return float(price_text)
            return None
        except Exception as e:
            logging.error(f"Error getting product price: {str(e)}")
            return None
            
    def get_discounts(self) -> list:
        """Get current discounts/promotions"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/promotions",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            discounts = []
            for item in data.get('items', []):
                try:
                    discounts.append({
                        'name': item['name'],
                        'store': 'Maxima',
                        'original_price': float(item['original_price']),
                        'discount_price': float(item['discount_price']),
                        'url': f"{self.base_url}/promotions/{item['slug']}",
                        'valid_until': item.get('valid_until')
                    })
                except Exception as e:
                    logging.error(f"Error parsing discount: {str(e)}")
                    continue
                    
            return discounts
        except Exception as e:
            logging.error(f"Error getting Maxima discounts: {str(e)}")
            return []
