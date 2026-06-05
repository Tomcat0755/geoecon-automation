import os
import feedparser
import requests
from datetime import datetime
from supabase import create_client, Client

print("=" * 50)
print("INICIANDO SCRAPER")
print("=" * 50)

# ===== CONFIGURACIÓN =====
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Debug: Verificar variables
print(f"\n🔍 Verificando variables de entorno:")
print(f"  SUPABASE_URL existe: {'SÍ' if SUPABASE_URL else 'NO'}")
print(f"  SUPABASE_KEY existe: {'SÍ' if SUPABASE_KEY else 'NO'}")

if SUPABASE_URL:
    print(f"  SUPABASE_URL (primeros 30 chars): {SUPABASE_URL[:30]}...")
if SUPABASE_KEY:
    print(f"  SUPABASE_KEY (primeros 30 chars): {SUPABASE_KEY[:30]}...")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ ERROR: Las variables de entorno no están configuradas")
    print("  Verifica que los secrets en GitHub estén correctamente nombrados:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_KEY")
    raise Exception("Faltan variables de entorno de Supabase")

print(f"\n✅ Variables verificadas correctamente")

# Inicializar cliente de Supabase
print(f"\n🔌 Conectando a Supabase...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexión exitosa a Supabase")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    raise

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
    """Extrae artículos de los RSS de think tanks"""
    briefings = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"\n📰 Procesando {source_name}...")
        try:
            feed = feedparser.parse(feed_url)
            print(f"  ✓ Encontrados {len(feed.entries)} artículos")
            
            for entry in feed.entries[:5]:  # Solo los 5 más recientes
                country = 'usa' if 'CSIS' in source_name or 'Brookings' in source_name or 'CFR' in source_name else 'eu'
                flag = '🇺🇸' if country == 'usa' else '🇪🇺'
                
                summary = entry.get('summary', entry.get('description', ''))
                tags = ['Geopolítica', 'Economía']
                
                briefing = {
                    'author': source_name,
                    'country': country,
                    'flag': flag,
                    'avatar': source_name[:2].upper(),
                    'role': f'Think Tank - {source_name}',
                    'type': 'academic',
                    'urgency': 'medium',
                    'title': entry.get('title', 'Sin título')[:200],
                    'quote': summary[:300] + '...' if len(summary) > 300 else summary,
                    'tags': ','.join(tags),
                    'source': source_name,
                    'link': entry.get('link', ''),
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                briefings.append(briefing)
                print(f"    • {briefing['title'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error procesando {source_name}: {e}")
    
    return briefings

def save_to_supabase(briefings):
    """Guarda los briefings en Supabase"""
    print(f"\n💾 Guardando {len(briefings)} briefings en Supabase...")
    
    count = 0
    for briefing in briefings:
        try:
            existing = supabase.table('briefings').select('id').eq('title', briefing['title']).eq('date', briefing['date']).execute()
                        if not existing.data:
                result = supabase.table('briefings').insert(briefing).execute()
                count += 1
                print(f"  ✓ Insertado: {briefing['title'][:50]}...")
            else:
                print(f"  ⊘ Ya existe: {briefing['title'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error guardando: {e}")
    
    print(f"\n✅ {count} nuevos briefings guardados")

def main():
    """Función principal"""
    print("\n" + "=" * 50)
    print("🤖 GeoEcon Automation Robot")
    print(f"📅 Ejecutando en: {datetime.now()}")
    print("=" * 50)
    
    # 1. Extraer datos de RSS
    briefings = parse_rss_feeds()
    
    # 2. Guardar en Supabase
    if briefings:
        save_to_supabase(briefings)
    else:
        print("\n⚠️ No se encontraron briefings para guardar")
    
    print("\n" + "=" * 50)
    print("✅ Ejecución completada")
    print("=" * 50)

if __name__ == "__main__":
    main()
