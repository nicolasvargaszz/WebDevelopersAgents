"""
Discovery Agent - Google Maps Scraper
Target: Paraguay (Asunción, Gran Asunción, Central)

Extracts business data from Google Maps and identifies
businesses without an official website.
"""

import asyncio
import json
import logging
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


# ===========================================
# CONSTANTS
# ===========================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "fb.com", "fb.me",
    "instagram.com", "instagr.am",
    "twitter.com", "x.com",
    "tiktok.com",
    "linkedin.com",
    "wa.me", "whatsapp.com",
    "youtube.com", "youtu.be",
]

# Selectors for Google Maps (updated January 2026)
SELECTORS = {
    "search_input": '#UGojuc, input.UGojuc, input[name="q"]',
    "search_button": 'button.mL3xi, button[aria-label="Búsqueda"], button[aria-label="Search"]',
    "results_container": 'div[role="feed"], div.m6QErb.DxyBCb',
    "result_item": 'a.hfpxzc',
    "result_card": 'div.Nv2PK',
    # Detail panel selectors
    "business_name": 'h1.DUwDvf, div.qBF1Pd.fontHeadlineSmall',
    "rating_stars": 'span.ZkP5Je',  # aria-label="4,6 estrellas 206 reseñas"
    "rating_value": 'span.MW4etd',  # "4,6"
    "review_count": 'span.UY7F9',   # "(206)"
    "category": 'button.DkEaL, div.W4Efsd span:first-child',
    "address": 'button[data-item-id="address"], div.rogA2c, div.Io6YTe',
    "phone": 'button[data-item-id*="phone"], a[href^="tel:"]',
    "website": 'a[data-item-id="authority"], a[aria-label*="sitio web"]',
    "hours": 'div[data-hide-tooltip-on-mouse-move] span.ZDu9vd',
}


# ===========================================
# DATA CLASSES
# ===========================================

@dataclass
class ScrapedBusiness:
    """Raw business data from Google Maps"""
    name: str
    google_place_id: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    city: str = "Asunción"
    neighborhood: Optional[str] = None
    phone: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    photo_urls: list = field(default_factory=list)
    photo_count: int = 0
    
    # Website detection
    has_website: bool = False
    website_url: Optional[str] = None
    website_status: str = "none"  # none, social_only, dead, active
    
    # Metadata
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    raw_data: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "google_place_id": self.google_place_id,
            "category": self.category,
            "address": self.address,
            "city": self.city,
            "neighborhood": self.neighborhood,
            "phone": self.phone,
            "rating": self.rating,
            "review_count": self.review_count,
            "photo_urls": self.photo_urls,
            "photo_count": self.photo_count,
            "has_website": self.has_website,
            "website_url": self.website_url,
            "website_status": self.website_status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "scraped_at": self.scraped_at.isoformat(),
        }


# ===========================================
# MAPS SCRAPER CLASS
# ===========================================

class MapsScraper:
    """
    Google Maps Scraper for discovering businesses without websites.
    
    Uses Playwright for browser automation with anti-detection measures.
    """
    
    def __init__(
        self,
        headless: bool = True,
        delay_min: float = 2.0,
        delay_max: float = 5.0,
        max_results_per_search: int = 60,
        timeout: int = 30000,
    ):
        self.headless = headless
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_results = max_results_per_search
        self.timeout = timeout
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.results: list[ScrapedBusiness] = []
        
        # Load locations config
        self.locations = self._load_locations()
        self.categories = self._load_categories()
    
    def _load_locations(self) -> dict:
        """Load locations from config file"""
        config_path = Path(__file__).parent.parent.parent / "config" / "locations.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Locations config not found at {config_path}")
            return {"cities": []}
    
    def _load_categories(self) -> dict:
        """Load categories from config file"""
        config_path = Path(__file__).parent.parent.parent / "config" / "categories.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Categories config not found at {config_path}")
            return {}
    
    async def _random_delay(self, multiplier: float = 1.0) -> None:
        """Add random delay to avoid detection"""
        delay = random.uniform(self.delay_min, self.delay_max) * multiplier
        await asyncio.sleep(delay)
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent string"""
        return random.choice(USER_AGENTS)
    
    def _is_social_media_url(self, url: str) -> bool:
        """Check if URL is a social media profile"""
        if not url:
            return False
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            return any(social in domain for social in SOCIAL_MEDIA_DOMAINS)
        except Exception:
            return False
    
    def _extract_place_id(self, url: str) -> Optional[str]:
        """Extract Google Place ID from URL"""
        if not url:
            return None
        # Pattern: /maps/place/.../data=...!1s0x...
        match = re.search(r'!1s(0x[a-f0-9]+:[a-f0-9]+)', url)
        if match:
            return match.group(1)
        # Alternative pattern: place_id=...
        match = re.search(r'place_id=([^&]+)', url)
        if match:
            return match.group(1)
        return None
    
    def _parse_review_count(self, text: str) -> int:
        """Parse review count from text like '(123)' or '123 reseñas'"""
        if not text:
            return 0
        numbers = re.findall(r'[\d,\.]+', text.replace(".", "").replace(",", ""))
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return 0
        return 0
    
    def _parse_rating(self, text: str) -> float:
        """Parse rating from text like '4.5' or '4,5'"""
        if not text:
            return 0.0
        text = text.replace(",", ".")
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
        return 0.0
    
    async def initialize(self) -> None:
        """Initialize browser with anti-detection settings"""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--lang=es-PY,es',
            ]
        )
        
        context = await self.browser.new_context(
            user_agent=self._get_random_user_agent(),
            viewport={"width": 1920, "height": 1080},
            locale="es-PY",
            timezone_id="America/Asuncion",
            geolocation={"latitude": -25.2637, "longitude": -57.5759},
            permissions=["geolocation"],
        )
        
        # Anti-detection scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}};
        """)
        
        self.page = await context.new_page()
        self.page.set_default_timeout(self.timeout)
        
        logger.info("Browser initialized with anti-detection measures")
    
    async def close(self) -> None:
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
    
    async def search_businesses(
        self,
        query: str,
        location: str,
        max_results: Optional[int] = None
    ) -> list[ScrapedBusiness]:
        """
        Search for businesses on Google Maps.
        
        Args:
            query: Search term (e.g., "restaurantes", "salón de belleza")
            location: Location to search (e.g., "Villa Morra, Asunción")
            max_results: Maximum results to scrape
            
        Returns:
            List of ScrapedBusiness objects
        """
        if not self.page:
            await self.initialize()
        
        max_results = max_results or self.max_results
        search_query = f"{query} en {location}, Paraguay"
        
        logger.info(f"Searching: {search_query}")
        
        try:
            # Navigate to Google Maps
            await self.page.goto("https://www.google.com/maps?hl=es", wait_until="domcontentloaded")
            await self._random_delay(1.0)
            
            # Handle cookie consent - try multiple button variations
            for selector in [
                'button[aria-label*="Aceptar"]',
                'button[aria-label*="Accept"]', 
                'button:has-text("Aceptar todo")',
                'button:has-text("Accept all")',
                'form[action*="consent"] button',
                'button#L2AGLb',
            ]:
                try:
                    btn = await self.page.query_selector(selector)
                    if btn:
                        await btn.click()
                        logger.info("Accepted cookie consent")
                        await self._random_delay(0.5)
                        break
                except Exception:
                    continue
            
            # Perform search
            search_box = await self.page.wait_for_selector(SELECTORS["search_input"], timeout=10000)
            await search_box.click()
            await self._random_delay(0.3)
            await search_box.fill(search_query)
            await self._random_delay(0.3)
            
            # Click search button or press Enter
            search_btn = await self.page.query_selector(SELECTORS["search_button"])
            if search_btn:
                await search_btn.click()
            else:
                await self.page.keyboard.press("Enter")
            
            await self._random_delay(1.5)
            
            # Wait for results panel to appear (left sidebar with business list)
            try:
                await self.page.wait_for_selector(SELECTORS["results_container"], timeout=10000)
            except PlaywrightTimeout:
                # If no results panel, try scrollable container
                try:
                    await self.page.wait_for_selector('div.m6QErb.WNBkOb', timeout=5000)
                except PlaywrightTimeout:
                    logger.warning("Results panel not found, checking for map pins...")
            
            await self._random_delay()
            
            # Scroll to load more results
            businesses = await self._scroll_and_collect_results(max_results)
            
            # Process each business
            results = []
            for i, business_el in enumerate(businesses[:max_results]):
                try:
                    business = await self._extract_business_details(business_el, location)
                    if business:
                        results.append(business)
                        logger.info(f"[{i+1}/{len(businesses)}] Scraped: {business.name}")
                    
                    await self._random_delay(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error extracting business {i}: {e}")
                    continue
            
            self.results.extend(results)
            return results
            
        except PlaywrightTimeout:
            # Save screenshot for debugging
            await self.page.screenshot(path="debug_timeout.png")
            logger.error(f"Timeout searching for: {search_query}. Screenshot saved.")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def _scroll_and_collect_results(self, target_count: int) -> list:
        """Scroll through results to load more businesses"""
        results_container = await self.page.query_selector('div[role="feed"], div.m6QErb.DxyBCb')
        
        if not results_container:
            logger.warning("Results container not found")
            return []
        
        collected = []
        seen_hrefs = set()
        last_count = 0
        no_change_count = 0
        
        while len(collected) < target_count and no_change_count < 3:
            # Get current results - links to places
            items = await self.page.query_selector_all('a.hfpxzc')
            
            # Deduplicate by href
            for item in items:
                href = await item.get_attribute("href")
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    collected.append(item)
            
            if len(collected) == last_count:
                no_change_count += 1
            else:
                no_change_count = 0
                last_count = len(collected)
            
            # Scroll down
            await results_container.evaluate("el => el.scrollBy(0, 300)")
            await self._random_delay(0.4)
            
            logger.debug(f"Scrolling... found {len(collected)} unique results")
        
        return collected[:target_count]
    
    async def _extract_business_details(self, element, location: str) -> Optional[ScrapedBusiness]:
        """Extract details from a business listing"""
        try:
            # Click on the business to open details panel
            await element.click()
            await self._random_delay(1.0)
            
            # Wait for details panel to load
            await self.page.wait_for_selector('div.m6QErb.DxyBCb, div[role="main"]', timeout=10000)
            await self._random_delay(0.5)
            
            # Extract name - try multiple selectors
            name = "Unknown"
            for name_sel in ['h1.DUwDvf', 'div.qBF1Pd.fontHeadlineSmall', 'h2.qBF1Pd', 'div.fontHeadlineSmall span']:
                name_el = await self.page.query_selector(name_sel)
                if name_el:
                    name = await name_el.inner_text()
                    if name and name != "Resultados" and len(name) > 1:
                        break
            
            # Extract place ID from URL
            current_url = self.page.url
            place_id = self._extract_place_id(current_url)
            
            # Extract rating and review count from aria-label (most reliable)
            rating = 0.0
            review_count = 0
            
            # Try to get from aria-label "4,6 estrellas 206 reseñas"
            rating_el = await self.page.query_selector('span.ZkP5Je')
            if rating_el:
                aria_label = await rating_el.get_attribute("aria-label") or ""
                # Parse "4,6 estrellas 206 reseñas"
                rating_match = re.search(r'([\d,\.]+)\s*estrellas?', aria_label)
                if rating_match:
                    rating = self._parse_rating(rating_match.group(1))
                review_match = re.search(r'([\d\.]+)\s*reseñas?', aria_label.replace(".", ""))
                if review_match:
                    review_count = int(review_match.group(1))
            
            # Fallback to individual elements
            if rating == 0:
                rating_val = await self.page.query_selector('span.MW4etd')
                if rating_val:
                    rating = self._parse_rating(await rating_val.inner_text())
            
            if review_count == 0:
                review_el = await self.page.query_selector('span.UY7F9')
                if review_el:
                    review_text = await review_el.inner_text()
                    review_count = self._parse_review_count(review_text)
            
            # Extract category
            category = None
            cat_el = await self.page.query_selector('button[jsaction*="category"]')
            if cat_el:
                category = await cat_el.inner_text()
            
            # Extract address
            address = None
            addr_el = await self.page.query_selector('button[data-item-id="address"]')
            if addr_el:
                address = await addr_el.inner_text()
            
            # Extract phone
            phone = None
            phone_el = await self.page.query_selector('button[data-item-id*="phone"]')
            if phone_el:
                phone = await phone_el.inner_text()
                phone = re.sub(r'[^\d+\-\s()]', '', phone)
            
            # Check for website
            website_url = None
            website_status = "none"
            has_website = False
            
            website_el = await self.page.query_selector('a[data-item-id="authority"]')
            if website_el:
                website_url = await website_el.get_attribute("href")
                
                if website_url:
                    if self._is_social_media_url(website_url):
                        website_status = "social_only"
                        has_website = False
                    else:
                        # Could add dead link check here
                        website_status = "active"
                        has_website = True
            
            # Extract photos count
            photo_count = 0
            photo_urls = []
            photos_btn = await self.page.query_selector('button[jsaction*="photos"]')
            if photos_btn:
                photos_text = await photos_btn.inner_text()
                photo_match = re.search(r'(\d+)', photos_text)
                if photo_match:
                    photo_count = int(photo_match.group(1))
            
            # Get thumbnail images
            img_elements = await self.page.query_selector_all('button[jsaction*="heroHeaderImage"] img, img[decoding="async"]')
            for img in img_elements[:5]:
                src = await img.get_attribute("src")
                if src and "googleusercontent" in src:
                    photo_urls.append(src)
            
            # Extract coordinates from URL
            lat, lng = None, None
            coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
            if coord_match:
                lat = float(coord_match.group(1))
                lng = float(coord_match.group(2))
            
            business = ScrapedBusiness(
                name=name.strip(),
                google_place_id=place_id,
                category=category,
                address=address,
                city=location.split(",")[0].strip() if "," in location else location,
                neighborhood=location.split(",")[0].strip() if "," in location else None,
                phone=phone,
                rating=rating,
                review_count=review_count,
                photo_urls=photo_urls,
                photo_count=photo_count or len(photo_urls),
                has_website=has_website,
                website_url=website_url,
                website_status=website_status,
                latitude=lat,
                longitude=lng,
            )
            
            # Close panel and go back
            await self.page.keyboard.press("Escape")
            await self._random_delay(0.3)
            
            return business
            
        except Exception as e:
            logger.warning(f"Error extracting business details: {e}")
            return None
    
    async def check_website_status(self, url: str) -> str:
        """
        Check if a website URL is actually functional.
        
        Returns:
            'active', 'dead', 'social_only', or 'redirect'
        """
        if not url:
            return "none"
        
        if self._is_social_media_url(url):
            return "social_only"
        
        try:
            context = await self.browser.new_context(
                user_agent=self._get_random_user_agent()
            )
            page = await context.new_page()
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            
            await page.close()
            await context.close()
            
            if response:
                status = response.status
                if 200 <= status < 400:
                    return "active"
                elif status >= 400:
                    return "dead"
            
            return "dead"
            
        except Exception as e:
            logger.debug(f"Website check failed for {url}: {e}")
            return "dead"
    
    async def run_discovery(
        self,
        categories: Optional[list[str]] = None,
        cities: Optional[list[str]] = None,
    ) -> list[ScrapedBusiness]:
        """
        Run full discovery process across configured locations and categories.
        
        Args:
            categories: List of category keys to search (or use config)
            cities: List of city names to search (or use config)
            
        Returns:
            All discovered businesses without websites
        """
        all_results = []
        
        # Get categories to search
        search_categories = categories or self.locations.get("search_config", {}).get(
            "categories_priority", ["restaurant", "salon"]
        )
        
        # Get cities to search
        search_cities = cities or [c["name"] for c in self.locations.get("cities", [])]
        
        try:
            await self.initialize()
            
            for city_data in self.locations.get("cities", []):
                city_name = city_data["name"]
                
                if search_cities and city_name not in search_cities:
                    continue
                
                for zone in city_data.get("zones", [{"name": city_name}]):
                    zone_name = zone.get("name", city_name)
                    location = f"{zone_name}, {city_name}"
                    
                    for category_key in search_categories:
                        cat_config = self.categories.get(category_key, {})
                        search_terms = cat_config.get("google_search_terms", [category_key])
                        
                        # Use primary search term
                        search_term = search_terms[0] if search_terms else category_key
                        
                        logger.info(f"Searching {search_term} in {location}")
                        
                        results = await self.search_businesses(
                            query=search_term,
                            location=location
                        )
                        
                        # Filter out businesses with websites
                        no_website = [b for b in results if not b.has_website]
                        all_results.extend(no_website)
                        
                        logger.info(f"Found {len(no_website)} businesses without website")
                        
                        # Respect rate limits
                        await self._random_delay(2.0)
            
        finally:
            await self.close()
        
        logger.info(f"Discovery complete. Total: {len(all_results)} businesses without websites")
        return all_results
    
    def get_results_without_website(self) -> list[ScrapedBusiness]:
        """Get only businesses that don't have a website"""
        return [b for b in self.results if not b.has_website]
    
    def export_results(self, filepath: str) -> None:
        """Export results to JSON file"""
        data = [b.to_dict() for b in self.results]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported {len(data)} results to {filepath}")


# ===========================================
# STANDALONE EXECUTION
# ===========================================

def load_existing_data(filepath: str) -> tuple[list[dict], set[str], set[str]]:
    """Load existing scraped data and extract seen names/hrefs and completed searches"""
    existing_data = []
    seen_names = set()
    seen_phones = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            for b in existing_data:
                seen_names.add(b.get('name', ''))
                if b.get('phone'):
                    seen_phones.add(b.get('phone', '').strip())
        logger.info(f"Loaded {len(existing_data)} existing businesses")
    except FileNotFoundError:
        logger.info("No existing data file found, starting fresh")
    except json.JSONDecodeError:
        logger.warning("Could not parse existing data file, starting fresh")
    
    return existing_data, seen_names, seen_phones


async def main():
    """Run discovery across multiple categories and locations - CONTINUES from existing data"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    OUTPUT_FILE = "discovered_businesses.json"
    
    # Load existing data to avoid duplicates
    existing_data, seen_names, seen_phones = load_existing_data(OUTPUT_FILE)
    logger.info(f"Starting with {len(seen_names)} known businesses to skip")
    
    scraper = MapsScraper(
        headless=False,  # Set True for production
        delay_min=2.0,
        delay_max=4.0,
        max_results_per_search=15,
    )
    
    # ALL POSSIBLE SEARCHES - organized by category and location
    # We'll skip any that were already done based on existing results
    all_searches = [
        # === ALREADY COMPLETED (will be skipped if businesses found) ===
        # ("salón de belleza", "Villa Morra, Asunción"),
        # ("barbería", "Villa Morra, Asunción"),
        # ("restaurante", "Carmelitas, Asunción"),
        # ("dentista", "Centro, Asunción"),
        # ("veterinaria", "San Lorenzo"),
        
        # === NEW SEARCHES - Asunción zones ===
        ("peluquería", "Centro, Asunción"),
        ("gimnasio", "Villa Morra, Asunción"),
        ("cafetería", "Carmelitas, Asunción"),
        ("panadería", "Centro, Asunción"),
        ("taller mecánico", "San Lorenzo"),
        ("clínica médica", "Villa Morra, Asunción"),
        ("farmacia", "Centro, Asunción"),
        ("ferretería", "San Lorenzo"),
        ("librería", "Centro, Asunción"),
        ("óptica", "Centro, Asunción"),
        
        # === Recoleta ===
        ("restaurante", "Recoleta, Asunción"),
        ("dentista", "Recoleta, Asunción"),
        ("peluquería", "Recoleta, Asunción"),
        ("veterinaria", "Recoleta, Asunción"),
        ("gimnasio", "Recoleta, Asunción"),
        
        # === Las Mercedes ===
        ("restaurante", "Las Mercedes, Asunción"),
        ("salón de belleza", "Las Mercedes, Asunción"),
        ("barbería", "Las Mercedes, Asunción"),
        ("dentista", "Las Mercedes, Asunción"),
        
        # === Sajonia ===
        ("restaurante", "Sajonia, Asunción"),
        ("taller mecánico", "Sajonia, Asunción"),
        ("ferretería", "Sajonia, Asunción"),
        
        # === Luque (Gran Asunción) ===
        ("restaurante", "Luque, Paraguay"),
        ("dentista", "Luque, Paraguay"),
        ("veterinaria", "Luque, Paraguay"),
        ("taller mecánico", "Luque, Paraguay"),
        ("peluquería", "Luque, Paraguay"),
        ("panadería", "Luque, Paraguay"),
        ("gimnasio", "Luque, Paraguay"),
        
        # === Fernando de la Mora ===
        ("restaurante", "Fernando de la Mora, Paraguay"),
        ("dentista", "Fernando de la Mora, Paraguay"),
        ("veterinaria", "Fernando de la Mora, Paraguay"),
        ("barbería", "Fernando de la Mora, Paraguay"),
        ("taller mecánico", "Fernando de la Mora, Paraguay"),
        
        # === Lambaré ===
        ("restaurante", "Lambaré, Paraguay"),
        ("dentista", "Lambaré, Paraguay"),
        ("veterinaria", "Lambaré, Paraguay"),
        ("salón de belleza", "Lambaré, Paraguay"),
        ("panadería", "Lambaré, Paraguay"),
        
        # === Mariano Roque Alonso ===
        ("restaurante", "Mariano Roque Alonso, Paraguay"),
        ("veterinaria", "Mariano Roque Alonso, Paraguay"),
        ("taller mecánico", "Mariano Roque Alonso, Paraguay"),
        ("ferretería", "Mariano Roque Alonso, Paraguay"),
        
        # === Capiatá ===
        ("restaurante", "Capiatá, Paraguay"),
        ("dentista", "Capiatá, Paraguay"),
        ("veterinaria", "Capiatá, Paraguay"),
        ("taller mecánico", "Capiatá, Paraguay"),
        
        # === Ñemby ===
        ("restaurante", "Ñemby, Paraguay"),
        ("dentista", "Ñemby, Paraguay"),
        ("peluquería", "Ñemby, Paraguay"),
        
        # === More specific Asunción searches ===
        ("abogado", "Centro, Asunción"),
        ("contador", "Centro, Asunción"),
        ("inmobiliaria", "Villa Morra, Asunción"),
        ("spa", "Carmelitas, Asunción"),
        ("floristería", "Centro, Asunción"),
        ("lavadero de autos", "San Lorenzo"),
        ("pizzería", "Villa Morra, Asunción"),
        ("heladería", "Carmelitas, Asunción"),
        ("carnicería", "Centro, Asunción"),
        ("cerrajería", "San Lorenzo"),
    ]
    
    # Track new results
    new_results = []
    searches_completed = 0
    
    try:
        await scraper.initialize()
        
        for query, location in all_searches:
            logger.info(f"\n{'='*50}")
            logger.info(f"Searching: {query} in {location}")
            logger.info(f"{'='*50}")
            
            try:
                results = await scraper.search_businesses(
                    query=query,
                    location=location,
                    max_results=12
                )
                
                # Only add truly new businesses
                added_count = 0
                for r in results:
                    phone_clean = (r.phone or '').strip()
                    is_duplicate = (
                        r.name in seen_names or 
                        (phone_clean and phone_clean in seen_phones)
                    )
                    
                    if not is_duplicate:
                        seen_names.add(r.name)
                        if phone_clean:
                            seen_phones.add(phone_clean)
                        new_results.append(r)
                        added_count += 1
                
                logger.info(f"Added {added_count} NEW businesses (skipped {len(results) - added_count} duplicates)")
                searches_completed += 1
                
                # Save progress every 5 searches
                if searches_completed % 5 == 0:
                    combined = existing_data + [r.to_dict() for r in new_results]
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(combined, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 Progress saved: {len(combined)} total businesses")
                
            except Exception as e:
                logger.error(f"Error searching {query} in {location}: {e}")
                continue
            
            # Delay between searches
            await asyncio.sleep(random.uniform(3, 5))
        
        # Final save
        combined = existing_data + [r.to_dict() for r in new_results]
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        
        # Summary
        no_website = [b for b in new_results if not b.has_website]
        
        print(f"\n{'='*60}")
        print(f"DISCOVERY COMPLETE")
        print(f"{'='*60}")
        print(f"Previous businesses: {len(existing_data)}")
        print(f"NEW businesses found: {len(new_results)}")
        print(f"NEW without website: {len(no_website)}")
        print(f"TOTAL in database: {len(combined)}")
        print(f"{'='*60}\n")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
