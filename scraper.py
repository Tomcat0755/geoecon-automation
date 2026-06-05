import os
import feedparser
import requests
import json
from datetime import datetime

print("=" * 50)
print("INICIANDO SCRAPER - GeoEcon Automation")
print("=" * 50)

# ===== CONFIGURACIÓN =====
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

print(f"\n🔍 Verificando variables:")
print(f"  SUPABASE_URL: {'✓ Configurada' if SUPABASE_URL else '✗ NO configurada'}")
print(f"  SUPABASE_KEY: {'✓ Configurada' if SUPABASE_KEY else '✗ NO configurada'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ ERROR: Faltan variables de entorno")
    exit(1)

# Headers para la API de Supabase
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

print(f"\n✅ Variables verificadas correctamente")
print(f"🔌 Conectando a: {SUPABASE_URL[:40]}...")

# ===== FUENTES DE DATOS =====
RSS_FEEDS = {
    'CSIS': 'https://www.csis.org/rss.xml',
    'Brookings': 'https://www.brookings.edu/feed/',
    'Chatham House': 'https://www.chathamhouse.org/rss.xml',
    'CFR': 'https://www.cfr.org/rss.xml',
    'Carnegie': 'https://carnegieendowment.org/rss?lang=en',
}

# ===== FUNCIONES =====
def parse_rss_feeds():
    """Extrae artículos de los RSS"""
    briefings = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"\n📰 Procesando {source_name}...")
        try:            feed = feedparser.parse(feed_url)
            print(f"  ✓ {len(feed.entries)} artículos encontrados")
            
            for entry in feed.entries[:5]:
                country = 'usa' if any(x in source_name for x in ['CSIS', 'Brookings', 'CFR']) else 'eu'
                flag = '🇺' if country == 'usa' else '🇪🇺'
                
                summary = entry.get('summary', entry.get('description', ''))
                
                briefing = {
                    'author': source_name,
                    'country': country,
                    'flag': flag,
                    'avatar': source_name[:2].upper(),
                    'role': f'Think Tank - {source_name}',
                    'type': 'academic',
                    'urgency': 'medium',
                    'title': entry.get('title', 'Sin título')[:200],
                    'quote': (summary[:300] + '...') if len(summary) > 300 else summary,
                    'tags': 'Geopolítica,Economía',
                    'source': source_name,
                    'link': entry.get('link', ''),
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                briefings.append(briefing)
                print(f"    • {briefing['title'][:60]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return briefings

def save_to_supabase(briefings):
    """Guarda usando API REST"""
    print(f"\n💾 Guardando {len(briefings)} briefings...")
    
    count = 0
    for briefing in briefings:
        try:
            # Verificar si existe
            check_url = f"{SUPABASE_URL}/rest/v1/briefings"
            check_params = f"select=id&title=eq.{briefing['title']}&date=eq.{briefing['date']}"
            check_response = requests.get(f"{check_url}?{check_params}", headers=headers)
            
            if check_response.status_code == 200 and len(check_response.json()) == 0:
                # Insertar nuevo
                insert_url = f"{SUPABASE_URL}/rest/v1/briefings"
                insert_response = requests.post(insert_url, json=briefing, headers=headers)
                
                if insert_response.status_code in [201, 204]:
                    count += 1                    print(f"  ✓ Guardado: {briefing['title'][:50]}...")
                else:
                    print(f"  ⚠ Error {insert_response.status_code}: {briefing['title'][:50]}")
            else:
                print(f"  ⊘ Ya existe: {briefing['title'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n✅ {count} nuevos briefings guardados")

def main():
    print("\n" + "=" * 50)
    print("🤖 GeoEcon Automation Robot")
    print(f"📅 {datetime.now()}")
    print("=" * 50)
    
    briefings = parse_rss_feeds()
    
    if briefings:
        save_to_supabase(briefings)
    else:
        print("\n⚠️ No se encontraron briefings")
    
    print("\n" + "=" * 50)
    print("✅ EJECUCIÓN COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    main()
