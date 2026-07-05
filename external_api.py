import requests
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

# OpenFoodFacts API base URL
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org/api/v0"

class ExternalAPIIntegration:
    """Handles integration with OpenFoodFacts API."""
    
    def __init__(self, timeout: int = 5, max_retries: int = 2):
        self.timeout = timeout
        self.base_url = OPENFOODFACTS_API_URL
        self.max_retries = max_retries

    def _get_with_retry(self, url: str, params: dict = None) -> Optional[requests.Response]:
        """
        Perform a GET request with simple retry logic on transient failures.

        Args:
            url: Request URL
            params: Optional query parameters

        Returns:
            Response object or None on failure
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                return response
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying: {e}")
                    time.sleep(0.5)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
                    return None
    
    def fetch_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Fetch product information from OpenFoodFacts by barcode.
        
        Args:
            barcode: Product barcode/UPC
            
        Returns:
            Product data dictionary or None if not found
        """
        url = f"{self.base_url}/product/{barcode}.json"
        response = self._get_with_retry(url)

        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == 1 and "product" in data:
                return self._format_product_data(data["product"])

        logger.warning(f"Product not found for barcode: {barcode}")
        return None
    
    def fetch_product_by_name(self, product_name: str, limit: int = 5) -> Optional[list]:
        """
        Fetch products from OpenFoodFacts by name.
        
        Args:
            product_name: Name of the product to search
            limit: Maximum number of results
            
        Returns:
            List of product data dictionaries or None
        """
        params = {
            "search_terms": product_name,
            "json": 1,
            "page_size": limit
        }
        response = self._get_with_retry(
            f"{self.base_url}/cgi/search.pl",
            params=params
        )

        if response and response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            return [self._format_product_data(p) for p in products[:limit]]

        logger.warning(f"No products found for name: {product_name}")
        return None
    
    @staticmethod
    def _format_product_data(product: Dict) -> Dict:
        """
        Format raw API product data into consistent format.
        
        Args:
            product: Raw product data from OpenFoodFacts
            
        Returns:
            Formatted product data
        """
        return {
            "product_name": product.get("product_name", "Unknown"),
            "brands": product.get("brands", "Unknown"),
            "barcode": product.get("code", ""),
            "categories": product.get("categories", ""),
            "ingredients_text": product.get("ingredients_text", "Not available"),
            "nutrition_grade": product.get("nutrition_grade_fr", "Unknown"),
            "energy_kcal": product.get("energy_kcal_100g", 0),
            "fat": product.get("fat_100g", 0),
            "carbohydrates": product.get("carbohydrates_100g", 0),
            "proteins": product.get("proteins_100g", 0),
            "image_url": product.get("image_front_url", ""),
            "url": product.get("url", "")
        }

# Create singleton instance
api_client = ExternalAPIIntegration()

def fetch_product_details(search_term: str, search_type: str = "barcode") -> Optional[Dict]:
    """
    Wrapper function to fetch product details.
    
    Args:
        search_term: Barcode or product name
        search_type: "barcode" or "name"
        
    Returns:
        Product data or None
    """
    if search_type == "barcode":
        return api_client.fetch_product_by_barcode(search_term)
    elif search_type == "name":
        results = api_client.fetch_product_by_name(search_term, limit=1)
        return results[0] if results else None
    return None
