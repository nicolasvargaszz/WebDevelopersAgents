#!/usr/bin/env python3
"""Export discovered businesses JSON to CSV format."""

import json
import csv
from pathlib import Path

def main():
    # Load JSON data
    json_path = Path("discovered_businesses.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get all unique keys from all records
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    # Sort keys for consistent column order
    columns = sorted(list(all_keys))

    # Print summary
    print(f'Total businesses: {len(data)}')
    print(f'Total columns: {len(columns)}')
    print(f'\n📊 All columns collected:')
    for i, col in enumerate(columns, 1):
        print(f'  {i:2}. {col}')

    # Count businesses without websites
    no_website = sum(1 for b in data if not b.get('has_website', True))
    print(f'\n🎯 Businesses WITHOUT website (qualified leads): {no_website}')
    print(f'🌐 Businesses WITH website: {len(data) - no_website}')

    # Category breakdown
    categories = {}
    for b in data:
        cat = b.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print(f'\n📁 Top 15 categories:')
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:15]:
        print(f'  {count:4} - {cat}')

    # Write CSV
    csv_path = Path("discovered_businesses.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for item in data:
            # Convert lists to strings for CSV
            row = {}
            for k, v in item.items():
                if isinstance(v, list):
                    row[k] = '; '.join(str(x) for x in v)
                else:
                    row[k] = v
            writer.writerow(row)

    print(f'\n✅ CSV file created: {csv_path.absolute()}')
    print(f'   File size: {csv_path.stat().st_size / 1024:.1f} KB')

if __name__ == "__main__":
    main()
