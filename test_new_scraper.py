#!/usr/bin/env python3
"""
Test script to verify the new MapsScraper fixes are working correctly.
Scrapes 10 businesses and displays the extracted data.
"""

import asyncio
import json
import logging
from agents.discovery.google_maps import MapsScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_scraper():
    """Test the new scraper fixes on 10 businesses"""
    
    print("\n" + "="*70)
    print("🧪 TESTING NEW MAPSSCRAPER FIXES")
    print("="*70)
    print("\nNew features being tested:")
    print("  1. Isolation Logic - Wait for correct business panel")
    print("  2. High-Resolution Images (1200x800)")
    print("  3. 5-Star Review Extraction (text > 40 chars)")
    print("  4. ARIA-Label Rating Extraction")
    print("  5. About Section & Plus Code")
    print("  6. Review Count tracking")
    print("="*70 + "\n")
    
    scraper = MapsScraper(
        headless=False,  # Visible browser for testing
        delay_min=2.0,
        delay_max=3.5,
        max_results_per_search=10,  # Only 10 for test
    )
    
    test_results = []
    
    try:
        await scraper.initialize()
        
        # Test with a simple search that should return good results
        test_searches = [
            ("restaurante", "Villa Morra, Asunción"),
        ]
        
        for query, location in test_searches:
            logger.info(f"Searching: {query} en {location}")
            
            results = await scraper.search_businesses(
                query=query,
                location=location,
                max_results=10
            )
            
            test_results.extend(results)
            logger.info(f"Found {len(results)} businesses")
        
        # Display results
        print("\n" + "="*70)
        print(f"📊 SCRAPED DATA FOR {len(test_results)} BUSINESSES")
        print("="*70)
        
        for i, business in enumerate(test_results):
            print(f"\n{'─'*70}")
            print(f"🏢 BUSINESS #{i+1}: {business.name}")
            print(f"{'─'*70}")
            
            # Basic Info
            print(f"  📍 Category:     {business.category or 'N/A'}")
            print(f"  📍 Address:      {business.address or 'N/A'}")
            print(f"  📍 City:         {business.city}")
            print(f"  📍 Plus Code:    {business.plus_code or 'N/A'}")
            print(f"  📞 Phone:        {business.phone or 'N/A'}")
            
            # Rating & Reviews (NEW FIXES)
            print(f"\n  ⭐ Rating:       {business.rating} / 5.0")
            print(f"  📝 Review Count: {business.review_count}")  # NEW FIELD
            
            # About Section (NEW FIX)
            if business.about_summary:
                about_preview = business.about_summary[:100] + "..." if len(business.about_summary) > 100 else business.about_summary
                print(f"  📄 About:        {about_preview}")
            else:
                print(f"  📄 About:        N/A")
            
            # Website Status
            print(f"\n  🌐 Has Website:  {business.has_website}")
            print(f"  🌐 Website URL:  {business.website_url or 'None'}")
            print(f"  🌐 Status:       {business.website_status}")
            
            # Photos (HIGH-RES FIX)
            print(f"\n  📸 Photo Count:  {business.photo_count}")
            print(f"  📸 URLs Found:   {len(business.photo_urls)}")
            if business.photo_urls:
                first_photo = business.photo_urls[0]
                # Check if high-res
                is_high_res = "w1200" in first_photo or "h800" in first_photo
                print(f"  📸 High-Res:     {'✅ YES' if is_high_res else '❌ NO'}")
                print(f"  📸 Sample URL:   {first_photo[:80]}...")
            
            # Reviews (5-STAR FILTER FIX)
            print(f"\n  💬 Reviews:      {len(business.reviews)} extracted")
            if business.reviews:
                for j, review in enumerate(business.reviews[:3]):
                    stars = review.get('rating', 0)
                    text = review.get('text', '')[:60]
                    author = review.get('author', 'Anonymous')
                    print(f"      [{j+1}] ⭐{stars} by {author[:15]}: \"{text}...\"")
                
                # Verify all are 5-star
                all_five_star = all(r.get('rating', 0) == 5 for r in business.reviews)
                print(f"      All 5-star: {'✅ YES' if all_five_star else '❌ NO'}")
            
            # Additional Data
            if business.social_media:
                print(f"\n  📱 Social Media: {list(business.social_media.keys())}")
            
            if business.service_options and any(business.service_options.values()):
                active = [k for k, v in business.service_options.items() if v]
                print(f"  🍽️  Services:     {active}")
        
        # Save test results to JSON for inspection
        output_file = "test_scraper_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in test_results], f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ TEST COMPLETE - {len(test_results)} businesses scraped")
        print(f"📁 Full data saved to: {output_file}")
        print(f"{'='*70}\n")
        
        # Summary of fixes verification
        print("\n📋 FIX VERIFICATION SUMMARY:")
        print("─"*40)
        
        # Check high-res images
        high_res_count = sum(1 for r in test_results if r.photo_urls and ("w1200" in r.photo_urls[0] or "h800" in r.photo_urls[0]))
        print(f"  High-Res Images:     {high_res_count}/{len(test_results)} businesses")
        
        # Check review counts tracked
        with_review_count = sum(1 for r in test_results if r.review_count > 0)
        print(f"  Review Count Tracked: {with_review_count}/{len(test_results)} businesses")
        
        # Check 5-star reviews
        five_star_only = sum(1 for r in test_results if r.reviews and all(rev.get('rating') == 5 for rev in r.reviews))
        with_reviews = sum(1 for r in test_results if r.reviews)
        print(f"  5-Star Reviews Only: {five_star_only}/{with_reviews} businesses with reviews")
        
        # Check about summaries
        with_about = sum(1 for r in test_results if r.about_summary)
        print(f"  About Sections:      {with_about}/{len(test_results)} businesses")
        
        # Check plus codes
        with_plus_code = sum(1 for r in test_results if r.plus_code)
        print(f"  Plus Codes:          {with_plus_code}/{len(test_results)} businesses")
        
        print("─"*40)
        
    finally:
        await scraper.close()
    
    return test_results


if __name__ == "__main__":
    asyncio.run(test_scraper())
