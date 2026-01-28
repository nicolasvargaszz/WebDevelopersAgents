#!/usr/bin/env python3
"""Check menu and reviews data in discovered businesses."""

import json

with open('discovered_businesses.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check menu and review fields
menu_link_count = sum(1 for b in data if b.get('menu_link'))
reviews_count = sum(1 for b in data if b.get('reviews'))
review_topics_count = sum(1 for b in data if b.get('review_topics'))

print('=' * 60)
print('MENU & REVIEWS DATA CHECK')
print('=' * 60)

print(f'\nTotal businesses: {len(data)}')
print(f'\nMENU DATA:')
print(f'  - menu_link:       {menu_link_count} businesses have menu links')

print(f'\nREVIEWS DATA:')
print(f'  - reviews:         {reviews_count} businesses have reviews')
print(f'  - review_topics:   {review_topics_count} businesses have review topics')

# Show sample with reviews
print('\n' + '-' * 60)
print('SAMPLE BUSINESS WITH REVIEWS:')
print('-' * 60)

for b in data:
    if b.get('reviews'):
        print(f'\nBusiness: {b.get("name")}')
        print(f'Category: {b.get("category")}')
        print(f'Rating: {b.get("rating")} ({b.get("review_count")} reviews)')
        
        reviews = b.get('reviews', [])
        print(f'\nReviews saved: {len(reviews) if isinstance(reviews, list) else "N/A"} reviews')
        
        if reviews and isinstance(reviews, list) and len(reviews) > 0:
            print('\nSample Review:')
            r = reviews[0]
            if isinstance(r, dict):
                print(f'  Author: {r.get("author", "N/A")}')
                print(f'  Rating: {r.get("rating", "N/A")}')
                print(f'  Time: {r.get("time", "N/A")}')
                text = r.get('text', 'N/A')
                if text and len(str(text)) > 200:
                    print(f'  Text: {text[:200]}...')
                else:
                    print(f'  Text: {text}')
            else:
                print(f'  {str(r)[:300]}')
        
        if b.get('review_topics'):
            print(f'\nReview Topics: {b.get("review_topics")}')
        break
else:
    print('\nNo businesses with reviews found in the data.')

# Show sample with menu
print('\n' + '-' * 60)
print('SAMPLE BUSINESS WITH MENU:')
print('-' * 60)

for b in data:
    if b.get('menu_link'):
        print(f'\nBusiness: {b.get("name")}')
        print(f'Category: {b.get("category")}')
        print(f'Menu Link: {b.get("menu_link")}')
        break
else:
    print('\nNo businesses with menu links found in the data.')

print('\n' + '=' * 60)
