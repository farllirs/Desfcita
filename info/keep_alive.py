from flask import Flask, request, jsonify, redirect, session
from threading import Thread
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())

# Importar páginas y estilos
from info.pages.styles import BASE_STYLES, META_TAGS
from info.pages.terms import TERMS_HTML
from info.pages.privacy import PRIVACY_HTML
from info.pages.verify import VERIFY_HTML
from info.pages.interactions import INTERACTIONS_PAGE_HTML
from info.pages.callback import render_success, render_error

# Importar OAuth2 oficial
from info.discord_oauth import (
    get_oauth_url, exchange_code, get_user_info, 
    get_user_avatar_url, update_role_connection,
    PUBLIC_KEY, verify_discord_signature
)

# ══════════════════════════════════════════════════════════════════════════════
# 🏠 PÁGINA PRINCIPAL - GLASSMORPHISM
# ══════════════════════════════════════════════════════════════════════════════

HOME_HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    {META_TAGS}
    <title>DESFCITA — Discord Bot</title>
    {BASE_STYLES}
    <style>
        .hero {{
            text-align: center;
        }}
        
        .logo-container {{
            position: relative;
            width: 120px;
            height: 120px;
            margin: 0 auto 28px;
        }}
        
        .logo {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 3px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 12px 40px rgba(255, 107, 157, 0.4);
            object-fit: cover;
        }}
        
        .logo-glow {{
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), #8B5CF6);
            opacity: 0.5;
            filter: blur(20px);
            z-index: -1;
            animation: glowPulse 3s ease-in-out infinite;
        }}
        
        @keyframes glowPulse {{
            0%, 100% {{ opacity: 0.4; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.05); }}
        }}
        
        .brand {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #fff 0%, var(--primary-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .tagline {{
            color: var(--text-secondary);
            font-size: 1rem;
            margin-bottom: 32px;
        }}
        
        .nav-links {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 32px;
        }}
        
        .nav-link {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            color: var(--text-primary);
            text-decoration: none;
            transition: all 0.2s ease;
        }}
        
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(4px);
            border-color: var(--primary);
        }}
        
        .nav-link.primary {{
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border: none;
        }}
        
        .nav-link.primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(255, 107, 157, 0.4);
        }}
        
        .nav-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }}
        
        .nav-link.primary .nav-icon {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        .nav-content {{
            flex: 1;
        }}
        
        .nav-title {{
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 2px;
        }}
        
        .nav-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        
        .nav-link.primary .nav-desc {{
            color: rgba(255, 255, 255, 0.8);
        }}
        
        .nav-arrow {{
            color: var(--text-muted);
            font-size: 1.2rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin: 32px 0;
        }}
        
        .stat {{
            text-align: center;
            padding: 16px 8px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-light);
        }}
        
        .stat-label {{
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="hero">
                <div class="logo-container">
                    <div class="logo-glow"></div>
                    <img src="https://cdn.discordapp.com/attachments/1465306003389026314/1467410893846348029/Screenshot_20260112-172303.png" 
                         alt="DESFCITA" 
                         class="logo"
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23FF6B9D%22 width=%22100%22 height=%22100%22 rx=%2250%22/><text x=%2250%22 y=%2265%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2240%22>D</text></svg>'">
                </div>
                
                <div class="brand">DESFCITA</div>
                <div class="tagline">Tu asistente de Discord premium</div>
                
                <div class="status-badge">
                    <div class="status-dot"></div>
                    <span class="status-text">En línea</span>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">24/7</div>
                    <div class="stat-label">Activo</div>
                </div>
                <div class="stat">
                    <div class="stat-value">∞</div>
                    <div class="stat-label">Comandos</div>
                </div>
                <div class="stat">
                    <div class="stat-value">v2.1</div>
                    <div class="stat-label">Versión</div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/verify-user" class="nav-link primary">
                    <span class="nav-icon">🔐</span>
                    <span class="nav-content">
                        <span class="nav-title">Verificar cuenta</span>
                        <span class="nav-desc">Vincula tu cuenta de Discord</span>
                    </span>
                    <span class="nav-arrow">→</span>
                </a>
                
                <a href="/terms-of-service" class="nav-link">
                    <span class="nav-icon">📋</span>
                    <span class="nav-content">
                        <span class="nav-title">Términos de servicio</span>
                        <span class="nav-desc">Reglas y condiciones de uso</span>
                    </span>
                    <span class="nav-arrow">→</span>
                </a>
                
                <a href="/privacy-policy" class="nav-link">
                    <span class="nav-icon">🔒</span>
                    <span class="nav-content">
                        <span class="nav-title">Política de privacidad</span>
                        <span class="nav-desc">Cómo protegemos tus datos</span>
                    </span>
                    <span class="nav-arrow">→</span>
                </a>
                
                <a href="/api/interactions" class="nav-link">
                    <span class="nav-icon">⚡</span>
                    <span class="nav-content">
                        <span class="nav-title">API</span>
                        <span class="nav-desc">Endpoint de interactions</span>
                    </span>
                    <span class="nav-arrow">→</span>
                </a>
            </div>
            
            <div class="footer">
                DESFCITA Bot · Hecho con ♥
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return HOME_HTML

@app.route("/terms")
@app.route("/terms-of-service")
def terms():
    return TERMS_HTML

@app.route("/privacy")
@app.route("/privacy-policy")
def privacy():
    return PRIVACY_HTML

# ══════════════════════════════════════════════════════════════════════════════
# 🔐 OAUTH2 - LINKED ROLES VERIFICATION (OFICIAL)
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/verify")
@app.route("/verify-user")
def verify():
    """Iniciar flujo OAuth2 para verificación de Linked Roles"""
    oauth_url = get_oauth_url()
    return redirect(oauth_url)

@app.route("/callback")
def oauth_callback():
    """Callback de OAuth2 - Procesar autorización"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return render_error(f"Autorización denegada: {error}")
    
    if not code:
        return render_error("No se recibió código de autorización")
    
    tokens = exchange_code(code)
    if not tokens:
        return render_error("Error al obtener tokens de acceso")
    
    access_token = tokens.get('access_token')
    
    user_data = get_user_info(access_token)
    if not user_data:
        return render_error("Error al obtener información del usuario")
    
    from datetime import datetime
    metadata = {
        'verified': True,
        'member_since': datetime.utcnow().isoformat() + 'Z',
        'level': 1
    }
    
    update_role_connection(
        access_token=access_token,
        platform_name='DESFCITA Bot',
        platform_username=user_data.get('username', 'Usuario'),
        metadata=metadata
    )
    
    avatar_url = get_user_avatar_url(user_data)
    return render_success(user_data, avatar_url)

# ══════════════════════════════════════════════════════════════════════════════
# ⚡ INTERACTIONS ENDPOINT (OFICIAL CON VERIFICACIÓN DE FIRMA)
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/interactions", methods=['GET', 'POST'])
def interactions():
    """Endpoint oficial de Interactions de Discord"""
    if request.method == 'GET':
        return INTERACTIONS_PAGE_HTML
    
    if PUBLIC_KEY:
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if signature and timestamp:
            try:
                from nacl.signing import VerifyKey
                verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
                body = request.data.decode('utf-8')
                message = timestamp.encode() + body.encode()
                verify_key.verify(message, bytes.fromhex(signature))
            except Exception:
                return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    if data.get('type') == 1:
        return jsonify({'type': 1})
    
    if data.get('type') == 2:
        command_name = data.get('data', {}).get('name', '')
        return jsonify({
            'type': 4,
            'data': {
                'content': f'Comando `/{command_name}` recibido',
                'flags': 64
            }
        })
    
    if data.get('type') == 3:
        return jsonify({
            'type': 4,
            'data': {'content': 'Interacción procesada', 'flags': 64}
        })
    
    if data.get('type') == 5:
        return jsonify({
            'type': 4,
            'data': {'content': 'Formulario recibido', 'flags': 64}
        })
    
    return jsonify({'type': 1})

# ══════════════════════════════════════════════════════════════════════════════
# 🔧 ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/register-metadata", methods=['POST'])
def register_metadata_route():
    """Registrar metadata de Linked Roles"""
    from info.discord_oauth import register_metadata
    success, message = register_metadata()
    return jsonify({'success': success, 'message': message})

@app.route("/health")
def health():
    """Health check para Render"""
    return jsonify({'status': 'ok', 'bot': 'DESFCITA'})

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
