from .base_scraper import BaseScraper
import json
import logging

class RimiScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.rimi.lv"
        self.search_url = f"{self.base_url}/e-veikals/meklet"
        
    def search_product(self, query: str) -> list:
        """
        Search for products on Rimi Latvia
        Returns list of products with their prices
        """
        try:
            params = {
                'q': query,
                'page': 1
            }
            soup = self._make_request(f"{self.search_url}?{params}")
            if not soup:
                return []
                
            products = []
            product_cards = soup.find_all('div', class_='product-grid__item')
            
            for card in product_cards:
                try:
                    name = card.find('p', class_='card__name').text.strip()
                    price_elem = card.find('div', class_='price-tag')
                    if price_elem:
                        price = float(price_elem.get('data-price', 0))
                        products.append({
                            'name': name,
                            'price': price,
                            'store': 'Rimi',
                            'url': self.base_url + card.find('a')['href']
                        })
                except Exception as e:
                    logging.error(f"Error parsing product card: {str(e)}")
                    continue
                    
            return products
        except Exception as e:
            logging.error(f"Error searching Rimi products: {str(e)}")
            return []
            
    def get_product_price(self, product_url: str) -> float:
        """Get current price for a specific product"""
        try:
            soup = self._make_request(product_url)
            if not soup:
                return None
                
            price_elem = soup.find('div', class_='price-tag')
            if price_elem:
                return float(price_elem.get('data-price', 0))
            return None
        except Exception as e:
            logging.error(f"Error getting product price: {str(e)}")
            return None
            
    def get_discounts(self) -> list:
        """Get current discounts/promotions"""
        try:
            soup = self._make_request(f"{self.base_url}/e-veikals/akcijas")
            if not soup:
                return []
                
            discounts = []
            discount_cards = soup.find_all('div', class_='product-grid__item')
            
            for card in discount_cards:
                try:
                    name = card.find('p', class_='card__name').text.strip()
                    regular_price = float(card.find('span', class_='price-tag__original-price').text.strip().replace('€', ''))
                    discount_price = float(card.find('div', class_='price-tag').get('data-price', 0))
                    
                    discounts.append({
                        'name': name,
                        'store': 'Rimi',
                        'original_price': regular_price,
                        'discount_price': discount_price,
                        'url': self.base_url + card.find('a')['href']
                    })
                except Exception as e:
                    logging.error(f"Error parsing discount card: {str(e)}")
                    continue
                    
            return discounts
        except Exception as e:
            logging.error(f"Error getting Rimi discounts: {str(e)}")
            return []
