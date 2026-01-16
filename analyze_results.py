#!/usr/bin/env python3
"""
Analyze scraped business data from Discovery Agent
"""
import json
from pathlib import Path

def analyze_results():
    data_file = Path(__file__).parent / "discovered_businesses.json"
    
    if not data_file.exists():
        print("No data file found!")
        return
    
    with open(data_file) as f:
        data = json.load(f)
    
    print("📊 DISCOVERY RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total businesses scraped: {len(data)}")
    print()
    
    # Count by website status
    no_website = [b for b in data if b.get('website_status') == 'none']
    social_only = [b for b in data if b.get('website_status') == 'social_only']
    has_website = [b for b in data if b.get('website_status') == 'active']
    
    print(f"🎯 LEADS (no website):     {len(no_website)}")
    print(f"📱 Social media only:      {len(social_only)}")
    print(f"🌐 Has website (skip):     {len(has_website)}")
    print()
    
    # By city
    cities = {}
    for b in data:
        city = b.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1
    
    print("📍 By Location:")
    for city, count in sorted(cities.items(), key=lambda x: -x[1]):
        print(f"   {city}: {count}")
    print()
    
    # By category
    categories = {}
    for b in data:
        cat = b.get('category', 'Unknown') or 'Unknown'
        categories[cat] = categories.get(cat, 0) + 1
    
    print("📂 By Category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"   {cat}: {count}")
    print()
    
    # Show top leads
    print("🎯 TOP 10 LEADS (businesses without websites):")
    print("-" * 50)
    for i, b in enumerate(no_website[:10], 1):
        name = b.get('name', 'N/A')[:40]
        city = b.get('city', 'N/A')
        phone = (b.get('phone') or '').strip() or 'No phone'
        cat = b.get('category', 'N/A') or 'N/A'
        rating = b.get('rating', 0)
        reviews = b.get('review_count', 0)
        
        print(f"{i}. {name}")
        print(f"   📍 {city} | ⭐ {rating} ({reviews} reseñas)")
        print(f"   📂 {cat}")
        print(f"   📞 {phone}")
        print()
    
    # Export leads to separate file
    leads_file = Path(__file__).parent / "leads.json"
    with open(leads_file, 'w', encoding='utf-8') as f:
        json.dump(no_website + social_only, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(no_website) + len(social_only)} leads to leads.json")

if __name__ == "__main__":
    analyze_results()
