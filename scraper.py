import os
import feedparser
import requests
from datetime import datetime

print("INICIANDO RASPADOR")

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Faltan variables")
    exit(1)

print("Variables Vale")

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
    'autor': source_name,
    'pais': 'usa',
    'flag': 'U',  # Cambiado de 'bandera' a 'flag'
    'avatar': source_name[:2].upper(),
    'rol': 'Think Tank',
    'escribe': 'academic',  # Cambiado de 'tipo' a 'escribe'
    'urgencia': 'medium',
    'titulo': entry.get('title', 'Sin titulo')[:200],
    'cita': entry.get('summary', '')[:300],
    'etiquetas': 'Geopolitica',
    'fuente': source_name,
    'enlace': entry.get('link', ''),
    'fecha': datetime.now().strftime('%Y-%m-%d')
}
            briefings.append(briefing)
            print("  OK: " + briefing['titulo'][:50])
    return briefings

def save_to_supabase(briefings):
    print("Guardando " + str(len(briefings)) + " informes...")
    count = 0
    for briefing in briefings:
        try:
            url = SUPABASE_URL + '/rest/v1/briefings'
            response = requests.post(url, json=briefing, headers=headers)
            print("  Status: " + str(response.status_code))
            if response.status_code in [201, 204]:
                count += 1
                print("  OK guardado")
            else:
                print("  ERROR response: " + response.text[:100])
        except Exception as e:
            print("  ERROR: " + str(e))
    print("Total guardados: " + str(count))

def main():
    print("Robot de Automatizacion GeoEcon")
    briefings = parse_rss_feeds()
    if briefings:
        save_to_supabase(briefings)
    print("COMPLETADO")

if __name__ == "__main__":
    main()
