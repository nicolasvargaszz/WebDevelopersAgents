#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🎯 ENDURANCE SCRAPING LOOP v1.0                            ║
║                                                                               ║
║  Automated lead discovery system that runs until TARGET_LEADS is reached     ║
║  or all search combinations are exhausted.                                    ║
║                                                                               ║
║  Features:                                                                    ║
║  • Smart permutation of all Category × Location combinations                  ║
║  • Crash recovery via search_history.json                                     ║
║  • Anti-blocking measures with random delays                                  ║
║  • Cool-down periods on soft-bans                                             ║
║  • Real-time progress tracking                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import random
import time
import itertools
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.discovery.google_maps import MapsScraper, ScrapedBusiness

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TARGET_LEADS = 1000  # Stop when we reach this many qualified leads
MIN_DELAY = 5        # Minimum seconds between searches
MAX_DELAY = 15       # Maximum seconds between searches
COOLDOWN_TIME = 60   # Seconds to wait on soft-ban detection
MAX_RETRIES = 3      # Max retries per search before moving on
HEADLESS = True      # Run browser headless for production

# File paths
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
CATEGORIES_FILE = CONFIG_DIR / "categories.json"
LOCATIONS_FILE = CONFIG_DIR / "locations.json"
HISTORY_FILE = PROJECT_ROOT / "search_history.json"
LEADS_FILE = PROJECT_ROOT / "discovered_businesses.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSOLE OUTPUT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class Console:
    """Beautiful console output with colors and formatting."""
    
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }
    
    @staticmethod
    def clear_line():
        print("\033[K", end="")
    
    @staticmethod
    def banner():
        print(f"""
{Console.COLORS['cyan']}╔═══════════════════════════════════════════════════════════════════════════════╗
║{Console.COLORS['yellow']}  🎯 ENDURANCE SCRAPING LOOP - Lead Discovery System                          {Console.COLORS['cyan']}║
║{Console.COLORS['white']}     Target: {TARGET_LEADS} qualified leads (businesses WITHOUT websites)          {Console.COLORS['cyan']}║
╚═══════════════════════════════════════════════════════════════════════════════╝{Console.COLORS['reset']}
""")
    
    @staticmethod
    def progress(current: int, target: int, category: str, location: str, combo_num: int, total_combos: int):
        pct = (current / target) * 100 if target > 0 else 0
        bar_width = 30
        filled = int(bar_width * current / target) if target > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        print(f"\r{Console.COLORS['bold']}{Console.COLORS['cyan']}[{bar}] {current}/{target} ({pct:.1f}%){Console.COLORS['reset']}", end="")
        print(f" | Combo {combo_num}/{total_combos}", end="")
        print(f" | {Console.COLORS['yellow']}'{category}'{Console.COLORS['reset']} in {Console.COLORS['green']}'{location}'{Console.COLORS['reset']}   ", end="")
        sys.stdout.flush()
    
    @staticmethod
    def success(msg: str):
        print(f"\n{Console.COLORS['green']}✅ {msg}{Console.COLORS['reset']}")
    
    @staticmethod
    def warning(msg: str):
        print(f"\n{Console.COLORS['yellow']}⚠️  {msg}{Console.COLORS['reset']}")
    
    @staticmethod
    def error(msg: str):
        print(f"\n{Console.COLORS['red']}❌ {msg}{Console.COLORS['reset']}")
    
    @staticmethod
    def info(msg: str):
        print(f"\n{Console.COLORS['blue']}ℹ️  {msg}{Console.COLORS['reset']}")
    
    @staticmethod
    def found_lead(name: str, category: str):
        print(f"\n{Console.COLORS['magenta']}🎯 NEW LEAD: {Console.COLORS['white']}{name}{Console.COLORS['reset']} ({category})")
    
    @staticmethod
    def stats(leads: int, searches: int, skipped: int, duration: float):
        print(f"""
{Console.COLORS['cyan']}╔═══════════════════════════════════════════════════════════════════════════════╗
║{Console.COLORS['white']}                         📊 SESSION STATISTICS                               {Console.COLORS['cyan']}║
╠═══════════════════════════════════════════════════════════════════════════════╣
║{Console.COLORS['green']}  ✅ Qualified Leads Found:  {leads:<10}{Console.COLORS['cyan']}                                         ║
║{Console.COLORS['blue']}  🔍 Total Searches Made:    {searches:<10}{Console.COLORS['cyan']}                                         ║
║{Console.COLORS['yellow']}  ⏭️  Searches Skipped:       {skipped:<10}{Console.COLORS['cyan']}                                         ║
║{Console.COLORS['white']}  ⏱️  Total Duration:         {duration/60:.1f} minutes{Console.COLORS['cyan']}                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝{Console.COLORS['reset']}
""")


# ═══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class SearchHistory:
    """Manages search history for crash recovery."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.history: set = set()
        self.load()
    
    def load(self):
        """Load search history from file."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = set(data.get("completed_searches", []))
                Console.info(f"Loaded {len(self.history)} completed searches from history")
            except Exception as e:
                Console.warning(f"Could not load history: {e}")
                self.history = set()
        else:
            self.history = set()
    
    def save(self):
        """Save search history to file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "completed_searches": list(self.history),
                    "last_updated": datetime.now().isoformat(),
                    "total_searches": len(self.history)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Console.error(f"Could not save history: {e}")
    
    def is_completed(self, category: str, location: str) -> bool:
        """Check if a search combination has been completed."""
        key = f"{category}|{location}"
        return key in self.history
    
    def mark_completed(self, category: str, location: str):
        """Mark a search combination as completed."""
        key = f"{category}|{location}"
        self.history.add(key)
        self.save()  # Save after each completion for crash recovery


class LeadsManager:
    """Manages discovered leads storage."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.leads: list = []
        self.seen_names: set = set()
        self.load()
    
    def load(self):
        """Load existing leads from file."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.leads = json.load(f)
                    # Build seen names set for deduplication
                    for lead in self.leads:
                        name = lead.get("name", "").lower().strip()
                        if name:
                            self.seen_names.add(name)
                Console.info(f"Loaded {len(self.leads)} existing leads")
            except Exception as e:
                Console.warning(f"Could not load leads: {e}")
                self.leads = []
    
    def save(self):
        """Save leads to file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.leads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Console.error(f"Could not save leads: {e}")
    
    def count_qualified(self) -> int:
        """Count leads without websites (qualified leads)."""
        return sum(1 for lead in self.leads 
                   if not lead.get("website_url") 
                   and lead.get("website_status") != "active")
    
    def add_lead(self, business: dict) -> bool:
        """
        Add a new lead if it's qualified (no website) and not a duplicate.
        Returns True if added, False otherwise.
        """
        name = business.get("name", "").lower().strip()
        
        # Skip duplicates
        if name in self.seen_names:
            return False
        
        # Only add if no active website
        has_website = (
            business.get("website_url") or 
            business.get("website_status") == "active"
        )
        
        if has_website:
            return False
        
        # Add the lead
        self.leads.append(business)
        self.seen_names.add(name)
        self.save()  # Save after each addition for safety
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION LOADERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_categories() -> list[tuple[str, str]]:
    """
    Load categories from config file.
    Returns list of (category_key, search_term) tuples.
    """
    categories = []
    
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for key, config in data.items():
            # Use the Spanish name as primary search term
            name_es = config.get("name_es", config.get("name", key))
            categories.append((key, name_es))
            
            # Also add google search terms for variety
            for term in config.get("google_search_terms", [])[:2]:  # Limit to 2 extra terms
                if term.lower() != name_es.lower():
                    categories.append((key, term))
        
        Console.info(f"Loaded {len(categories)} category search terms")
        return categories
        
    except Exception as e:
        Console.error(f"Could not load categories: {e}")
        return []


def load_locations() -> list[str]:
    """
    Load all locations (neighborhoods/zones) from config file.
    Returns list of location names.
    """
    locations = []
    
    try:
        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for city in data.get("cities", []):
            city_name = city.get("name", "")
            
            # Add zones within the city
            for zone in city.get("zones", []):
                zone_name = zone.get("name", "")
                if zone_name:
                    # Format: "Zone Name, City Name" (scraper adds Paraguay)
                    full_location = f"{zone_name}, {city_name}"
                    locations.append(full_location)
            
            # Also add the city itself as a location
            if city_name:
                locations.append(city_name)
        
        Console.info(f"Loaded {len(locations)} locations")
        return locations
        
    except Exception as e:
        Console.error(f"Could not load locations: {e}")
        return []


def generate_search_combinations(categories: list, locations: list) -> list[tuple]:
    """
    Generate all possible (category, search_term, location) combinations.
    Shuffled randomly to avoid IP bans from hitting same location repeatedly.
    """
    combinations = list(itertools.product(categories, locations))
    
    # Expand tuples: ((key, term), location) -> (key, term, location)
    expanded = [(cat[0], cat[1], loc) for cat, loc in combinations]
    
    # Shuffle to randomize
    random.shuffle(expanded)
    
    Console.info(f"Generated {len(expanded)} search combinations (shuffled)")
    return expanded


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SCRAPING LOOP
# ═══════════════════════════════════════════════════════════════════════════════

async def run_endurance_loop():
    """
    Main endurance scraping loop.
    Continues until TARGET_LEADS reached or all combinations exhausted.
    """
    Console.banner()
    
    # Initialize managers
    history = SearchHistory(HISTORY_FILE)
    leads = LeadsManager(LEADS_FILE)
    
    # Check if we've already reached target
    current_leads = leads.count_qualified()
    if current_leads >= TARGET_LEADS:
        Console.success(f"Target already reached! {current_leads}/{TARGET_LEADS} leads")
        return
    
    # Load configurations
    categories = load_categories()
    locations = load_locations()
    
    if not categories or not locations:
        Console.error("Could not load categories or locations. Aborting.")
        return
    
    # Generate all search combinations
    combinations = generate_search_combinations(categories, locations)
    total_combos = len(combinations)
    
    # Filter out already completed searches
    pending = [
        (key, term, loc) for key, term, loc in combinations 
        if not history.is_completed(term, loc)
    ]
    
    skipped = total_combos - len(pending)
    if skipped > 0:
        Console.info(f"Skipping {skipped} already-completed searches")
    
    if not pending:
        Console.warning("All search combinations have been completed!")
        return
    
    # Statistics
    start_time = time.time()
    searches_completed = 0
    soft_ban_count = 0
    
    # Initialize scraper
    scraper = None
    
    try:
        Console.info("Initializing MapsScraper...")
        scraper = MapsScraper(headless=HEADLESS)
        await scraper.initialize()
        Console.success("Scraper initialized successfully")
        
        # Main loop
        for i, (category_key, search_term, location) in enumerate(pending, 1):
            # Check if target reached
            current_leads = leads.count_qualified()
            if current_leads >= TARGET_LEADS:
                Console.success(f"\n🎉 TARGET REACHED! {current_leads}/{TARGET_LEADS} leads collected!")
                break
            
            # Progress display
            combo_num = skipped + i
            Console.progress(current_leads, TARGET_LEADS, search_term, location, combo_num, total_combos)
            
            # Retry logic
            retry_count = 0
            success = False
            
            while retry_count < MAX_RETRIES and not success:
                try:
                    # Perform the search
                    results = await scraper.search_businesses(
                        query=search_term,
                        location=location,
                        max_results=20
                    )
                    
                    # Process results
                    new_leads_this_search = 0
                    for business in results:
                        # Convert to dict if it's a ScrapedBusiness object
                        if isinstance(business, ScrapedBusiness):
                            business_dict = business.to_dict()
                        else:
                            business_dict = business
                        
                        # Add category info
                        business_dict["discovered_category"] = category_key
                        business_dict["discovered_location"] = location
                        business_dict["discovered_at"] = datetime.now().isoformat()
                        
                        # Try to add as lead
                        if leads.add_lead(business_dict):
                            new_leads_this_search += 1
                            Console.found_lead(
                                business_dict.get("name", "Unknown"),
                                category_key
                            )
                    
                    # Mark search as completed
                    history.mark_completed(search_term, location)
                    searches_completed += 1
                    success = True
                    
                    if new_leads_this_search > 0:
                        Console.success(f"Found {new_leads_this_search} new qualified leads!")
                    
                except Exception as e:
                    retry_count += 1
                    error_msg = str(e).lower()
                    
                    # Detect potential soft-ban
                    if "timeout" in error_msg or "not found" in error_msg or "visible" in error_msg:
                        soft_ban_count += 1
                        Console.warning(f"Potential soft-ban detected. Cooling down for {COOLDOWN_TIME}s...")
                        await asyncio.sleep(COOLDOWN_TIME)
                    else:
                        Console.error(f"Search error (attempt {retry_count}/{MAX_RETRIES}): {e}")
                        await asyncio.sleep(10)  # Brief pause before retry
            
            if not success:
                Console.warning(f"Skipping '{search_term}' in '{location}' after {MAX_RETRIES} failed attempts")
                # Still mark as completed to avoid infinite retries
                history.mark_completed(search_term, location)
            
            # Anti-blocking delay between searches
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            await asyncio.sleep(delay)
    
    except KeyboardInterrupt:
        Console.warning("\n\nInterrupted by user. Progress has been saved.")
    
    except Exception as e:
        Console.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if scraper:
            try:
                await scraper.close()
            except:
                pass
        
        # Final statistics
        duration = time.time() - start_time
        final_leads = leads.count_qualified()
        
        Console.stats(
            leads=final_leads,
            searches=searches_completed,
            skipped=skipped,
            duration=duration
        )
        
        # Save final state
        history.save()
        leads.save()
        
        Console.info(f"Progress saved. Run again to continue from where you left off.")
        
        if final_leads >= TARGET_LEADS:
            Console.success(f"🎉 MISSION ACCOMPLISHED! Collected {final_leads} leads!")
        else:
            remaining = TARGET_LEADS - final_leads
            Console.info(f"Still need {remaining} more leads to reach target.")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Entry point for the endurance scraping loop."""
    try:
        asyncio.run(run_endurance_loop())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
