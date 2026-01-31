#!/usr/bin/env python3
"""
Full Dataset Scraper: Collect ~2100 businesses from Google Maps
with the corrected scraper that extracts:
- Ratings and review counts
- 5-star reviews with photos
- High-resolution images
- Complete business information

Output: datos_definitivos.json
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/nicolasvargas/Desktop/Code/webpageAutomatization')

from agents.discovery.google_maps import MapsScraper

OUTPUT_FILE = 'datos_definitivos.json'
PROGRESS_FILE = 'scrape_progress.json'
TARGET_BUSINESSES = 2100

# Search queries and locations to cover Paraguay
SEARCHES = [
    # Restaurants
    {"query": "restaurante", "locations": [
        "Villa Morra, Asunción, Paraguay",
        "Carmelitas, Asunción, Paraguay",
        "Centro, Asunción, Paraguay",
        "San Lorenzo, Paraguay",
        "Luque, Paraguay",
        "Fernando de la Mora, Paraguay",
        "Lambaré, Paraguay",
        "Mariano Roque Alonso, Paraguay",
        "Capiatá, Paraguay",
        "Ñemby, Paraguay",
    ]},
    # Cafeterias
    {"query": "cafetería", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Beauty salons
    {"query": "salón de belleza", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
        "Luque, Paraguay",
        "Fernando de la Mora, Paraguay",
    ]},
    # Barber shops
    {"query": "barbería", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Veterinaries
    {"query": "veterinaria", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
        "Luque, Paraguay",
    ]},
    # Dental clinics
    {"query": "clínica dental", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Mechanic shops
    {"query": "taller mecánico", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
        "Luque, Paraguay",
        "Fernando de la Mora, Paraguay",
    ]},
    # Bakeries
    {"query": "panadería", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Gyms
    {"query": "gimnasio", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Pharmacies
    {"query": "farmacia", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Hotels
    {"query": "hotel", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
    ]},
    # Bars
    {"query": "bar", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
        "Carmelitas, Asunción, Paraguay",
    ]},
    # Spas
    {"query": "spa", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
    ]},
    # Car washes
    {"query": "lavadero de autos", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Pet shops
    {"query": "tienda de mascotas", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Electronics
    {"query": "tienda de electrónica", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Clothing stores
    {"query": "tienda de ropa", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
    ]},
    # Florists
    {"query": "floristería", "locations": [
        "Asunción, Paraguay",
    ]},
    # Pizzerias
    {"query": "pizzería", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Ice cream shops
    {"query": "heladería", "locations": [
        "Asunción, Paraguay",
        "Villa Morra, Asunción, Paraguay",
    ]},
    # Laundry
    {"query": "lavandería", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
    # Photography studios
    {"query": "estudio fotográfico", "locations": [
        "Asunción, Paraguay",
    ]},
    # Printing shops
    {"query": "imprenta", "locations": [
        "Asunción, Paraguay",
        "San Lorenzo, Paraguay",
    ]},
]


def load_progress():
    """Load progress from previous run if exists"""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_searches": [], "all_businesses": []}


def save_progress(progress):
    """Save progress to resume later if needed"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def save_final_data(businesses):
    """Save the final dataset"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(businesses, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved {len(businesses)} businesses to {OUTPUT_FILE}")


def deduplicate_businesses(businesses):
    """Remove duplicate businesses based on name + address"""
    seen = set()
    unique = []
    for b in businesses:
        key = (b.get('name', '').lower().strip(), b.get('address', '').lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(b)
    return unique


async def scrape_full_dataset():
    """Main scraping function"""
    progress = load_progress()
    all_businesses = progress.get("all_businesses", [])
    completed_searches = set(progress.get("completed_searches", []))
    
    print("\n" + "="*70)
    print("🚀 FULL DATASET SCRAPER - Collecting ~2100 businesses")
    print("="*70)
    print(f"📊 Starting with {len(all_businesses)} businesses from previous run")
    print(f"🎯 Target: {TARGET_BUSINESSES} businesses")
    print("="*70 + "\n")
    
    scraper = MapsScraper(headless=True)  # Run headless for speed
    
    try:
        await scraper.initialize()
        
        search_count = 0
        total_searches = sum(len(s["locations"]) for s in SEARCHES)
        
        for search_config in SEARCHES:
            query = search_config["query"]
            
            for location in search_config["locations"]:
                search_key = f"{query}|{location}"
                search_count += 1
                
                # Skip if already completed
                if search_key in completed_searches:
                    print(f"⏭️  [{search_count}/{total_searches}] Skipping (already done): {query} in {location}")
                    continue
                
                # Check if we've reached target
                if len(all_businesses) >= TARGET_BUSINESSES:
                    print(f"\n🎯 Reached target of {TARGET_BUSINESSES} businesses!")
                    break
                
                print(f"\n🔍 [{search_count}/{total_searches}] Searching: {query} in {location}")
                print(f"   📊 Current total: {len(all_businesses)} businesses")
                
                try:
                    results = await scraper.search_businesses(
                        query=query,
                        location=location,
                        max_results=50  # Get up to 50 per search
                    )
                    
                    # Convert to dicts
                    new_businesses = [r.to_dict() for r in results]
                    
                    # Add to collection
                    all_businesses.extend(new_businesses)
                    
                    # Deduplicate periodically
                    if len(all_businesses) % 200 == 0:
                        all_businesses = deduplicate_businesses(all_businesses)
                    
                    # Mark as completed
                    completed_searches.add(search_key)
                    
                    # Save progress
                    progress = {
                        "completed_searches": list(completed_searches),
                        "all_businesses": all_businesses,
                        "last_updated": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    
                    print(f"   ✅ Found {len(results)} businesses | Total: {len(all_businesses)}")
                    
                    # Brief pause between searches
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    continue
            
            # Check target after each query category
            if len(all_businesses) >= TARGET_BUSINESSES:
                break
        
        # Final deduplication
        print("\n🔄 Running final deduplication...")
        all_businesses = deduplicate_businesses(all_businesses)
        
        # Save final data
        save_final_data(all_businesses)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"  Total businesses collected: {len(all_businesses)}")
        
        # Statistics
        with_rating = sum(1 for b in all_businesses if b.get('rating'))
        with_reviews = sum(1 for b in all_businesses if b.get('reviews'))
        with_photos = sum(1 for b in all_businesses if b.get('photo_urls'))
        without_website = sum(1 for b in all_businesses if not b.get('has_website'))
        
        print(f"  With ratings: {with_rating} ({100*with_rating//len(all_businesses)}%)")
        print(f"  With 5-star reviews: {with_reviews} ({100*with_reviews//len(all_businesses)}%)")
        print(f"  With photos: {with_photos} ({100*with_photos//len(all_businesses)}%)")
        print(f"  Without website (leads): {without_website} ({100*without_website//len(all_businesses)}%)")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        # Save whatever we have
        if all_businesses:
            save_final_data(all_businesses)
            save_progress({
                "completed_searches": list(completed_searches),
                "all_businesses": all_businesses,
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            })
    
    finally:
        await scraper.close()
        print("\n🏁 Scraping complete!")


if __name__ == "__main__":
    print(f"\n📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(scrape_full_dataset())
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
