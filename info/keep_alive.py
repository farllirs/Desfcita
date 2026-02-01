from flask import Flask, request, jsonify, redirect, session
from threading import Thread
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())

# Importar páginas
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

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ DESFCITA Bot - Discord 💖</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8dc7 25%, #ffc1e3 50%, #ff8dc7 75%, #ff6b9d 100%);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            font-family: 'Quicksand', sans-serif;
            overflow-x: hidden;
            position: relative;
        }
        
        /* Estrellas y símbolos rosas */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        
        .star {
            position: absolute;
            color: #fff;
            font-size: 20px;
            animation: twinkle 3s infinite;
        }
        
        .star:nth-child(1) { top: 10%; left: 15%; animation-delay: 0s; }
        .star:nth-child(2) { top: 20%; left: 80%; animation-delay: 0.5s; }
        .star:nth-child(3) { top: 40%; left: 25%; animation-delay: 1s; }
        .star:nth-child(4) { top: 60%; left: 70%; animation-delay: 1.5s; }
        .star:nth-child(5) { top: 80%; left: 40%; animation-delay: 2s; }
        .star:nth-child(6) { top: 15%; left: 50%; animation-delay: 2.5s; }
        .star:nth-child(7) { top: 70%; left: 90%; animation-delay: 0.8s; }
        .star:nth-child(8) { top: 30%; left: 60%; animation-delay: 1.8s; }
        .star:nth-child(9) { top: 50%; left: 10%; animation-delay: 1.2s; }
        .star:nth-child(10) { top: 90%; left: 75%; animation-delay: 2.2s; }
        
        /* Corazones y símbolos rosas flotantes */
        .hearts {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
        }
        
        .heart {
            position: absolute;
            font-size: 25px;
            animation: float-hearts 15s infinite;
            opacity: 0;
        }
        
        .heart:nth-child(1) { left: 10%; animation-delay: 0s; }
        .heart:nth-child(2) { left: 20%; animation-delay: 3s; }
        .heart:nth-child(3) { left: 30%; animation-delay: 6s; }
        .heart:nth-child(4) { left: 45%; animation-delay: 9s; }
        .heart:nth-child(5) { left: 60%; animation-delay: 12s; }
        .heart:nth-child(6) { left: 75%; animation-delay: 2s; }
        .heart:nth-child(7) { left: 85%; animation-delay: 5s; }
        .heart:nth-child(8) { left: 15%; animation-delay: 8s; }
        
        .container {
            text-align: center;
            z-index: 10;
            padding: 20px;
            max-width: 850px;
            width: 100%;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            padding: 50px 40px;
            box-shadow: 0 25px 70px rgba(255, 105, 180, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
            animation: slideIn 1s ease-out;
        }
        
        .bot-avatar-container {
            margin: 0 auto 30px;
            position: relative;
            width: 170px;
            height: 170px;
        }
        
        .bot-avatar {
            width: 170px;
            height: 170px;
            margin: 0 auto;
            border-radius: 50%;
            box-shadow: 0 15px 50px rgba(255, 105, 180, 0.6);
            animation: pulse-avatar 3s ease-in-out infinite;
            border: 6px solid rgba(255, 182, 193, 0.8);
            object-fit: cover;
            transition: transform 0.6s ease;
        }
        
        .avatar-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 105, 180, 0.4) 0%, transparent 70%);
            animation: glow-pulse 3s ease-in-out infinite;
            pointer-events: none;
        }
        
        .decorative-hearts {
            position: absolute;
            top: -10px;
            right: -10px;
            font-size: 30px;
            animation: bounce-heart 2s ease-in-out infinite;
        }
        
        .bot-name {
            font-family: 'Pacifico', cursive;
            font-size: 3.8rem;
            background: linear-gradient(135deg, #ff1493 0%, #ff69b4 50%, #ffb6c1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            text-shadow: 0 5px 20px rgba(255, 105, 180, 0.5);
            animation: glow-text 3s ease-in-out infinite alternate;
            filter: drop-shadow(0 0 20px rgba(255, 105, 180, 0.6));
        }
        
        .bot-tagline {
            color: #fff;
            font-size: 1.4rem;
            margin-bottom: 30px;
            font-weight: 500;
            text-shadow: 0 2px 10px rgba(255, 105, 180, 0.3);
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: linear-gradient(135deg, rgba(255, 105, 180, 0.4) 0%, rgba(255, 182, 193, 0.4) 100%);
            padding: 18px 40px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            margin-bottom: 40px;
            border: 3px solid rgba(255, 182, 193, 0.6);
            box-shadow: 0 8px 25px rgba(255, 105, 180, 0.4);
            animation: bounce-in 1s ease-out 0.5s both;
        }
        
        .status-dot {
            width: 16px;
            height: 16px;
            background: #ff1493;
            border-radius: 50%;
            animation: pulse-dot 2s ease-in-out infinite;
            box-shadow: 0 0 25px #ff69b4;
        }
        
        .status-text {
            color: #ffffff;
            font-size: 1.3rem;
            font-weight: 600;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .feature-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 30px 20px;
            border-radius: 25px;
            border: 3px solid rgba(255, 182, 193, 0.4);
            transition: all 0.3s ease;
            animation: fade-in-up 1s ease-out;
            animation-fill-mode: both;
        }
        
        .feature-item:nth-child(1) { animation-delay: 0.8s; }
        .feature-item:nth-child(2) { animation-delay: 1s; }
        .feature-item:nth-child(3) { animation-delay: 1.2s; }
        .feature-item:nth-child(4) { animation-delay: 1.4s; }
        
        .feature-item:hover {
            transform: translateY(-12px) scale(1.05);
            background: rgba(255, 182, 193, 0.3);
            box-shadow: 0 15px 40px rgba(255, 105, 180, 0.5);
            border-color: rgba(255, 105, 180, 0.6);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 12px;
            display: block;
            animation: bounce-icon 2s ease-in-out infinite;
        }
        
        .feature-title {
            color: #fff;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 8px rgba(255, 105, 180, 0.3);
        }
        
        .feature-desc {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1rem;
            line-height: 1.5;
        }
        
        .footer {
            margin-top: 40px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            font-weight: 500;
            animation: fade-in 2s ease-out;
            text-shadow: 0 2px 10px rgba(255, 105, 180, 0.3);
        }
        
        /* Botones de navegación */
        .nav-buttons {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 40px;
            animation: fade-in-up 1s ease-out 1.6s both;
        }
        
        .nav-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 14px 24px;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 182, 193, 0.5);
            border-radius: 50px;
            color: #fff;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .nav-btn:hover {
            background: rgba(255, 105, 180, 0.4);
            border-color: rgba(255, 105, 180, 0.8);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255, 105, 180, 0.4);
        }
        
        .nav-btn .btn-icon {
            font-size: 1.2rem;
        }
        
        .verify-btn {
            background: linear-gradient(135deg, rgba(255, 20, 147, 0.5), rgba(255, 105, 180, 0.5));
            border-color: rgba(255, 20, 147, 0.7);
            padding: 16px 30px;
            font-size: 1.05rem;
        }
        
        .verify-btn:hover {
            background: linear-gradient(135deg, rgba(255, 20, 147, 0.7), rgba(255, 105, 180, 0.7));
            box-shadow: 0 15px 40px rgba(255, 20, 147, 0.5);
        }
        
        @media (max-width: 768px) {
            .nav-buttons {
                flex-direction: column;
                align-items: center;
            }
            .nav-btn {
                width: 100%;
                max-width: 250px;
                justify-content: center;
            }
        }
        
        .sparkle {
            position: absolute;
            width: 8px;
            height: 8px;
            background: #ff69b4;
            border-radius: 50%;
            pointer-events: none;
            animation: sparkle-effect 1s ease-out forwards;
            box-shadow: 0 0 10px #ff69b4;
        }
        
        /* Animaciones */
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(50px) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        @keyframes pulse-avatar {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 15px 50px rgba(255, 105, 180, 0.6);
            }
            50% {
                transform: scale(1.08);
                box-shadow: 0 20px 60px rgba(255, 105, 180, 0.8);
            }
        }
        
        @keyframes glow-pulse {
            0%, 100% {
                opacity: 0.6;
                transform: translate(-50%, -50%) scale(1);
            }
            50% {
                opacity: 0.9;
                transform: translate(-50%, -50%) scale(1.1);
            }
        }
        
        @keyframes bounce-heart {
            0%, 100% {
                transform: translateY(0) rotate(15deg);
            }
            50% {
                transform: translateY(-10px) rotate(15deg);
            }
        }
        
        @keyframes glow-text {
            from {
                filter: drop-shadow(0 0 15px rgba(255, 105, 180, 0.6));
            }
            to {
                filter: drop-shadow(0 0 30px rgba(255, 105, 180, 0.9));
            }
        }
        
        @keyframes pulse-dot {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.4);
                opacity: 0.6;
            }
        }
        
        @keyframes bounce-in {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                opacity: 1;
                transform: scale(1.15);
            }
            70% {
                transform: scale(0.95);
            }
            100% {
                transform: scale(1);
            }
        }
        
        @keyframes fade-in-up {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes bounce-icon {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-8px);
            }
        }
        
        @keyframes fade-in {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.4; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.3); }
        }
        
        @keyframes float-hearts {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 0.8;
            }
            90% {
                opacity: 0.8;
            }
            100% {
                transform: translateY(-100vh) rotate(360deg);
                opacity: 0;
            }
        }
        
        @keyframes sparkle-effect {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            100% {
                opacity: 0;
                transform: scale(3);
            }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .bot-name {
                font-size: 2.8rem;
            }
            
            .card {
                padding: 40px 25px;
            }
            
            .features {
                grid-template-columns: 1fr;
            }
            
            .bot-avatar-container,
            .bot-avatar {
                width: 140px;
                height: 140px;
            }
            
            .avatar-glow {
                width: 160px;
                height: 160px;
            }
        }
    </style>
</head>
<body>
    <!-- Estrellas y símbolos rosas -->
    <div class="stars">
        <div class="star">✨</div>
        <div class="star">🌸</div>
        <div class="star">💕</div>
        <div class="star">✨</div>
        <div class="star">🌸</div>
        <div class="star">💕</div>
        <div class="star">✨</div>
        <div class="star">🌸</div>
        <div class="star">💕</div>
        <div class="star">✨</div>
    </div>
    
    <!-- Corazones y símbolos flotantes -->
    <div class="hearts">
        <div class="heart">💖</div>
        <div class="heart">💕</div>
        <div class="heart">🌸</div>
        <div class="heart">💝</div>
        <div class="heart">💗</div>
        <div class="heart">🌺</div>
        <div class="heart">💓</div>
        <div class="heart">🌷</div>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="bot-avatar-container">
                <div class="avatar-glow"></div>
                <img src="https://cdn.discordapp.com/attachments/1465306003389026314/1467410893846348029/Screenshot_20260112-172303.png?ex=69804864&is=697ef6e4&hm=657bad049a26d4afe2be931c6fe437bdd91bb6a7a9c9d12fd547f31d64f146f7&" 
                     alt="DESFCITA Bot" 
                     class="bot-avatar"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="decorative-hearts">💖</div>
            </div>
            
            <h1 class="bot-name">DESFCITA 💖</h1>
            <p class="bot-tagline">Tu asistente de Discord más linda ✨🌸</p>
            
            <div class="status-badge">
                <div class="status-dot"></div>
                <span class="status-text">¡Estoy en línea y lista para ayudar! 💕✨</span>
            </div>
            
            <div class="features">
                <div class="feature-item">
                    <span class="feature-icon">👋💖</span>
                    <div class="feature-title">Bienvenidas 🌸</div>
                    <div class="feature-desc">Mensajes personalizados con imágenes hermosas y mucho amor</div>
                </div>
                
                <div class="feature-item">
                    <span class="feature-icon">🎫💕</span>
                    <div class="feature-title">Sistema de Tickets 💝</div>
                    <div class="feature-desc">Gestión eficiente de soporte con mucho cariño</div>
                </div>
                
                <div class="feature-item">
                    <span class="feature-icon">💡✨</span>
                    <div class="feature-title">Sugerencias 🌺</div>
                    <div class="feature-desc">Escucho todas tus ideas con atención y cariño</div>
                </div>
                
                <div class="feature-item">
                    <span class="feature-icon">⚙️💗</span>
                    <div class="feature-title">Configuración 🌷</div>
                    <div class="feature-desc">Personalizable completamente a tu gusto</div>
                </div>
            </div>
            
            <!-- Botones de navegación -->
            <div class="nav-buttons">
                <a href="/verify-user" class="nav-btn verify-btn">
                    <span class="btn-icon">🔐</span>
                    <span class="btn-text">Verificar Cuenta</span>
                </a>
                <a href="/terms-of-service" class="nav-btn">
                    <span class="btn-icon">📜</span>
                    <span class="btn-text">Términos</span>
                </a>
                <a href="/privacy-policy" class="nav-btn">
                    <span class="btn-icon">🔒</span>
                    <span class="btn-text">Privacidad</span>
                </a>
                <a href="/api/interactions" class="nav-btn">
                    <span class="btn-icon">⚡</span>
                    <span class="btn-text">API</span>
                </a>
            </div>
            
            <div class="footer">
                Made with 💖💕✨ by DESFCITA Team 🌸
            </div>
        </div>
    </div>
    
    <script>
        // Efecto de destellos rosas al hacer clic
        document.addEventListener('click', (e) => {
            for(let i = 0; i < 3; i++) {
                setTimeout(() => {
                    const sparkle = document.createElement('div');
                    sparkle.className = 'sparkle';
                    sparkle.style.left = (e.clientX + (Math.random() - 0.5) * 30) + 'px';
                    sparkle.style.top = (e.clientY + (Math.random() - 0.5) * 30) + 'px';
                    document.body.appendChild(sparkle);
                    
                    setTimeout(() => {
                        sparkle.remove();
                    }, 1000);
                }, i * 100);
            }
        });
        
        // Animación del avatar al pasar el mouse
        const avatar = document.querySelector('.bot-avatar');
        if(avatar) {
            avatar.addEventListener('mouseenter', () => {
                avatar.style.transform = 'rotate(360deg) scale(1.1)';
            });
            
            avatar.addEventListener('mouseleave', () => {
                avatar.style.transform = 'rotate(0deg) scale(1)';
            });
        }
        
        // Crear más corazones aleatorios
        setInterval(() => {
            const heartsContainer = document.querySelector('.hearts');
            const heart = document.createElement('div');
            heart.className = 'heart';
            const symbols = ['💖', '💕', '💗', '💓', '💝', '🌸', '🌺', '🌷', '✨'];
            heart.textContent = symbols[Math.floor(Math.random() * symbols.length)];
            heart.style.left = Math.random() * 100 + '%';
            heart.style.animationDuration = (10 + Math.random() * 10) + 's';
            heartsContainer.appendChild(heart);
            
            setTimeout(() => {
                heart.remove();
            }, 20000);
        }, 3000);
    </script>
</body>
</html>
    """

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
    # Redirigir a Discord OAuth2
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
    
    # Intercambiar código por tokens
    tokens = exchange_code(code)
    if not tokens:
        return render_error("Error al obtener tokens de acceso")
    
    access_token = tokens.get('access_token')
    
    # Obtener información del usuario
    user_data = get_user_info(access_token)
    if not user_data:
        return render_error("Error al obtener información del usuario")
    
    # Actualizar Linked Roles
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
    
    # Obtener avatar
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
    
    # Verificar firma de Discord (si hay PUBLIC_KEY configurada)
    if PUBLIC_KEY:
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if signature and timestamp:
            try:
                from nacl.signing import VerifyKey
                from nacl.exceptions import BadSignature
                
                verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
                body = request.data.decode('utf-8')
                message = timestamp.encode() + body.encode()
                
                verify_key.verify(message, bytes.fromhex(signature))
            except Exception:
                return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    # Tipo 1: PING - Discord verifica el endpoint
    if data.get('type') == 1:
        return jsonify({'type': 1})
    
    # Tipo 2: APPLICATION_COMMAND - Slash commands
    if data.get('type') == 2:
        command_name = data.get('data', {}).get('name', '')
        return jsonify({
            'type': 4,
            'data': {
                'content': f'💖 Comando `/{command_name}` recibido por DESFCITA Bot ✨',
                'flags': 64  # Ephemeral
            }
        })
    
    # Tipo 3: MESSAGE_COMPONENT - Botones, selects, etc.
    if data.get('type') == 3:
        return jsonify({
            'type': 4,
            'data': {
                'content': '💕 Interacción procesada por DESFCITA Bot 🌸',
                'flags': 64
            }
        })
    
    # Tipo 5: MODAL_SUBMIT
    if data.get('type') == 5:
        return jsonify({
            'type': 4,
            'data': {
                'content': '✨ Formulario recibido correctamente 💖',
                'flags': 64
            }
        })
    
    return jsonify({'type': 1})

# ══════════════════════════════════════════════════════════════════════════════
# 🔧 ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/register-metadata", methods=['POST'])
def register_metadata_route():
    """Registrar metadata de Linked Roles (llamar una vez)"""
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
