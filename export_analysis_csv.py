#!/usr/bin/env python3
"""
Export businesses to CSV for data analysis.
Includes computed fields to help identify the best business opportunities.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def load_businesses():
    """Load businesses from JSON file"""
    json_path = Path("datos_definitivos_final.json")
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def extract_analysis_data(business: dict, index: int) -> dict:
    """Extract all relevant fields for analysis"""
    
    # Basic info
    name = business.get('name', '')
    category = business.get('category', '')
    
    # Location
    address = business.get('address', '')
    city = business.get('city', '')
    neighborhood = business.get('neighborhood', '')
    
    # Contact
    phone = business.get('phone', '')
    website = business.get('website', '')
    
    # Ratings
    rating = business.get('rating', 0) or 0
    review_count = business.get('review_count', 0) or 0
    
    # Photos analysis
    photo_urls = business.get('photo_urls', []) or []
    num_photos = len(photo_urls)
    has_photos = num_photos > 0
    
    # Reviews analysis
    reviews = business.get('reviews', []) or []
    num_reviews_with_text = len(reviews)
    
    # Count reviews with photos
    reviews_with_photos = sum(1 for r in reviews if r.get('photo_url'))
    review_photos = [r.get('photo_url') for r in reviews if r.get('photo_url')]
    num_review_photos = len(review_photos)
    
    # Total images available
    total_images = num_photos + num_review_photos
    
    # Opening hours
    opening_hours = business.get('opening_hours', {}) or {}
    has_opening_hours = bool(opening_hours)
    days_with_hours = len(opening_hours) if opening_hours else 0
    
    # Additional data
    price_level = business.get('price_level', '')
    
    # Accessibility
    accessibility = business.get('accessibility', []) or []
    has_accessibility = len(accessibility) > 0
    accessibility_text = '; '.join(accessibility) if accessibility else ''
    
    # Amenities
    amenities = business.get('amenities', []) or []
    has_amenities = len(amenities) > 0
    amenities_text = '; '.join(amenities) if amenities else ''
    
    # Payments
    payments = business.get('payments', []) or []
    has_payments = len(payments) > 0
    payments_text = '; '.join(payments) if payments else ''
    
    # Parking
    parking = business.get('parking', []) or []
    has_parking = len(parking) > 0
    parking_text = '; '.join(parking) if parking else ''
    
    # Service options
    service_options = business.get('service_options', []) or []
    has_service_options = len(service_options) > 0
    service_options_text = '; '.join(service_options) if service_options else ''
    
    # Highlights
    highlights = business.get('highlights', []) or []
    has_highlights = len(highlights) > 0
    highlights_text = '; '.join(highlights) if highlights else ''
    
    # Coordinates
    latitude = business.get('latitude', '')
    longitude = business.get('longitude', '')
    has_coordinates = bool(latitude and longitude)
    
    # Plus code
    plus_code = business.get('plus_code', '')
    
    # Google Maps URL
    maps_url = business.get('maps_url', '')
    place_id = business.get('place_id', '')
    
    # Scraped timestamp
    scraped_at = business.get('scraped_at', '')
    
    # === COMPUTED QUALITY SCORES ===
    
    # Data completeness score (0-100)
    completeness_points = 0
    if name: completeness_points += 10
    if phone: completeness_points += 15
    if address: completeness_points += 10
    if website: completeness_points += 10
    if rating > 0: completeness_points += 10
    if has_photos: completeness_points += 15
    if has_opening_hours: completeness_points += 10
    if num_reviews_with_text > 0: completeness_points += 20
    data_completeness = completeness_points
    
    # Image quality score
    image_score = 0
    if num_photos >= 5: image_score = 3
    elif num_photos >= 3: image_score = 2
    elif num_photos >= 1: image_score = 1
    
    # Review quality score
    review_score = 0
    if num_reviews_with_text >= 5: review_score = 3
    elif num_reviews_with_text >= 3: review_score = 2
    elif num_reviews_with_text >= 1: review_score = 1
    
    # Rating quality (only if has reviews)
    rating_score = 0
    if review_count > 0:
        if rating >= 4.5: rating_score = 3
        elif rating >= 4.0: rating_score = 2
        elif rating >= 3.5: rating_score = 1
    
    # Overall quality score (0-10)
    overall_quality = (
        (data_completeness / 100) * 3 +  # Max 3 points
        image_score +                      # Max 3 points
        review_score +                     # Max 3 points
        (rating_score / 3)                 # Max 1 point
    )
    
    # Website potential (businesses without website = opportunity)
    needs_website = not website or website == ''
    
    # Engagement level (based on reviews)
    if review_count >= 100: engagement = 'High'
    elif review_count >= 30: engagement = 'Medium'
    elif review_count >= 5: engagement = 'Low'
    else: engagement = 'Very Low'
    
    # Category type for filtering
    category_lower = category.lower() if category else ''
    
    # Determine category group
    if any(x in category_lower for x in ['restaurant', 'parrilla', 'café', 'cafetería', 'pastelería', 'panadería']):
        category_group = 'Food & Beverage'
    elif any(x in category_lower for x in ['peluquería', 'barbería', 'salon', 'belleza', 'spa', 'estética']):
        category_group = 'Beauty & Personal Care'
    elif any(x in category_lower for x in ['veterinari', 'mascota', 'pet']):
        category_group = 'Pet Services'
    elif any(x in category_lower for x in ['dentist', 'odonto', 'médic', 'clinic', 'farmacia', 'botica']):
        category_group = 'Health & Medical'
    elif any(x in category_lower for x in ['taller', 'mecánic', 'auto']):
        category_group = 'Automotive'
    elif any(x in category_lower for x in ['gimnasio', 'gym', 'fitness', 'crossfit']):
        category_group = 'Fitness'
    elif any(x in category_lower for x in ['ropa', 'boutique', 'moda', 'tienda', 'zapater', 'calzado', 'joyería', 'accesorio']):
        category_group = 'Fashion & Retail'
    else:
        category_group = 'Other'
    
    # Best for landing page (composite score)
    is_good_candidate = (
        rating >= 4.0 and
        num_photos >= 2 and
        num_reviews_with_text >= 1 and
        has_opening_hours
    )
    
    # Premium candidate (excellent data)
    is_premium_candidate = (
        rating >= 4.5 and
        num_photos >= 5 and
        num_reviews_with_text >= 3 and
        has_opening_hours and
        phone
    )
    
    return {
        'index': index,
        'name': name,
        'category': category,
        'category_group': category_group,
        
        # Location
        'address': address,
        'city': city,
        'neighborhood': neighborhood,
        'latitude': latitude,
        'longitude': longitude,
        'has_coordinates': has_coordinates,
        'plus_code': plus_code,
        
        # Contact
        'phone': phone,
        'has_phone': bool(phone),
        'website': website,
        'has_website': bool(website),
        'needs_website': needs_website,
        
        # Ratings
        'rating': rating,
        'review_count': review_count,
        'engagement_level': engagement,
        
        # Photos
        'num_photos': num_photos,
        'has_photos': has_photos,
        'num_review_photos': num_review_photos,
        'total_images': total_images,
        
        # Reviews
        'num_reviews_with_text': num_reviews_with_text,
        'reviews_with_photos': reviews_with_photos,
        
        # Business details
        'price_level': price_level,
        'has_opening_hours': has_opening_hours,
        'days_with_hours': days_with_hours,
        
        # Features
        'has_accessibility': has_accessibility,
        'accessibility': accessibility_text,
        'has_amenities': has_amenities,
        'amenities': amenities_text,
        'has_payments': has_payments,
        'payments': payments_text,
        'has_parking': has_parking,
        'parking': parking_text,
        'has_service_options': has_service_options,
        'service_options': service_options_text,
        'has_highlights': has_highlights,
        'highlights': highlights_text,
        
        # Quality scores
        'data_completeness': data_completeness,
        'image_score': image_score,
        'review_score': review_score,
        'rating_score': rating_score,
        'overall_quality': round(overall_quality, 2),
        
        # Candidate flags
        'is_good_candidate': is_good_candidate,
        'is_premium_candidate': is_premium_candidate,
        
        # Links
        'maps_url': maps_url,
        'place_id': place_id,
        'scraped_at': scraped_at,
    }

def main():
    print("=" * 60)
    print("📊 Business Data Export for Analysis")
    print("=" * 60)
    
    # Load data
    businesses = load_businesses()
    print(f"\n📦 Loaded {len(businesses)} businesses")
    
    if not businesses:
        print("❌ No businesses found!")
        return
    
    # Extract analysis data
    analysis_data = []
    for i, business in enumerate(businesses):
        data = extract_analysis_data(business, i)
        analysis_data.append(data)
    
    # Export to CSV
    output_file = "business_analysis.csv"
    
    if analysis_data:
        fieldnames = analysis_data[0].keys()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analysis_data)
    
    print(f"\n✅ Exported to: {output_file}")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("📈 SUMMARY STATISTICS")
    print("=" * 60)
    
    total = len(analysis_data)
    
    # Basic counts
    with_phone = sum(1 for d in analysis_data if d['has_phone'])
    with_website = sum(1 for d in analysis_data if d['has_website'])
    needs_website = sum(1 for d in analysis_data if d['needs_website'])
    with_photos = sum(1 for d in analysis_data if d['has_photos'])
    with_reviews = sum(1 for d in analysis_data if d['num_reviews_with_text'] > 0)
    with_hours = sum(1 for d in analysis_data if d['has_opening_hours'])
    
    print(f"\n📱 Contact Info:")
    print(f"   With phone: {with_phone:,} ({with_phone/total*100:.1f}%)")
    print(f"   With website: {with_website:,} ({with_website/total*100:.1f}%)")
    print(f"   Needs website: {needs_website:,} ({needs_website/total*100:.1f}%)")
    
    print(f"\n📸 Media:")
    print(f"   With photos: {with_photos:,} ({with_photos/total*100:.1f}%)")
    print(f"   With review text: {with_reviews:,} ({with_reviews/total*100:.1f}%)")
    
    print(f"\n⏰ Business Info:")
    print(f"   With hours: {with_hours:,} ({with_hours/total*100:.1f}%)")
    
    # Rating distribution
    print(f"\n⭐ Rating Distribution:")
    rating_5 = sum(1 for d in analysis_data if d['rating'] >= 4.5)
    rating_4 = sum(1 for d in analysis_data if 4.0 <= d['rating'] < 4.5)
    rating_3 = sum(1 for d in analysis_data if 3.0 <= d['rating'] < 4.0)
    rating_low = sum(1 for d in analysis_data if 0 < d['rating'] < 3.0)
    rating_none = sum(1 for d in analysis_data if d['rating'] == 0)
    
    print(f"   ⭐⭐⭐⭐⭐ (4.5+): {rating_5:,}")
    print(f"   ⭐⭐⭐⭐ (4.0-4.4): {rating_4:,}")
    print(f"   ⭐⭐⭐ (3.0-3.9): {rating_3:,}")
    print(f"   ⭐⭐ (<3.0): {rating_low:,}")
    print(f"   No rating: {rating_none:,}")
    
    # Photo distribution
    print(f"\n📷 Photo Count Distribution:")
    photos_5plus = sum(1 for d in analysis_data if d['num_photos'] >= 5)
    photos_3_4 = sum(1 for d in analysis_data if 3 <= d['num_photos'] < 5)
    photos_1_2 = sum(1 for d in analysis_data if 1 <= d['num_photos'] < 3)
    photos_0 = sum(1 for d in analysis_data if d['num_photos'] == 0)
    
    print(f"   5+ photos: {photos_5plus:,}")
    print(f"   3-4 photos: {photos_3_4:,}")
    print(f"   1-2 photos: {photos_1_2:,}")
    print(f"   0 photos: {photos_0:,}")
    
    # Review text distribution
    print(f"\n💬 Reviews with Text Distribution:")
    reviews_5plus = sum(1 for d in analysis_data if d['num_reviews_with_text'] >= 5)
    reviews_3_4 = sum(1 for d in analysis_data if 3 <= d['num_reviews_with_text'] < 5)
    reviews_1_2 = sum(1 for d in analysis_data if 1 <= d['num_reviews_with_text'] < 3)
    reviews_0 = sum(1 for d in analysis_data if d['num_reviews_with_text'] == 0)
    
    print(f"   5+ reviews: {reviews_5plus:,}")
    print(f"   3-4 reviews: {reviews_3_4:,}")
    print(f"   1-2 reviews: {reviews_1_2:,}")
    print(f"   0 reviews: {reviews_0:,}")
    
    # Category groups
    print(f"\n📂 Category Groups:")
    from collections import Counter
    category_counts = Counter(d['category_group'] for d in analysis_data)
    for cat, count in category_counts.most_common():
        print(f"   {cat}: {count:,}")
    
    # Quality candidates
    print(f"\n🎯 LEAD QUALITY:")
    good_candidates = sum(1 for d in analysis_data if d['is_good_candidate'])
    premium_candidates = sum(1 for d in analysis_data if d['is_premium_candidate'])
    
    print(f"   Good candidates (4.0+ rating, 2+ photos, reviews, hours): {good_candidates:,}")
    print(f"   Premium candidates (4.5+ rating, 5+ photos, 3+ reviews): {premium_candidates:,}")
    
    # Top 20 by quality score
    print(f"\n🏆 TOP 20 BY OVERALL QUALITY:")
    print("-" * 80)
    sorted_data = sorted(analysis_data, key=lambda x: x['overall_quality'], reverse=True)[:20]
    
    for d in sorted_data:
        print(f"   [{d['index']:04d}] {d['name'][:40]:<40} | Q:{d['overall_quality']:.1f} | ⭐{d['rating']:.1f} | 📷{d['num_photos']} | 💬{d['num_reviews_with_text']}")
    
    print("\n" + "=" * 60)
    print(f"📁 Full data exported to: {output_file}")
    print("   Open in Excel/Google Sheets for detailed analysis")
    print("=" * 60)

if __name__ == "__main__":
    main()
