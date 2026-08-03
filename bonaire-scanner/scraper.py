#!/usr/bin/env python3
"""
Bonaire Vastgoed Scanner — automatische scraper
Scrapt bonaire-brokers.com (incl. sold-status) + Casa Dushi
"""

import asyncio
import aiohttp
import json
import re
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
}

BB_BASE = 'https://bonaire-brokers.com'
CD_BASE = 'https://bonaire.casadushi.com'

BROKER_MAP = {
    're-max-paradise-homes': 'RE/MAX Paradise Homes',
    'q-villas-bonaire': 'Q-Villas Bonaire',
    'bonaire-realty': 'Bonaire Realty',
    'baerz-co': 'Baerz & Co',
    'karko-real-estate': 'Karko Real Estate',
    'nlc-real-estate': 'NLC Real Estate',
    'the-real-estate-guy': 'The Real Estate Guy',
    'sunbelt-realty': 'Sunbelt Realty',
    'keller-williams-bonaire': 'Keller Williams Bonaire',
    'harbourtown-real-estate': 'Harbourtown Real Estate',
    'bonaire-real-estate-group': 'Bonaire Real Estate Group',
    'caribbean-homes-bonaire': 'Caribbean Homes Bonaire',
    'lux-realty-bonaire': 'Lux Realty Bonaire',
    'rj-real-estate': 'RJ Real Estate',
    'bonne-bonaire': 'Bonne Bonaire',
}

CD_BROKER_MAP = {
    'bonaire_homes': 'Harbourtown Real Estate',
    'bonairehomes': 'Harbourtown Real Estate',
    'sunbelt': 'Sunbelt Realty',
    'caribbean_homes': 'Caribbean Homes Bonaire',
    'caribbeanhomes': 'Caribbean Homes Bonaire',
    'bonaire_realty': 'Bonaire Realty',
    'bonairerealty': 'Bonaire Realty',
    'bonaire_realestate_group': 'Bonaire Real Estate Group',
    'bonairerealestategroup': 'Bonaire Real Estate Group',
    'harbour_town': 'Harbourtown Real Estate',
    'harbourtown': 'Harbourtown Real Estate',
    'qvillas': 'Q-Villas Bonaire',
    'q-villas': 'Q-Villas Bonaire',
    'kw_bonaire': 'Keller Williams Bonaire',
    'kwbonaire': 'Keller Williams Bonaire',
    're/max': 'RE/MAX Paradise Homes',
    'remax': 'RE/MAX Paradise Homes',
}


def broker_from_slug(slug):
    for key, val in BROKER_MAP.items():
        if slug.startswith(key):
            return val
    return 'Privéverkoop'


def normalize_cd_broker(raw):
    r = (raw or '').lower().replace(' ', '').replace('_', '').replace('-', '')
    for key, val in CD_BROKER_MAP.items():
        if key.replace('_', '').replace('-', '').replace(' ', '') in r:
            return val
    return raw or 'Onbekend'


def parse_price(text):
    m = re.search(r'\$([\d,]+)', text)
    if not m:
        return None, None
    price_str = '$' + m.group(1)
    return int(m.group(1).replace(',', '')), price_str


async def fetch_text(session, url, extra_headers=None, retries=3):
    h = {**HEADERS, **(extra_headers or {})}
    for i in range(retries):
        try:
            async with session.get(url, headers=h,
                                   timeout=aiohttp.ClientTimeout(total=20)) as r:
                if r.status == 200:
                    return await r.text()
                print(f"  HTTP {r.status} for {url}")
                return None
        except Exception as e:
            if i == retries - 1:
                print(f"  Failed {url}: {e}")
                return None
            await asyncio.sleep(2 ** i)


# ─── BONAIRE BROKERS ─────────────────────────────────────────────────────────

async def scrape_bb_urls(session):
    """Haal alle listing-URLs op van bonaire-brokers.com (server-rendered)"""
    print("Scraping bonaire-brokers.com listings...")
    html = await fetch_text(session, f"{BB_BASE}/properties")
    if not html:
        return []

    soup = BeautifulSoup(html, 'html5lib')
    seen = set()
    listings = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if not re.match(r'/properties/[a-z0-9-]+$', href):
            continue
        url = BB_BASE + href
        if url in seen:
            continue
        seen.add(url)

        slug = href.split('/properties/')[-1]
        text = a.get_text(' ', strip=True)
        price, price_str = parse_price(text)

        # Titel: verwijder prijs + status-woorden
        title = re.sub(
            r'\$([\d,]+)|Price on Request|Te koop|Prijs op aanvraag|'
            r'For Sale|Sold|Pending|Verkocht',
            '', text
        ).strip(' —–-')
        title = re.sub(r'\s{2,}', ' ', title).strip()
        if len(title) < 2:
            title = ' '.join(w.capitalize() for w in slug.split('-')
                             if w not in BROKER_MAP)

        listings.append({
            'title': title,
            'price': price,
            'price_display': price_str,
            'url': url,
            'broker': broker_from_slug(slug),
            'source': 'bonaire-brokers.com',
            'sold': False,
        })

    print(f"  Gevonden: {len(listings)} BB listings")
    return listings


async def check_sold(session, listing, sem):
    """Haal individuele property-pagina op en check sold/pending status"""
    async with sem:
        html = await fetch_text(session, listing['url'])
        await asyncio.sleep(0.05)

        if not html:
            return listing

        # De property-pagina rendert "Sold" of "Pending" als platte tekst
        soup = BeautifulSoup(html, 'html5lib')
        page_text = soup.get_text()
        if re.search(r'\b(Sold|Pending|Verkocht)\b', page_text):
            return {**listing, 'sold': True}
        return listing


async def scrape_bb(session):
    """Volledige BB scrape incl. sold-status check"""
    listings = await scrape_bb_urls(session)
    if not listings:
        return []

    print(f"  Sold-status checken voor {len(listings)} listings "
          f"(~{len(listings)//15 + 1}s)...")
    sem = asyncio.Semaphore(15)
    results = await asyncio.gather(*[check_sold(session, l, sem) for l in listings])

    active = sum(1 for l in results if not l['sold'])
    sold = sum(1 for l in results if l['sold'])
    print(f"  BB resultaat: {active} actief, {sold} verkocht")
    return list(results)


# ─── CASA DUSHI ──────────────────────────────────────────────────────────────

def parse_rsc_payload(html):
    """Extraheer initialSaleListings uit de Next.js RSC payload"""
    # RSC payload zit in self.__next_f.push([1,"..."]) script-tags
    scripts = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)',
                         html, re.DOTALL)
    if not scripts:
        return []

    rsc_text = '\n'.join(scripts)

    # Zoek de key (dubbel-escaped in de JS-string)
    for key in ('initialSaleListings\\":', 'initialSaleListings":'):
        idx = rsc_text.find(key)
        if idx != -1:
            break
    else:
        print("  initialSaleListings niet gevonden in RSC payload")
        return []

    start = rsc_text.index('[', idx)
    depth, i, end = 0, start, start
    while i < len(rsc_text):
        c = rsc_text[i]
        if c == '\\' and i + 1 < len(rsc_text):
            i += 2
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1

    raw = rsc_text[start:end]
    unescaped = raw.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')

    try:
        return json.loads(unescaped)
    except json.JSONDecodeError as e:
        print(f"  JSON parse fout: {e}")
        return []


async def scrape_casadushi(session):
    """Scrape Casa Dushi via RSC payload (geen browser nodig)"""
    print("Scraping Casa Dushi...")

    # RSC payload ophalen — bevat alle 316 listings met volledige data
    rsc_headers = {
        'RSC': '1',
        'Next-Router-State-Tree': '%5B%22%22%2C%7B%7D%5D',
        'Next-Url': '/',
    }
    html = await fetch_text(session, f"{CD_BASE}/?_rsc=1",
                            extra_headers=rsc_headers)

    # Fallback: gewone pagina
    if not html or 'initialSaleListings' not in html:
        html = await fetch_text(session, CD_BASE)

    if not html:
        print("  Casa Dushi niet bereikbaar")
        return []

    items = parse_rsc_payload(html)
    if not items:
        print("  Geen items geparsed uit RSC payload")
        return []

    listings = []
    for item in items:
        if not isinstance(item, dict):
            continue

        price_raw = item.get('price') or item.get('priceRaw') or 0
        try:
            price = int(float(str(price_raw))) if price_raw else None
        except (ValueError, TypeError):
            price = None

        broker_raw = (item.get('broker') or item.get('realtor') or
                      item.get('brokerName') or '')
        broker = normalize_cd_broker(str(broker_raw))

        href = item.get('href') or item.get('slug') or ''
        url = f"{CD_BASE}/{href}" if href and not href.startswith('http') else href
        title = item.get('title') or item.get('name') or href

        listings.append({
            'title': title,
            'price': price,
            'price_display': f'${price:,}' if price else None,
            'url': url,
            'broker': broker,
            'source': 'casadushi',
            'sold': False,
            'beds': item.get('bedrooms') or item.get('beds'),
            'baths': item.get('bathrooms') or item.get('baths'),
            'type': item.get('listingType') or item.get('type'),
            'lat': item.get('lat'),
            'lng': item.get('lng'),
        })

    print(f"  Casa Dushi: {len(listings)} listings geparsed")
    return listings


# ─── DEDUPLICATIE ────────────────────────────────────────────────────────────

def norm(t):
    return re.sub(r'[^a-z0-9]', '', (t or '').lower())


def is_duplicate(cd_title, bb_titles_set, bb_norms):
    cn = norm(cd_title)
    if cn in bb_titles_set:
        return True
    for bn in bb_norms:
        if len(cn) > 5 and len(bn) > 5:
            if cn in bn or bn in cn:
                return True
            common = sum(1 for c in cn if c in bn)
            if common / max(len(cn), len(bn)) > 0.82:
                return True
    return False


def deduplicate(bb, cd):
    bb_norms = [norm(l['title']) for l in bb]
    bb_set = set(bb_norms)
    unique_cd = [l for l in cd if not is_duplicate(l['title'], bb_set, bb_norms)]
    print(f"  Dedup: {len(cd)} CD listings → {len(unique_cd)} uniek")
    return bb + unique_cd


# ─── MAIN ────────────────────────────────────────────────────────────────────

async def main():
    t0 = time.time()
    print(f"=== Bonaire Scraper gestart: {datetime.now():%Y-%m-%d %H:%M:%S} ===\n")

    async with aiohttp.ClientSession() as session:
        bb_task = scrape_bb(session)
        cd_task = scrape_casadushi(session)
        bb, cd = await asyncio.gather(bb_task, cd_task)

    combined = deduplicate(bb, cd)
    active = sum(1 for l in combined if not l.get('sold'))
    sold = sum(1 for l in combined if l.get('sold'))

    print(f"\n=== Resultaat ===")
    print(f"Totaal : {len(combined)}")
    print(f"Actief : {active}")
    print(f"Verkocht: {sold}")
    print(f"Tijd   : {time.time() - t0:.1f}s")

    Path('data').mkdir(exist_ok=True)
    with open('data/listings.json', 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    # Sla timestamp op
    with open('data/last_updated.txt', 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))

    print("✓ data/listings.json opgeslagen")


if __name__ == '__main__':
    asyncio.run(main())
