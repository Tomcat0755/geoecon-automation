import os
import feedparser
import requests
from datetime import datetime
from supabase import create_client, Client

# ===== CONFIGURACIÓN =====
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Debug: Imprimir si las variables existen
print(f"SUPABASE_URL configurada: {'SÍ' if SUPABASE_URL else 'NO'}")
print(f"SUPABASE_KEY configurada: {'SÍ' if SUPABASE_KEY else 'NO'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Las variables de entorno SUPABASE_URL o SUPABASE_KEY no están configuradas")

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
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
        print(f"Procesando {source_name}...")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:5]:  # Solo los 5 más recientes de cada fuente
            # Determinar país/región basado en la fuente
            country = 'usa' if 'CSIS' in source_name or 'Brookings' in source_name or 'CFR' in source_name else 'eu'
            flag = '🇺' if country == 'usa' else '🇪🇺'
            
            # Extraer tags del resumen (simplificado)
            summary = entry.get('summary', '')
            tags = ['Geopolítica', 'Economía']
            
            briefing = {
                'author': source_name,
                'country': country,
                'flag': flag,
                'avatar': source_name[:2].upper(),
                'role': f'Think Tank - {source_name}',
                'type': 'academic',
                'urgency': 'medium',
                'title': entry.get('title', 'Sin título'),
                'quote': summary[:300] + '...' if len(summary) > 300 else summary,                'tags': ','.join(tags),
                'source': source_name,
                'link': entry.get('link', ''),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            briefings.append(briefing)
    
    return briefings

def save_to_supabase(briefings):
    """Guarda los briefings en Supabase"""
    print(f"Guardando {len(briefings)} briefings en Supabase...")
    
    for briefing in briefings:
        # Verificar si ya existe (por título y fecha)
        existing = supabase.table('briefings').select('id').eq('title', briefing['title']).eq('date', briefing['date']).execute()
        
        if not existing.data:
            # Insertar nuevo briefing
            result = supabase.table('briefings').insert(briefing).execute()
            print(f"✓ Insertado: {briefing['title'][:50]}...")
        else:
            print(f"⊘ Ya existe: {briefing['title'][:50]}...")

def update_keywords():
    """Genera keywords basadas en los briefings recientes"""
    print("Actualizando keywords...")
    
    # Obtener briefings de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    recent = supabase.table('briefings').select('title,tags').eq('date', today).execute()
    
    # Contar frecuencia de palabras (simplificado)
    word_count = {}
    for item in recent.data:
        words = item['title'].split() + item['tags'].split(',')
        for word in words:
            word = word.strip().lower()
            if len(word) > 4:  # Solo palabras con más de 4 letras
                word_count[word] = word_count.get(word, 0) + 1
    
    # Guardar top 10 keywords
    top_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for word, count in top_keywords:
        supabase.table('keywords').insert({
            'text': word.capitalize(),
            'category': 'trending' if count > 3 else '',
            'count': count,
            'date': today        }).execute()
    
    print(f"✓ {len(top_keywords)} keywords actualizadas")

def main():
    """Función principal"""
    print("=" * 50)
    print("GeoEcon Automation Robot")
    print(f"Ejecutando en: {datetime.now()}")
    print("=" * 50)
    
    # 1. Extraer datos de RSS
    briefings = parse_rss_feeds()
    
    # 2. Guardar en Supabase
    save_to_supabase(briefings)
    
    # 3. Actualizar keywords
    update_keywords()
    
    print("=" * 50)
    print("✓ Ejecución completada")
    print("=" * 50)

if __name__ == "__main__":
    main()
