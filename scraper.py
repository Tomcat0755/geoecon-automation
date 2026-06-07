import os
import requests
import feedparser
from datetime import datetime

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def get_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:3]: # Solo los 3 más recientes
            link = entry.get('link', '')
            title = entry.get('title', 'Sin título')
            summary = entry.get('summary', entry.get('description', ''))
            # Limpiar HTML del resumen
            import re
            summary = re.sub('<[^<]+>', '', summary)[:250]
            
            published = entry.get('published', '')
            try:
                date_obj = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d')

            articles.append({
                'title': title,
                'quote': summary,
                'link': link,
                'date': date_str,
                'source': url.split('/')[2],
                'urgency': 'medium'
            })
        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def save_to_supabase(articles):
    if not articles:
        print("No articles to save.")
        return
    
    url = f"{SUPABASE_URL}/rest/v1/briefings"
    headers = get_headers()
    
    # Mapear campos a los nombres exactos de tu tabla en Supabase
    payload = []
    for art in articles:
        payload.append({
            'author': art['source'],
            'country': 'usa', # Default, el scraper puede mejorarse para detectar país
            'flag': '🇸',
            'avatar': art['source'][:2].upper(),
            'role': 'Think Tank',
            'type': 'thinktank',
            'urgency': art['urgency'],
            'title': art['title'],
            'quote': art['quote'],
            'tags': 'Geopolítica, Análisis',
            'source': art['source'],
            'link': art['link'],
            'date': art['date']
        })

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        print(f"✅ Guardados {len(payload)} artículos correctamente.")
    else:
        print(f"❌ Error al guardar: {response.status_code} - {response.text}")

def main():
    print(" Iniciando raspado de GeoEcon...")
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Faltan credenciales de Supabase.")
        return

    rss_feeds = [
        'https://www.csis.org/rss.xml',
        'https://www.brookings.edu/feed/',
        'https://www.chathamhouse.org/rss.xml'
    ]

    all_articles = []
    for feed_url in rss_feeds:
        print(f"📡 Procesando: {feed_url}")
        articles = fetch_rss(feed_url)
        all_articles.extend(articles)

    print(f"📦 Total de artículos extraídos: {len(all_articles)}")
    save_to_supabase(all_articles)
    print("✅ Completado.")

if __name__ == "__main__":
    main()
