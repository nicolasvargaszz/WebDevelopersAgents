#!/usr/bin/env python3
"""Simple Google Maps scraper - search based."""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright


async def scrape_businesses():
    print("🚀 Starting Google Maps Scraper...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="es-PY",
            timezone_id="America/Asuncion"
        )
        page = await context.new_page()
        
        # Go to Google Maps with search query
        search_query = "panadería en Asunción Paraguay"
        print(f"\n📍 Opening Google Maps with search: {search_query}")
        search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}?hl=es"
        await page.goto(search_url, wait_until="load", timeout=60000)
        await asyncio.sleep(4)
        
        # Accept cookies if present
        print("   Checking for cookie banner...")
        for sel in ['button[aria-label*="Aceptar"]', 'button:has-text("Aceptar todo")', 'button#L2AGLb', 'form[action*="consent"] button']:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    print("   ✅ Accepted cookies")
                    await asyncio.sleep(2)
                    break
            except:
                continue
        
        # Wait a bit more for maps to fully load
        print(f"\n🔍 Loading search results...")
        await asyncio.sleep(3)
        
        # Take screenshot to debug
        await page.screenshot(path="maps_debug.png")
        print("   📸 Screenshot saved to maps_debug.png")
        
        # Try different selectors for search box
        search_box = None
        for selector in ['input#searchboxinput', 'input[name="q"]', 'input[aria-label*="Buscar"]']:
            try:
                search_box = await page.query_selector(selector)
                if search_box:
                    print(f"   Found search box with: {selector}")
                    break
            except:
                continue
        # We already navigated with search, so skip search box interaction
        # Just wait for results to load
        
        # Wait for results feed - try multiple selectors
        print("   Waiting for results feed...")
        feed = None
        for feed_sel in ['div[role="feed"]', 'div.Nv2PK', 'div[role="main"] div[aria-label*="Results"]']:
            try:
                feed = await page.wait_for_selector(feed_sel, timeout=10000, state="attached")
                if feed:
                    print(f"   ✓ Found feed with: {feed_sel}")
                    break
            except:
                continue
        
        if not feed:
            print("   ⚠️ Could not find results feed, checking page content...")
            content = await page.content()
            if "hfpxzc" in content:
                print("   ✓ Found business links in page")
            else:
                await page.screenshot(path="maps_no_feed.png")
                print("   ❌ No feed found, screenshot saved")
        
        await asyncio.sleep(2)
        
        # Scroll to load results - use page scroll if feed not found
        scroll_target = feed if feed else page
        if feed:
            for _ in range(3):
                await feed.evaluate("el => el.scrollBy(0, 500)")
                await asyncio.sleep(1)
        else:
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(2)
        
        # Get result links
        result_links = await page.query_selector_all('a.hfpxzc')
        print(f"   Found {len(result_links)} results")
        
        all_businesses = []
        
        # Process first 10
        for i, link in enumerate(result_links[:10]):
            try:
                print(f"\n🏪 [{i+1}/10] Clicking business...")
                
                # Click on business
                await link.click()
                await asyncio.sleep(2)
                
                # Wait for panel to load
                await page.wait_for_selector('h1.DUwDvf', state="attached", timeout=8000)
                await asyncio.sleep(1)
                
                business = {}
                
                # Name
                name_el = await page.query_selector('h1.DUwDvf')
                business["name"] = (await name_el.inner_text()).strip() if name_el else "Unknown"
                print(f"   📍 {business['name']}")
                
                # Category
                cat_el = await page.query_selector('button[jsaction*="category"]')
                business["category"] = await cat_el.inner_text() if cat_el else None
                
                # Rating & Review Count
                rating_container = await page.query_selector('div.F7nice')
                if rating_container:
                    rating_text = await rating_container.inner_text()
                    # "4,7(236)"
                    match = re.search(r'([\d,\.]+)\s*\((\d+)', rating_text.replace(".", ""))
                    if match:
                        business["rating"] = float(match.group(1).replace(",", "."))
                        business["review_count"] = int(match.group(2))
                    else:
                        business["rating"] = 0
                        business["review_count"] = 0
                else:
                    business["rating"] = 0
                    business["review_count"] = 0
                
                # Try aria-label for better review count
                rating_span = await page.query_selector('span[aria-label*="estrellas"]')
                if rating_span:
                    aria = await rating_span.get_attribute("aria-label") or ""
                    r_match = re.search(r'([\d,\.]+)\s*estrellas?', aria)
                    rv_match = re.search(r'(\d[\d\.]*)\s*reseñas?', aria.replace(".", ""))
                    if r_match:
                        business["rating"] = float(r_match.group(1).replace(",", "."))
                    if rv_match:
                        business["review_count"] = int(rv_match.group(1).replace(".", ""))
                
                # Address
                addr_el = await page.query_selector('button[data-item-id="address"] div.Io6YTe')
                business["address"] = await addr_el.inner_text() if addr_el else None
                
                # Phone
                phone_el = await page.query_selector('button[data-item-id*="phone"] div.Io6YTe')
                business["phone"] = await phone_el.inner_text() if phone_el else None
                
                # Website
                web_el = await page.query_selector('a[data-item-id="authority"]')
                business["website"] = await web_el.get_attribute("href") if web_el else None
                
                # Price
                price_el = await page.query_selector('span.mgr77e span')
                business["price_range"] = await price_el.inner_text() if price_el else None
                
                # Open status
                status_el = await page.query_selector('span.ZDu9vd span')
                business["open_status"] = await status_el.inner_text() if status_el else None
                
                # Service options
                service_options = {"dine_in": False, "takeout": False, "delivery": False}
                service_els = await page.query_selector_all('div.LTs0Rc')
                for el in service_els:
                    aria = (await el.get_attribute("aria-label") or "").lower()
                    if "consumo" in aria or "lugar" in aria:
                        service_options["dine_in"] = "ofrece" in aria
                    if "llevar" in aria:
                        service_options["takeout"] = "ofrece" in aria
                    if "domicilio" in aria:
                        service_options["delivery"] = "ofrece" in aria
                business["service_options"] = service_options
                
                # Review topics
                review_topics = {}
                topic_btns = await page.query_selector_all('button.e2moi[aria-label*="mencionado"]')
                for btn in topic_btns[:8]:
                    aria = await btn.get_attribute("aria-label") or ""
                    match = re.match(r'([^,]+),\s*mencionado en\s*(\d+)', aria)
                    if match:
                        review_topics[match.group(1).strip()] = int(match.group(2))
                business["review_topics"] = review_topics
                
                # Rating distribution
                rating_dist = {}
                dist_rows = await page.query_selector_all('tr.BHOKXe')
                for row in dist_rows:
                    aria = await row.get_attribute("aria-label") or ""
                    match = re.search(r'(\d+)\s*estrellas?,.*?(\d+)\s*reseñas?', aria)
                    if match:
                        rating_dist[match.group(1)] = int(match.group(2))
                business["rating_distribution"] = rating_dist
                
                # Top reviews
                reviews = []
                review_cards = await page.query_selector_all('div.jftiEf[data-review-id]')
                for card in review_cards[:5]:
                    try:
                        author_el = await card.query_selector('div.d4r55')
                        info_el = await card.query_selector('div.RfnDt')
                        rating_el = await card.query_selector('span.kvMYJc')
                        date_el = await card.query_selector('span.rsqaWe')
                        text_el = await card.query_selector('span.wiI7pd')
                        
                        author = await author_el.inner_text() if author_el else "Anon"
                        info = await info_el.inner_text() if info_el else ""
                        date = await date_el.inner_text() if date_el else ""
                        text = await text_el.inner_text() if text_el else ""
                        
                        stars = 0
                        if rating_el:
                            aria = await rating_el.get_attribute("aria-label") or ""
                            m = re.search(r'(\d+)', aria)
                            stars = int(m.group(1)) if m else 0
                        
                        reviews.append({
                            "author": author,
                            "is_local_guide": "local guide" in info.lower(),
                            "rating": stars,
                            "date": date,
                            "text": text[:400]
                        })
                    except:
                        continue
                business["reviews"] = reviews
                
                # ========== MENU EXTRACTION ==========
                menu_data = {
                    "menu_link": None,
                    "menu_items": [],
                    "menu_images": [],
                    "popular_dishes": []
                }
                
                try:
                    # 1. Get menu link if available
                    menu_link_el = await page.query_selector('a[data-item-id="menu"], a[aria-label*="Carta"], a[aria-label*="Menú"]')
                    if menu_link_el:
                        menu_data["menu_link"] = await menu_link_el.get_attribute("href")
                        print(f"   📋 Found menu link")
                    
                    # 2. Try to click on "Carta" or "Menú" tab to see menu items
                    menu_tab = await page.query_selector('button[aria-label*="Carta"], button[data-tab-index][aria-label*="Menú"]')
                    if menu_tab:
                        await menu_tab.click()
                        await asyncio.sleep(2)
                        print(f"   📋 Clicked menu tab")
                        
                        # Extract menu items (name, price, description)
                        # Google Maps shows menu items in different formats
                        menu_items = []
                        
                        # Format 1: Menu items with price in structured cards
                        menu_cards = await page.query_selector_all('div[data-index] div.rogA2c, div.m6QErb div.Io6YTe')
                        for card in menu_cards[:30]:
                            try:
                                item_text = await card.inner_text()
                                if item_text and len(item_text) > 2:
                                    # Try to extract price from text
                                    price_match = re.search(r'[₲$€]\s*[\d\.,]+|[\d\.,]+\s*[₲$€]|[\d\.]+\.000', item_text)
                                    price = price_match.group(0) if price_match else None
                                    name = re.sub(r'[₲$€]\s*[\d\.,]+|[\d\.,]+\s*[₲$€]', '', item_text).strip()
                                    if name:
                                        menu_items.append({"name": name[:100], "price": price})
                            except:
                                continue
                        
                        # Format 2: Menu sections with items
                        menu_sections = await page.query_selector_all('div.fontHeadlineSmall, h3.fontHeadlineSmall')
                        for section in menu_sections:
                            try:
                                section_name = await section.inner_text()
                                if section_name:
                                    menu_items.append({"section": section_name.strip()})
                            except:
                                continue
                        
                        # Format 3: Individual menu item rows
                        item_rows = await page.query_selector_all('div.m6QErb button[aria-label], div.m6QErb div[role="button"]')
                        for row in item_rows[:20]:
                            try:
                                aria = await row.get_attribute("aria-label")
                                if aria:
                                    # Parse "Empanada de carne, 5.000 ₲" format
                                    price_match = re.search(r'[₲$€]\s*[\d\.,]+|[\d\.,]+\s*[₲$€]|[\d\.]+\.000', aria)
                                    price = price_match.group(0) if price_match else None
                                    name = re.sub(r',?\s*[₲$€]?\s*[\d\.,]+\s*[₲$€]?', '', aria).strip()
                                    if name and len(name) > 2 and name not in [m.get("name") for m in menu_items]:
                                        menu_items.append({"name": name[:100], "price": price})
                            except:
                                continue
                        
                        menu_data["menu_items"] = menu_items[:25]  # Limit to 25 items
                        
                        # Get menu images
                        menu_images = []
                        img_els = await page.query_selector_all('img[src*="googleusercontent"], img.YQ4gaf')
                        for img in img_els[:10]:
                            try:
                                src = await img.get_attribute("src")
                                if src and "googleusercontent" in src and src not in menu_images:
                                    menu_images.append(src)
                            except:
                                continue
                        menu_data["menu_images"] = menu_images
                        
                        # Go back to main tab
                        back_btn = await page.query_selector('button[data-tab-index="0"], button[aria-label*="Descripción"]')
                        if back_btn:
                            await back_btn.click()
                            await asyncio.sleep(0.5)
                    
                    # 3. Get popular dishes from main page (if visible)
                    popular_dishes = []
                    dish_els = await page.query_selector_all('div.m6QErb button.M0S7ae, div[data-index] div.fontBodyMedium')
                    for dish_el in dish_els[:10]:
                        try:
                            dish_text = await dish_el.inner_text()
                            if dish_text and len(dish_text) > 3:
                                price_match = re.search(r'[₲$€]\s*[\d\.,]+|[\d\.,]+\s*[₲$€]', dish_text)
                                price = price_match.group(0) if price_match else None
                                name = re.sub(r'[₲$€]\s*[\d\.,]+', '', dish_text).strip()
                                if name and len(name) > 2:
                                    popular_dishes.append({"name": name[:80], "price": price})
                        except:
                            continue
                    menu_data["popular_dishes"] = popular_dishes
                    
                except Exception as e:
                    print(f"   ⚠️ Menu extraction error: {e}")
                
                business["menu"] = menu_data
                
                # ========== INFO TAB (Payments/Parking) ==========
                # Try Info tab for payments/parking
                try:
                    info_tab = await page.query_selector('button[aria-label*="Información sobre"]')
                    if info_tab:
                        await info_tab.click()
                        await asyncio.sleep(1.5)
                        
                        payments = []
                        parking = []
                        accessibility = []
                        
                        sections = await page.query_selector_all('div.iP2t7d')
                        for section in sections:
                            title_el = await section.query_selector('h2.iL3Qke')
                            if not title_el:
                                continue
                            title = (await title_el.inner_text()).lower()
                            
                            items = []
                            item_els = await section.query_selector_all('li.hpLkke')
                            for item_el in item_els:
                                span = await item_el.query_selector('span:not(.google-symbols)')
                                if span:
                                    txt = await span.inner_text()
                                    if txt:
                                        items.append(txt.strip())
                            
                            if 'pago' in title:
                                payments = items
                            elif 'estacionamiento' in title:
                                parking = items
                            elif 'accesibilidad' in title:
                                accessibility = items
                        
                        business["payments"] = payments
                        business["parking"] = parking
                        business["accessibility"] = accessibility
                        
                        # Go back
                        back_tab = await page.query_selector('button[data-tab-index="0"]')
                        if back_tab:
                            await back_tab.click()
                            await asyncio.sleep(0.5)
                except:
                    business["payments"] = []
                    business["parking"] = []
                    business["accessibility"] = []
                
                business["scraped_at"] = datetime.now().isoformat()
                all_businesses.append(business)
                
                print(f"   ⭐ {business['rating']} ({business['review_count']} reviews)")
                
                # Go back to results
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
                continue
        
        await browser.close()
    
    # Save results
    with open("test_scrape_10.json", "w", encoding="utf-8") as f:
        json.dump(all_businesses, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ SAVED {len(all_businesses)} businesses to test_scrape_10.json")
    print(f"{'='*80}")
    
    # Print summary
    for i, b in enumerate(all_businesses):
        print(f"\n{'─'*80}")
        print(f"📍 {i+1}. {b['name']}")
        print(f"   ⭐ Rating: {b['rating']} ({b['review_count']} reviews)")
        print(f"   📂 Category: {b.get('category')}")
        print(f"   📍 Address: {b.get('address')}")
        print(f"   📞 Phone: {b.get('phone')}")
        print(f"   🌐 Website: {b.get('website', 'None')[:50] if b.get('website') else 'None'}...")
        print(f"   🕐 Status: {b.get('open_status')}")
        
        if b.get('service_options'):
            svcs = [k for k,v in b['service_options'].items() if v]
            print(f"   🍽️  Services: {', '.join(svcs) if svcs else 'N/A'}")
        
        if b.get('payments'):
            print(f"   💳 Payments: {', '.join(b['payments'][:3])}")
        
        if b.get('parking'):
            print(f"   🅿️  Parking: {', '.join(b['parking'][:2])}")
        
        if b.get('review_topics'):
            topics = [f"{k}({v})" for k,v in list(b['review_topics'].items())[:4]]
            print(f"   🏷️  Topics: {', '.join(topics)}")
        
        if b.get('rating_distribution'):
            dist = [f"{k}⭐:{v}" for k,v in b['rating_distribution'].items()]
            print(f"   📊 Distribution: {' | '.join(dist)}")
        
        # MENU DATA
        menu = b.get('menu', {})
        if menu:
            if menu.get('menu_link'):
                print(f"   📋 Menu Link: {menu['menu_link'][:60]}...")
            if menu.get('menu_items'):
                print(f"   🍽️  Menu Items: {len(menu['menu_items'])} items found")
                for item in menu['menu_items'][:5]:
                    if 'section' in item:
                        print(f"      📂 [{item['section']}]")
                    else:
                        price_str = f" - {item['price']}" if item.get('price') else ""
                        print(f"      • {item['name'][:50]}{price_str}")
            if menu.get('menu_images'):
                print(f"   🖼️  Menu Images: {len(menu['menu_images'])} images")
            if menu.get('popular_dishes'):
                dishes = [f"{d['name'][:20]}" for d in menu['popular_dishes'][:3]]
                print(f"   🌟 Popular: {', '.join(dishes)}")
        
        if b.get('reviews'):
            print(f"   📝 Reviews: {len(b['reviews'])} collected")
            if b['reviews']:
                r = b['reviews'][0]
                g = "🏅" if r.get('is_local_guide') else ""
                print(f"      └─ {g}{r['author']} ({r['rating']}⭐): \"{r['text'][:80]}...\"")


if __name__ == "__main__":
    asyncio.run(scrape_businesses())
