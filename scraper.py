import os
import feedparser
import requests
from datetime import datetime

print("INICIANDO SCRAPER")

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Faltan variables")
    exit(1)

print("Variables OK")

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json'
}

RSS_FEEDS = {
    'CSIS': 'https://www.csis.org/rss.xml',
    'Brookings': 'https://www.brookings.edu/feed/',
    'Chatham House': 'https://www.chathamhouse.org/rss.xml',
}

def parse_rss_feeds():
    briefings = []
    for source_name, feed_url in RSS_FEEDS.items():
        print("Procesando: " + source_name)
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:
            briefing = {
                'author': source_name,
                'country': 'usa',
                'flag': 'U',
                'avatar': source_name[:2].upper(),
                'role': 'Think Tank',
                'type': 'academic',
                'urgency': 'medium',
                'title': entry.get('title', 'Sin titulo')[:200],
                'quote': entry.get('summary', '')[:300],
                'tags': 'Geopolitica',
                'source': source_name,
                'link': entry.get('link', ''),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            briefings.append(briefing)
            print("  OK: " + briefing['title'][:50])
    return briefings

def save_to_supabase(briefings):
    print("Guardando " + str(len(briefings)) + " briefings...")
    count = 0
    for briefing in briefings:
        try:
            url = SUPABASE_URL + '/rest/v1/briefings'
            response = requests.post(url, json=briefing, headers=headers)
            if response.status_code in [201, 204]:
                count += 1
                print("  OK guardado")
        except Exception as e:
            print("  ERROR: " + str(e))
    print("Total guardados: " + str(count))

def main():
    print("GeoEcon Automation Robot")
    briefings = parse_rss_feeds()
    if briefings:
        save_to_supabase(briefings)
    print("COMPLETADO")

if __name__ == "__main__":
    main()
