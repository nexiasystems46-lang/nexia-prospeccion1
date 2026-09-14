import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_email(company_name, website, context, active_resource):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing.")

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    resource_text = ""
    if active_resource:
        resource_text = f"""
        Actualmente en nuestra agencia tenemos este recurso/novedad que debes mencionar sutilmente y ofrecer:
        Nombre del recurso: {active_resource['name']}
        Descripción: {active_resource['description']}
        URL del recurso: {active_resource['url']}
        """

    prompt = f"""
    Eres un experto en ventas B2B y prospección para una Agencia de Inteligencia Artificial.
    Tu objetivo es redactar un "Cold Email" (correo en frío) altamente personalizado para ofrecer nuestros servicios.
    
    Datos del prospecto:
    - Nombre de la empresa: {company_name}
    - Sitio web: {website}
    - Contexto extraído de su web (resumen):
    {context[:1500]}
    
    {resource_text}
    
    Instrucciones:
    1. Redacta el correo en español, con un tono profesional pero cercano, no excesivamente formal (evita "Estimados señores").
    2. Encuentra un ángulo entre los servicios de la empresa (basado en el contexto) y cómo la Inteligencia Artificial (automatización, agentes, etc.) podría ayudarles.
    3. Si hay un "recurso/novedad" activo (mencionado arriba), intégralo de manera natural como un regalo o demostración de lo que hacemos.
    4. Termina con un Call to Action (CTA) sencillo, invitando a una llamada rápida de 10 minutos.
    5. Devuelve la respuesta en formato JSON estricto con dos claves: "subject" (el asunto del correo) y "body" (el cuerpo del correo, puedes usar saltos de línea \\n).
    
    Responde ÚNICAMENTE con el JSON, sin formato markdown extra, solo el objeto JSON válido.
    """
    
    response = model.generate_content(prompt)
    
    import json
    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error parseando JSON de Gemini: {e}")
        return {
            "subject": f"Propuesta de Inteligencia Artificial para {company_name}",
            "body": response.text
        }
