#!/usr/bin/env python3
"""Show the test results clearly"""
import json

with open('test_10_businesses.json', 'r') as f:
    data = json.load(f)

print('='*70)
print('📊 SCRAPER TEST RESULTS - 8 BUSINESSES COLLECTED')
print('='*70)

for i, b in enumerate(data, 1):
    print(f"\n#{i} {b['name']}")
    print(f"   ⭐ Rating: {b.get('rating', 'N/A')} ({b.get('review_count', 0)} reviews)")
    print(f"   📍 Plus Code: {b.get('plus_code', 'None')}")
    about = b.get('about_summary', 'None') or 'None'
    print(f"   📝 About: {about[:60]}...")
    
    # Photos
    photos = b.get('photo_urls', [])
    high_res = [p for p in photos if 'w1200' in p]
    print(f"   📷 Photos: {len(photos)} total ({len(high_res)} high-res w1200)")
    
    # Reviews
    reviews = b.get('reviews', [])
    five_star = [r for r in reviews if r.get('rating') == 5]
    print(f"   💬 5-Star Reviews: {len(five_star)} collected")

# Summary
print('\n' + '='*70)
print('📊 QUALITY METRICS:')
print('='*70)

total = len(data)
with_rating = sum(1 for b in data if b.get('rating'))
with_review_count = sum(1 for b in data if b.get('review_count'))
with_plus_code = sum(1 for b in data if b.get('plus_code'))
with_about = sum(1 for b in data if b.get('about_summary'))
with_high_res = sum(1 for b in data if any('w1200' in p for p in b.get('photo_urls', [])))
with_reviews = sum(1 for b in data if b.get('reviews'))

print(f"   ✅ Rating:        {with_rating}/{total} ({100*with_rating//total}%)")
print(f"   ✅ Review Count:  {with_review_count}/{total} ({100*with_review_count//total}%)")
print(f"   ✅ Plus Code:     {with_plus_code}/{total} ({100*with_plus_code//total}%)")
print(f"   ✅ About Summary: {with_about}/{total} ({100*with_about//total}%)")
print(f"   ✅ High-res:      {with_high_res}/{total} ({100*with_high_res//total}%)")
print(f"   ⚠️ 5-star Reviews: {with_reviews}/{total} ({100*with_reviews//total}%)")
print('='*70)
