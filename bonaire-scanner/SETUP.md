# bonaire-scanner.com — Setup Instructies

Volg deze stappen **eenmalig** om de website live te zetten.
Daarna ververst alles automatisch elke nacht.

---

## Stap 1 — GitHub account & repository aanmaken

1. Ga naar **github.com** en maak een gratis account aan (als je er nog geen hebt)
2. Klik rechtsboven op **+** → **New repository**
3. Naam: `bonaire-scanner`
4. Zet op **Public** (vereist voor gratis GitHub Pages)
5. Klik **Create repository**

---

## Stap 2 — Bestanden uploaden

**Optie A — via GitHub website (makkelijkst):**

1. Open je nieuwe repository op GitHub
2. Klik **uploading an existing file**
3. Sleep alle bestanden en mappen uit de `bonaire-scanner/` map naar het uploadvenster:
   - `scraper.py`
   - `build_dashboard.py`
   - `requirements.txt`
   - `index.html`
   - `data/listings.json`
   - `data/last_updated.txt`
   - `.github/workflows/daily_scrape.yml`
4. Klik **Commit changes**

**Optie B — via Terminal (als je Git geïnstalleerd hebt):**

```bash
cd pad/naar/bonaire-scanner/
git init
git add .
git commit -m "Eerste versie"
git remote add origin https://github.com/JOUW-NAAM/bonaire-scanner.git
git push -u origin main
```

---

## Stap 3 — GitHub Pages inschakelen

1. Ga naar je repository → **Settings** → **Pages** (in de linkerzijbalk)
2. Under **Source**: selecteer **Deploy from a branch**
3. Branch: **main** / folder: **/ (root)**
4. Klik **Save**

Na ~1 minuut is je site live op:
`https://JOUW-NAAM.github.io/bonaire-scanner`

---

## Stap 4 — Domein registreren (bonaire-scanner.com)

1. Ga naar **cloudflare.com** → maak gratis account aan
2. Klik **Domain Registration** → zoek `bonaire-scanner.com`
3. Registreer (~$10/jaar)

---

## Stap 5 — Domein koppelen aan GitHub Pages

**In Cloudflare (DNS-instellingen van bonaire-scanner.com):**

Voeg deze 4 A-records toe:
| Type | Name | Content |
|------|------|---------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

En één CNAME:
| Type | Name | Content |
|------|------|---------|
| CNAME | www | JOUW-NAAM.github.io |

**In GitHub (Pages-instellingen):**

1. Settings → Pages → **Custom domain**
2. Vul in: `bonaire-scanner.com`
3. Vink **Enforce HTTPS** aan

Na 10–30 minuten (DNS-propagatie) is de site live op **bonaire-scanner.com** 🎉

---

## Stap 6 — Automatische updates verifiëren

De scraper draait elke nacht automatisch via GitHub Actions.

Controleren:
- Ga naar je repository → tabblad **Actions**
- Je ziet "Dagelijkse scrape & deploy" in de lijst
- Klik op **Run workflow** om hem nu handmatig te starten (eerste test)

Als alles groen is, ververst de site elke nacht om 05:00 Bonaire-tijd.

---

## Samenvatting kosten

| Item | Kosten |
|------|--------|
| GitHub repo + Pages + Actions | **Gratis** |
| Domeinnaam bonaire-scanner.com | ~**$10/jaar** |
| Hosting, SSL, CDN | **Gratis** (via Cloudflare + GitHub) |
| **Totaal** | **~$10/jaar** |
