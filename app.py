import streamlit as st
import os
import threading
from dotenv import load_dotenv

from core.database import init_db, add_resource, get_all_resources, toggle_resource, delete_resource, get_active_resources, get_queue_stats, add_to_queue
from core.scheduler import start_scheduler
from core.apify_client import search_businesses
from core.scraper import scrape_website
from core.ai_writer import generate_email

load_dotenv()

# Initialize DB on startup
init_db()

# Start scheduler once (Streamlit runs the script multiple times)
if 'scheduler_started' not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# --- App UI ---

st.set_page_config(page_title="Prospección IA", page_icon="🤖", layout="wide")
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["Lanzar Campaña", "Mis Recursos", "Estado y Cola"])

if menu == "Lanzar Campaña":
    st.title("🚀 Lanzar Campaña de Prospección")
    
    query = st.text_input("Término de búsqueda (ej. 'clínicas dentales en Madrid')")
    limit = st.number_input("Cantidad de clientes a buscar", min_value=1, max_value=50, value=5)
    
    if st.button("Iniciar Búsqueda y Generación"):
        if not query:
            st.error("Por favor ingresa un término de búsqueda.")
        else:
            with st.spinner("Buscando negocios en Google Maps (Apify)..."):
                try:
                    businesses = search_businesses(query, limit)
                except Exception as e:
                    st.error(f"Error en Apify: {e}")
                    businesses = []
                
            if not businesses:
                st.warning("No se encontraron negocios con sitio web o hubo un error.")
            else:
                st.success(f"Se encontraron {len(businesses)} negocios. Iniciando scraping y redacción...")
                
                active_resources = get_active_resources()
                active_resource = active_resources[0] if active_resources else None
                
                for b in businesses:
                    company = b['title']
                    website = b['website']
                    phone = b.get('phone', '')
                    
                    st.write(f"Procesando: **{company}** ({website})")
                    
                    # 1. Scrape
                    context = scrape_website(website)
                    
                    if not context:
                        st.write("  - ⚠️ No se pudo extraer contenido web. Se usará información básica.")
                        context = f"Empresa: {company}. Web: {website}. Teléfono: {phone}."
                        
                    # 2. IA Redacción
                    email_data = generate_email(company, website, context, active_resource)
                    
                    # Email extraction logic might be needed if Apify doesn't return it
                    # For this prototype, we'll assume the email is captured or added manually later if missing
                    extracted_email = b.get('email', '') 
                    
                    # 3. Add to queue
                    add_to_queue(
                        search_query=query,
                        company_name=company,
                        website=website,
                        email=extracted_email,
                        context=context,
                        email_subject=email_data.get('subject', f'Oportunidad para {company}'),
                        email_body=email_data.get('body', '')
                    )
                    st.write("  ✅ Correo redactado y añadido a la cola de envío.")

elif menu == "Mis Recursos":
    st.title("🗂️ Mis Recursos (Lead Magnets / Novedades)")
    
    with st.form("add_resource_form"):
        st.subheader("Añadir nuevo recurso")
        name = st.text_input("Nombre del recurso")
        url = st.text_input("URL / Link")
        desc = st.text_area("Descripción estratégica (para que la IA sepa cómo venderlo)")
        
        if st.form_submit_button("Guardar Recurso"):
            if name and desc:
                add_resource(name, url, desc)
                st.success("Recurso añadido correctamente.")
            else:
                st.error("Nombre y Descripción son obligatorios.")
                
    st.divider()
    st.subheader("Recursos Actuales")
    resources = get_all_resources()
    
    if not resources:
        st.info("No tienes recursos guardados.")
        
    for r in resources:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{r['name']}** - {r['url']}")
            st.caption(r['description'])
        with col2:
            is_active = st.checkbox("Activo", value=r['is_active'], key=f"active_{r['id']}")
            if is_active != r['is_active']:
                toggle_resource(r['id'], is_active)
                st.rerun()
        with col3:
            if st.button("Eliminar", key=f"del_{r['id']}"):
                delete_resource(r['id'])
                st.rerun()
        st.write("---")

elif menu == "Estado y Cola":
    st.title("📊 Estado y Cola de Envíos")
    
    stats = get_queue_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Pendientes", stats.get("pending", 0))
    col2.metric("Enviados", stats.get("sent", 0))
    col3.metric("Fallidos", stats.get("failed", 0))
    
    st.info("⏳ Los correos pendientes se envían automáticamente 1 cada 5 minutos en segundo plano para evitar ser marcados como Spam.")
    
    # Podríamos añadir una tabla para ver los últimos correos generados
