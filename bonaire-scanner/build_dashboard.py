#!/usr/bin/env python3
"""Genereert bonaire-scanner.com dashboard (index.html) vanuit data/listings.json"""

import json
import datetime
from pathlib import Path

DATA_FILE = Path('data/listings.json')
OUT_FILE = Path('index.html')

if not DATA_FILE.exists():
    print("data/listings.json niet gevonden — voer eerst scraper.py uit")
    exit(1)

with open(DATA_FILE) as f:
    all_listings = json.load(f)

try:
    last_updated = Path('data/last_updated.txt').read_text().strip()
except FileNotFoundError:
    last_updated = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

BROKER_COLORS = {
    'RE/MAX Paradise Homes': '#e53e3e',
    'Sunbelt Realty': '#dd6b20',
    'Karko Real Estate': '#d69e2e',
    'Q-Villas Bonaire': '#38a169',
    'The Real Estate Guy': '#319795',
    'Bonaire Realty': '#3182ce',
    'Harbourtown Real Estate': '#805ad5',
    'Bonaire Real Estate Group': '#d53f8c',
    'Caribbean Homes Bonaire': '#e07070',
    'Keller Williams Bonaire': '#dd6b20',
    'Lux Realty Bonaire': '#56a56a',
    'RJ Real Estate': '#2d9fb5',
    'Baerz & Co': '#4a8dd4',
    'NLC Real Estate': '#9070d0',
    'Bonne Bonaire': '#7b2d8b',
    'Privéverkoop': '#10b981',
    'Onbekend': '#aaaaaa',
}

FACEBOOK_SOURCES = {
    'groups': [
        {'name': 'Bonaire Housing', 'url': 'https://www.facebook.com/groups/1431665287083633/', 'members': '5,1k', 'posts': '4/dag'},
        {'name': 'Woonruimte aangeboden/gezocht Bonaire', 'url': 'https://www.facebook.com/groups/734192220001499/', 'members': '6,2k', 'posts': '2/dag'},
        {'name': 'Real Estate Bonaire', 'url': 'https://www.facebook.com/groups/420372482625777/', 'members': '1k', 'posts': ''},
        {'name': 'Bouwen op Bonaire', 'url': 'https://www.facebook.com/groups/290871973400525/', 'members': '2,5k', 'posts': ''},
        {'name': 'Bonaire House for rent', 'url': 'https://www.facebook.com/groups/792549405822085/', 'members': '13k', 'posts': '9/dag'},
    ],
    'searches': [
        {'label': 'woning te koop bonaire', 'url': 'https://www.facebook.com/search/posts/?q=woning%20te%20koop%20bonaire'},
        {'label': 'huis te koop bonaire', 'url': 'https://www.facebook.com/search/posts/?q=huis%20te%20koop%20bonaire'},
        {'label': 'real estate bonaire', 'url': 'https://www.facebook.com/search/posts/?q=real%20estate%20bonaire'},
        {'label': 'vastgoed bonaire', 'url': 'https://www.facebook.com/search/posts/?q=vastgoed%20bonaire'},
        {'label': 'te koop bonaire eigenaar', 'url': 'https://www.facebook.com/search/posts/?q=te+koop+bonaire+eigenaar'},
    ],
}

OTHER_SOURCES = [
    {'name': 'Casa Dushi — 2e aggregator', 'url': 'https://bonaire.casadushi.com/', 'desc': '316 listings van alle Bonaire makelaars'},
    {'name': '7th Heaven Properties', 'url': 'https://www.7thheavenproperties.com/real-estate/bonaire/', 'desc': '53 Bonaire listings incl. internationale kopers'},
    {'name': "Sotheby's Realty NL — Bonaire", 'url': 'https://sothebysrealty.nl/en/internationaal-aanbod/bonaire-villas-en-luxe-huizen-te-koop/', 'desc': 'Luxe listings via internationaal netwerk'},
    {'name': 'TKDE — privéverkoop', 'url': 'https://bonaire-brokers.com/nl/properties?fsbo=1', 'desc': 'Eigenaren die zonder makelaar verkopen'},
    {'name': 'Instagram #bonairerealestate', 'url': 'https://www.instagram.com/explore/tags/bonairerealestate/', 'desc': 'Recente posts + privé-aanbod'},
    {'name': 'Marktplaats — zoek "bonaire koop"', 'url': 'https://www.marktplaats.nl/q/bonaire+koop/', 'desc': 'Incidenteel privé-aanbod'},
]

active = [l for l in all_listings if not l.get('sold', False)]
sold_count = len(all_listings) - len(active)
with_price = sum(1 for l in active if l.get('price'))
brokers_count = len(set(l['broker'] for l in active))
sources_cd = sum(1 for l in active if l.get('source') == 'casadushi')
sources_bb = sum(1 for l in active if l.get('source') != 'casadushi')

listings_js = json.dumps(all_listings, ensure_ascii=False)

fb_groups_html = ''.join([
    f'<a class="fb-source" href="{g["url"]}" target="_blank" rel="noopener">'
    f'<span class="fb-icon">👥</span>'
    f'<span class="fb-name">{g["name"]}</span>'
    f'<span class="fb-meta">{g["members"]} leden{" · " + g["posts"] if g["posts"] else ""}</span>'
    f'</a>'
    for g in FACEBOOK_SOURCES['groups']
])
fb_searches_html = ''.join([
    f'<a class="fb-search-btn" href="{s["url"]}" target="_blank" rel="noopener">🔍 {s["label"]}</a>'
    for s in FACEBOOK_SOURCES['searches']
])
other_sources_html = ''.join([
    f'<a class="other-source" href="{s["url"]}" target="_blank" rel="noopener">'
    f'<span class="other-name">{s["name"]}</span>'
    f'<span class="other-desc">{s["desc"]}</span>'
    f'</a>'
    for s in OTHER_SOURCES
])

html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bonaire Vastgoed Scanner — bonaire-scanner.com</title>
<meta name="description" content="Compleet overzicht van alle woningen te koop op Bonaire. {len(active)} actuele listings van alle makelaars, dagelijks bijgewerkt.">
<meta property="og:title" content="Bonaire Vastgoed Scanner">
<meta property="og:description" content="{len(active)} woningen te koop op Bonaire — dagelijks bijgewerkt">
<meta property="og:url" content="https://bonaire-scanner.com">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a2332; }}
  .header {{
    background: linear-gradient(135deg, #0a3d62 0%, #1e6b9e 100%);
    color: white; padding: 24px 32px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;
  }}
  .header h1 {{ font-size: 1.6rem; font-weight: 700; }}
  .header p {{ font-size: 0.9rem; opacity: 0.85; margin-top: 4px; }}
  .header-stats {{ display: flex; gap: 24px; }}
  .stat {{ text-align: center; }}
  .stat .num {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
  .stat .lbl {{ font-size: 0.75rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }}
  .controls {{
    background: white; padding: 16px 32px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  }}
  .search-box {{ flex: 1; min-width: 200px; padding: 8px 14px; border: 1.5px solid #cbd5e0; border-radius: 8px; font-size: 0.9rem; outline: none; }}
  .search-box:focus {{ border-color: #1e6b9e; }}
  select {{ padding: 8px 12px; border: 1.5px solid #cbd5e0; border-radius: 8px; font-size: 0.875rem; background: white; cursor: pointer; outline: none; }}
  select:focus {{ border-color: #1e6b9e; }}
  .segments {{ padding: 20px 32px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
  .seg-btn {{ padding: 7px 16px; border: 2px solid #cbd5e0; border-radius: 20px; background: white; cursor: pointer; font-size: 0.82rem; font-weight: 600; color: #4a5568; transition: all 0.15s; white-space: nowrap; }}
  .seg-btn:hover {{ border-color: #1e6b9e; color: #1e6b9e; }}
  .seg-btn.active {{ background: #1e6b9e; border-color: #1e6b9e; color: white; }}
  .seg-btn .count {{ display: inline-block; background: rgba(255,255,255,0.25); border-radius: 10px; padding: 1px 7px; margin-left: 4px; font-size: 0.75rem; }}
  .seg-btn:not(.active) .count {{ background: #e2e8f0; color: #718096; }}
  .content {{ padding: 16px 32px 40px; }}
  .segment-section {{ margin-bottom: 32px; }}
  .segment-title {{ font-size: 1.1rem; font-weight: 700; color: #1a2332; padding: 12px 0 12px; border-bottom: 2px solid #e2e8f0; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }}
  .segment-title .badge {{ font-size: 0.8rem; font-weight: 600; padding: 3px 10px; border-radius: 12px; background: #ebf4ff; color: #1e6b9e; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }}
  .card {{ background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; transition: all 0.15s; text-decoration: none; color: inherit; display: block; }}
  .card:hover {{ box-shadow: 0 4px 20px rgba(30,107,158,0.15); transform: translateY(-2px); border-color: #90cdf4; }}
  .card.cd-card {{ border-left: 3px solid #10b981; }}
  .card-body {{ padding: 14px; }}
  .card-price {{ font-size: 1.15rem; font-weight: 800; color: #0a3d62; margin-bottom: 4px; }}
  .card-price.por {{ color: #718096; font-size: 0.95rem; font-weight: 600; }}
  .card-title {{ font-size: 0.85rem; color: #2d3748; font-weight: 500; line-height: 1.35; margin-bottom: 8px; }}
  .card-meta {{ display: flex; align-items: center; justify-content: space-between; }}
  .card-broker {{ font-size: 0.75rem; color: #718096; display: flex; align-items: center; gap: 4px; }}
  .broker-dot {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}
  .card-details {{ font-size: 0.72rem; color: #a0aec0; margin-top: 4px; }}
  .source-badge {{ font-size: 0.65rem; padding: 2px 5px; border-radius: 4px; font-weight: 700; background: #d1fae5; color: #065f46; }}
  .no-results {{ grid-column: 1/-1; padding: 40px; text-align: center; color: #718096; font-size: 0.95rem; }}
  .results-count {{ padding: 8px 32px; font-size: 0.85rem; color: #718096; font-weight: 500; }}
  .last-updated {{ text-align: center; padding: 20px; font-size: 0.8rem; color: #a0aec0; }}
  .sold-toggle {{ display: flex; align-items: center; gap: 8px; font-size: 0.85rem; cursor: pointer; }}
  .sold-toggle input {{ cursor: pointer; width: 15px; height: 15px; }}
  .social-panel {{ margin: 16px 32px 0; background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }}
  .social-header {{ padding: 12px 20px; background: #f7fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; cursor: pointer; }}
  .social-header h3 {{ font-size: 0.95rem; font-weight: 700; color: #1a2332; }}
  .social-body {{ padding: 16px 20px; display: none; }}
  .social-body.open {{ display: block; }}
  .social-section-title {{ font-size: 0.75rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; margin-top: 16px; }}
  .social-section-title:first-child {{ margin-top: 0; }}
  .fb-sources-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 8px; }}
  .fb-source {{ display: flex; flex-direction: column; gap: 2px; padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.15s; background: #fafbfc; }}
  .fb-source:hover {{ border-color: #1877f2; background: #f0f6ff; }}
  .fb-icon {{ font-size: 1rem; }}
  .fb-name {{ font-size: 0.85rem; font-weight: 600; color: #1a2332; }}
  .fb-meta {{ font-size: 0.75rem; color: #718096; }}
  .fb-searches {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .fb-search-btn {{ padding: 6px 14px; border: 1.5px solid #1877f2; border-radius: 20px; background: #f0f6ff; color: #1877f2; font-size: 0.8rem; font-weight: 600; text-decoration: none; transition: all 0.15s; white-space: nowrap; }}
  .fb-search-btn:hover {{ background: #1877f2; color: white; }}
  .other-sources-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px; }}
  .other-source {{ display: flex; flex-direction: column; gap: 2px; padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.15s; background: #fafbfc; }}
  .other-source:hover {{ border-color: #38a169; background: #f0fff4; }}
  .other-name {{ font-size: 0.85rem; font-weight: 600; color: #1a2332; }}
  .other-desc {{ font-size: 0.75rem; color: #718096; }}
  @media (max-width: 600px) {{
    .header {{ padding: 16px; }} .controls {{ padding: 12px 16px; gap: 10px; }}
    .segments {{ padding: 12px 16px 0; }} .content {{ padding: 12px 16px 32px; }}
    .grid {{ grid-template-columns: 1fr 1fr; gap: 10px; }}
    .card-body {{ padding: 10px; }} .social-panel {{ margin: 12px 16px 0; }}
  }}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>🌴 Bonaire Vastgoed Scanner</h1>
    <p>2 aggregators · {brokers_count} makelaars · Dagelijks bijgewerkt</p>
  </div>
  <div class="header-stats">
    <div class="stat"><div class="num" id="stat-total">{len(active)}</div><div class="lbl">Listings</div></div>
    <div class="stat"><div class="num">{with_price}</div><div class="lbl">Met prijs</div></div>
    <div class="stat"><div class="num">{brokers_count}</div><div class="lbl">Makelaars</div></div>
    <div class="stat"><div class="num">{sold_count}</div><div class="lbl">Verkocht</div></div>
  </div>
</div>
<div class="controls">
  <input class="search-box" type="text" id="search" placeholder="Zoeken op naam, makelaar..." oninput="render()">
  <select id="broker-filter" onchange="render()"><option value="">Alle makelaars</option></select>
  <select id="source-filter" onchange="render()">
    <option value="">Alle bronnen ({len(active)})</option>
    <option value="bonaire-brokers.com">bonaire-brokers.com ({sources_bb})</option>
    <option value="casadushi">Casa Dushi — uniek ({sources_cd})</option>
  </select>
  <select id="sort" onchange="render()">
    <option value="price-asc">Prijs: laag → hoog</option>
    <option value="price-desc">Prijs: hoog → laag</option>
    <option value="name">Naam A-Z</option>
  </select>
  <label class="sold-toggle">
    <input type="checkbox" id="hide-sold" checked onchange="render()">
    Verberg verkochte woningen
  </label>
</div>
<div class="social-panel">
  <div class="social-header" onclick="toggleSocial()">
    <h3>📋 Privéaanbod &amp; extra bronnen — handmatig controleren</h3>
    <span id="social-toggle-icon">▼ uitklappen</span>
  </div>
  <div class="social-body" id="social-body">
    <div style="background:#fffbeb;border:1.5px solid #f6c05c;border-radius:8px;padding:12px 16px;margin-bottom:14px;font-size:0.85rem;line-height:1.5;color:#744210;">
      <strong>ℹ️ Twee aggregators gecombineerd:</strong> {sources_bb} listings van <strong>bonaire-brokers.com</strong> + {sources_cd} extra unieke listings van <strong>Casa Dushi</strong>. Privéverkopen staan op Facebook-groepen hieronder.
    </div>
    <div class="social-section-title">Facebook Groepen — privéaanbod &amp; makelaars</div>
    <div class="fb-sources-grid">{fb_groups_html}</div>
    <div class="social-section-title">Facebook Zoekopdrachten</div>
    <div class="fb-searches">{fb_searches_html}</div>
    <div class="social-section-title">Overige platforms &amp; bronnen</div>
    <div class="other-sources-grid">{other_sources_html}</div>
  </div>
</div>
<div class="segments" id="segments"></div>
<div class="results-count" id="results-count"></div>
<div class="content" id="content"></div>
<div class="last-updated">Laatst bijgewerkt: {last_updated} · <span style="color:#10b981">■</span> = uniek via Casa Dushi</div>
<script>
const LISTINGS={listings_js};
const COLORS={json.dumps(BROKER_COLORS)};
const SEGMENTS=[
  {{id:'all',label:'Alles',min:0,max:Infinity}},
  {{id:'por',label:'Prijs op aanvraag',min:null,max:null}},
  {{id:'u200',label:'< $200k',min:0,max:200000}},
  {{id:'r200',label:'$200k–$300k',min:200000,max:300000}},
  {{id:'r300',label:'$300k–$400k',min:300000,max:400000}},
  {{id:'r400',label:'$400k–$500k',min:400000,max:500000}},
  {{id:'r500',label:'$500k–$750k',min:500000,max:750000}},
  {{id:'r750',label:'$750k–$1M',min:750000,max:1000000}},
  {{id:'r1m',label:'$1M–$2M',min:1000000,max:2000000}},
  {{id:'r2m',label:'$2M+',min:2000000,max:Infinity}},
];
let seg='all';

function fl(){{
  const q=document.getElementById('search').value.toLowerCase();
  const b=document.getElementById('broker-filter').value;
  const src=document.getElementById('source-filter').value;
  const hs=document.getElementById('hide-sold').checked;
  return LISTINGS.filter(l=>(!hs||!l.sold)&&(!b||l.broker===b)&&(!src||l.source===src)&&
    (!q||l.title.toLowerCase().includes(q)||(l.broker||'').toLowerCase().includes(q)));
}}

function sf(lst,s){{
  if(s.id==='all')return lst;
  if(s.id==='por')return lst.filter(l=>!l.price);
  return lst.filter(l=>l.price&&l.price>=s.min&&l.price<s.max);
}}

function sl(lst){{
  const s=document.getElementById('sort').value;
  return[...lst].sort((a,b)=>{{
    if(s==='price-asc'){{if(!a.price)return 1;if(!b.price)return -1;return a.price-b.price;}}
    if(s==='price-desc'){{if(!a.price)return 1;if(!b.price)return -1;return b.price-a.price;}}
    return(a.title||'').localeCompare(b.title||'');
  }});
}}

function fp(l){{
  if(!l.price)return'Prijs op aanvraag';
  return(l.price_display&&l.price_display.startsWith('€')?'€':'$')+l.price.toLocaleString('nl-NL');
}}

function card(l){{
  const por=!l.price,c=COLORS[l.broker]||'#718096';
  const isCd=l.source==='casadushi';
  const det=[];
  if(l.beds)det.push(l.beds+'🛏');if(l.baths)det.push(l.baths+'🚿');
  if(l.type&&l.type!=='Unknown'&&l.type!=='House')det.push(l.type);
  return`<a class="card${{isCd?' cd-card':''}}" href="${{l.url}}" target="_blank" rel="noopener">
    <div class="card-body">
      <div class="card-price${{por?' por':''}}">${{fp(l)}}</div>
      <div class="card-title">${{l.title}}</div>
      <div class="card-meta">
        <div class="card-broker"><div class="broker-dot" style="background:${{c}}"></div>${{l.broker}}</div>
        ${{isCd?'<span class="source-badge">Casa Dushi</span>':''}}
      </div>
      ${{det.length?`<div class="card-details">${{det.join(' · ')}}</div>`:''}}
    </div></a>`;
}}

function render(){{
  const f=fl(),s=sl(f);
  const actF=f.filter(l=>!l.sold);
  document.getElementById('stat-total').textContent=actF.length;
  const curSeg=SEGMENTS.find(x=>x.id===seg);
  document.getElementById('segments').innerHTML=SEGMENTS.map(x=>{{
    const cnt=sf(actF,x).length,isA=x.id===seg;
    return`<button class="seg-btn${{isA?' active':''}}" onclick="setSeg('${{x.id}}')">${{x.label}}<span class="count">${{cnt}}</span></button>`;
  }}).join('');
  const vis=sf(s,curSeg);
  document.getElementById('results-count').textContent=`${{vis.length}} van ${{f.length}} listings`;
  if(seg==='all'){{
    const secs=SEGMENTS.filter(x=>x.id!=='all'&&x.id!=='por').map(x=>{{
      const items=sf(s,x).filter(l=>l.price&&!l.sold);
      return items.length?`<div class="segment-section"><div class="segment-title">${{x.label}}<span class="badge">${{items.length}} listings</span></div><div class="grid">${{items.map(card).join('')}}</div></div>`:'';
    }});
    const por=sf(s,{{id:'por'}}).filter(l=>!l.sold);
    const porS=por.length?`<div class="segment-section"><div class="segment-title">Prijs op aanvraag<span class="badge">${{por.length}} listings</span></div><div class="grid">${{por.map(card).join('')}}</div></div>`:'';
    document.getElementById('content').innerHTML=secs.join('')+porS||'<div class="no-results">Geen resultaten.</div>';
  }}else{{
    document.getElementById('content').innerHTML=vis.length?`<div class="grid">${{vis.map(card).join('')}}</div>`:'<div class="no-results">Geen listings.</div>';
  }}
}}

function setSeg(id){{seg=id;render();window.scrollTo({{top:200,behavior:'smooth'}});}}
function toggleSocial(){{
  const b=document.getElementById('social-body'),open=b.classList.toggle('open');
  document.getElementById('social-toggle-icon').textContent=open?'▲ inklappen':'▼ uitklappen';
}}
function init(){{
  const brokers=[...new Set(LISTINGS.map(l=>l.broker))].sort();
  const bsel=document.getElementById('broker-filter');
  brokers.forEach(b=>{{const o=document.createElement('option');o.value=b;o.textContent=b;bsel.appendChild(o);}});
  render();
}}
init();
</script>
</body>
</html>"""

OUT_FILE.write_text(html, encoding='utf-8')
size = OUT_FILE.stat().st_size
print(f"✓ index.html gebouwd ({size // 1024} KB)")
print(f"  Actief: {len(active)} | Verkocht: {sold_count} | Makelaars: {brokers_count}")
