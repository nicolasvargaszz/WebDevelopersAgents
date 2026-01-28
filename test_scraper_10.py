#!/usr/bin/env python3
"""Test script to scrape 10 businesses and show the ultra deep data."""

import asyncio
import json
from agents.discovery.google_maps import MapsScraper


async def test_scraper():
    print("🚀 Starting Ultra Deep Data Scraper Test...")
    
    scraper = MapsScraper(headless=False, max_results_per_search=12)
    await scraper.initialize()
    
    # Search for bakeries in Asunción
    query = "panadería Asunción Paraguay"
    location = "Asunción, Paraguay"
    
    print(f"\n🔍 Searching: {query}")
    results = await scraper.search_businesses(query, location)
    print(f"   Found {len(results)} businesses")
    
    await scraper.close()
    
    # Take first 10
    results_10 = results[:10]
    
    # Save to JSON
    data = [r.to_dict() for r in results_10]
    output_file = "test_scrape_10.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(results_10)} businesses to {output_file}")
    
    # Print detailed summary
    print("\n" + "=" * 80)
    print("📊 SCRAPING RESULTS - ULTRA DEEP DATA")
    print("=" * 80)
    
    for i, b in enumerate(results_10):
        print(f"\n{'─' * 80}")
        print(f"📍 {i+1}. {b.name}")
        print(f"{'─' * 80}")
        print(f"   📂 Category: {b.category}")
        print(f"   ⭐ Rating: {b.rating} ({b.review_count} reviews)")
        print(f"   📍 Address: {b.address}")
        print(f"   📞 Phone: {b.phone}")
        print(f"   🌐 Website: {b.website_url or 'None'} (Status: {b.website_status})")
        print(f"   💰 Price: {b.price_range or 'N/A'}")
        
        # Service options
        if b.service_options:
            services = [k for k, v in b.service_options.items() if v]
            print(f"   🍽️  Services: {', '.join(services) if services else 'N/A'}")
        
        # Payments
        if b.payments:
            print(f"   💳 Payments: {', '.join(b.payments)}")
        
        # Parking
        if b.parking:
            print(f"   🅿️  Parking: {', '.join(b.parking)}")
        
        # Accessibility
        if b.accessibility:
            print(f"   ♿ Accessibility: {', '.join(b.accessibility[:2])}...")
        
        # Offerings
        if b.offerings:
            print(f"   ☕ Offerings: {', '.join(b.offerings)}")
        
        # Dining options
        if b.dining_options:
            print(f"   🍳 Dining: {', '.join(b.dining_options)}")
        
        # Review topics
        if b.review_topics:
            topics = [f"{k}({v})" for k, v in list(b.review_topics.items())[:5]]
            print(f"   🏷️  Topics: {', '.join(topics)}")
        
        # Rating distribution
        if b.rating_distribution:
            dist = " | ".join([f"{k}⭐:{v}" for k, v in b.rating_distribution.items()])
            print(f"   📊 Distribution: {dist}")
        
        # Reviews
        print(f"   📝 Reviews Collected: {len(b.reviews)}")
        if b.reviews and len(b.reviews) > 0:
            rev = b.reviews[0]
            author = rev.get("author", "Anonymous")
            is_guide = "🏅" if rev.get("is_local_guide") else ""
            rating = rev.get("rating", 0)
            text = rev.get("text", "")[:150]
            print(f"      └─ {is_guide}{author} ({rating}⭐): \"{text}...\"")
        
        # Photos
        print(f"   📷 Photos: {b.photo_count}")
        if b.photo_categories:
            print(f"      Categories: {', '.join(b.photo_categories[:5])}")
    
    print("\n" + "=" * 80)
    print("✅ SCRAPING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_scraper())
