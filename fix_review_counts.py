#!/usr/bin/env python3
"""
Fast re-scraper to fix review counts by searching business name + city.
Uses Playwright with parallel pages for speed.
"""

import asyncio
import json
import re
import csv
from pathlib import Path
from urllib.parse import quote
from playwright.async_api import async_playwright

DATA_FILE = Path(__file__).parent / "discovered_businesses.json"
CSV_FILE = Path(__file__).parent / "business_analysis.csv"


def build_search_url(name: str, city: str) -> str:
    """Build a Google Maps search URL."""
    query = f"{name} {city} Paraguay"
    return f"https://www.google.com/maps/search/{quote(query)}"


async def extract_business_data(page, name: str, city: str, timeout: int = 12000) -> dict:
    """Extract review count and rating from Google Maps search."""
    url = build_search_url(name, city)
    result = {"review_count": 0, "rating": None, "success": False}
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        await page.wait_for_timeout(2000)
        
        # Check if we landed on a business page directly or a list
        # If on business page, the main panel will have the details
        
        # Try to find review count
        content = await page.content()
        
        # Pattern 1: "(X reseñas)" or "(X reviews)"
        patterns = [
            r'\((\d[\d,\.]*)\s*(?:reseña|review)',  # (123 reseñas)
            r'(\d[\d,\.]*)\s*(?:reseña|review)',     # 123 reseñas
            r'aria-label="(\d[\d,\.]*)\s*(?:reseña|review)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for m in matches:
                try:
                    num = int(m.replace(',', '').replace('.', ''))
                    if 0 < num < 100000:  # Reasonable range
                        result["review_count"] = num
                        result["success"] = True
                        break
                except:
                    continue
            if result["review_count"] > 0:
                break
        
        # Try to find rating
        rating_patterns = [
            r'aria-label="([\d,\.]+)\s*(?:estrella|star)',
            r'<span[^>]*>([\d,\.]+)</span>\s*\([\d,\.]+\s*reseña',
        ]
        
        for pattern in rating_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for m in matches:
                try:
                    rating = float(m.replace(',', '.'))
                    if 1 <= rating <= 5:
                        result["rating"] = rating
                        break
                except:
                    continue
            if result["rating"]:
                break
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


async def fix_review_counts_fast():
    """Re-scrape review counts for businesses with parallel pages."""
    
    # Load data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        businesses = json.load(f)
    
    total = len(businesses)
    print(f"📦 Loaded {total} businesses")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='es-PY',
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Use multiple pages for speed
        NUM_PAGES = 4
        pages = [await context.new_page() for _ in range(NUM_PAGES)]
        
        fixed = 0
        skipped = 0
        errors = 0
        
        # Process in batches
        batch_size = NUM_PAGES
        
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch = list(enumerate(businesses[batch_start:batch_end], start=batch_start))
            
            # Create tasks
            tasks = []
            for page_idx, (biz_idx, biz) in enumerate(batch):
                page = pages[page_idx % NUM_PAGES]
                name = biz.get('name', '')
                city = biz.get('city', 'Asunción')
                tasks.append(extract_business_data(page, name, city))
            
            # Execute batch
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update data
            for (biz_idx, biz), result in zip(batch, results):
                if isinstance(result, Exception):
                    errors += 1
                    continue
                
                if result.get("success") and result.get("review_count", 0) > 0:
                    biz["review_count"] = result["review_count"]
                    if result.get("rating"):
                        biz["rating"] = result["rating"]
                    fixed += 1
                else:
                    skipped += 1
            
            # Progress
            progress = batch_end / total * 100
            print(f"\r⏳ {progress:.1f}% | Fixed: {fixed} | Skipped: {skipped} | Errors: {errors}", end="", flush=True)
            
            # Save every 50 batches
            if (batch_start // batch_size) % 50 == 0 and batch_start > 0:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(businesses, f, ensure_ascii=False, indent=2)
        
        await browser.close()
    
    print(f"\n\n✅ Completed!")
    print(f"   Fixed: {fixed}")
    print(f"   Skipped (no data found): {skipped}")
    print(f"   Errors: {errors}")
    
    # Final save
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(businesses, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved JSON to {DATA_FILE}")
    
    # Export CSV
    export_to_csv(businesses)
    
    # Stats
    review_counts = [b.get('review_count', 0) for b in businesses]
    unique = len(set(review_counts))
    print(f"\n📊 Unique review_count values: {unique}")
    print(f"📊 Max review count: {max(review_counts)}")
    print(f"📊 Non-zero review counts: {sum(1 for c in review_counts if c > 0)}")


def export_to_csv(businesses):
    """Export to analysis CSV."""
    
    fieldnames = [
        'index', 'name', 'category', 'category_group', 'address', 'city', 'neighborhood',
        'latitude', 'longitude', 'phone', 'website', 'rating', 'review_count',
        'photo_count', 'reviews_with_text', 'price_level',
        'has_phone', 'has_website', 'has_photos', 'needs_website',
        'data_completeness', 'overall_quality', 'engagement_level',
        'is_good_candidate', 'is_premium_candidate'
    ]
    
    category_groups = {
        'restaurant': 'Food & Beverage', 'cafe': 'Food & Beverage', 'bakery': 'Food & Beverage',
        'bar': 'Food & Beverage', 'food': 'Food & Beverage', 'coffee': 'Food & Beverage',
        'beauty_salon': 'Beauty & Personal Care', 'hair_care': 'Beauty & Personal Care',
        'spa': 'Beauty & Personal Care', 'barber': 'Beauty & Personal Care',
        'nail_salon': 'Beauty & Personal Care',
        'gym': 'Fitness', 'fitness': 'Fitness',
        'dentist': 'Health & Medical', 'doctor': 'Health & Medical', 'clinic': 'Health & Medical',
        'pharmacy': 'Health & Medical', 'hospital': 'Health & Medical',
        'veterinary': 'Pet Services', 'pet': 'Pet Services',
        'car_repair': 'Automotive', 'mechanic': 'Automotive', 'auto': 'Automotive',
        'clothing': 'Fashion & Retail', 'shoe': 'Fashion & Retail', 'fashion': 'Fashion & Retail',
        'sportswear': 'Fashion & Retail', 'accessories': 'Fashion & Retail',
    }
    
    rows = []
    for i, b in enumerate(businesses):
        cat = (b.get('category') or '').lower()
        cat_group = 'Other'
        for key, group in category_groups.items():
            if key in cat:
                cat_group = group
                break
        
        has_phone = bool(b.get('phone'))
        has_website = bool(b.get('website_url') or b.get('website'))
        has_photos = (b.get('photo_count') or 0) > 0
        review_count = b.get('review_count') or 0
        rating = b.get('rating') or 0
        photo_count = b.get('photo_count') or 0
        reviews_text = len(b.get('reviews') or [])
        
        completeness_fields = [
            bool(b.get('name')), bool(b.get('address')), has_phone,
            has_photos, rating > 0, review_count > 0
        ]
        data_completeness = sum(completeness_fields) / len(completeness_fields) * 100
        
        quality = min(10, (
            (rating / 5 * 3) +
            (min(photo_count, 10) / 10 * 2) +
            (min(review_count, 100) / 100 * 2) +
            (1 if has_phone else 0) +
            (1 if reviews_text > 0 else 0) +
            (1 if has_photos else 0)
        ))
        
        engagement = 'High' if review_count >= 50 else ('Medium' if review_count >= 10 else 'Low')
        is_good = rating >= 4.0 and photo_count >= 2 and review_count > 0
        is_premium = rating >= 4.5 and photo_count >= 5 and reviews_text >= 3
        
        rows.append({
            'index': i,
            'name': b.get('name', ''),
            'category': b.get('category', ''),
            'category_group': cat_group,
            'address': b.get('address', ''),
            'city': b.get('city', ''),
            'neighborhood': b.get('neighborhood', ''),
            'latitude': b.get('latitude', ''),
            'longitude': b.get('longitude', ''),
            'phone': b.get('phone', ''),
            'website': b.get('website_url') or b.get('website', ''),
            'rating': rating,
            'review_count': review_count,
            'photo_count': photo_count,
            'reviews_with_text': reviews_text,
            'price_level': b.get('price_level', ''),
            'has_phone': has_phone,
            'has_website': has_website,
            'has_photos': has_photos,
            'needs_website': not has_website,
            'data_completeness': round(data_completeness, 1),
            'overall_quality': round(quality, 1),
            'engagement_level': engagement,
            'is_good_candidate': is_good,
            'is_premium_candidate': is_premium
        })
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"📄 Exported CSV to {CSV_FILE}")


if __name__ == "__main__":
    asyncio.run(fix_review_counts_fast())
