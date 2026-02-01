"""
Página de callback OAuth2
"""
from datetime import datetime

CALLBACK_SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificación Exitosa - DESFCITA Bot 💖</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8dc7 25%, #ffc1e3 50%, #ff8dc7 75%, #ff6b9d 100%);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            font-family: 'Quicksand', sans-serif;
            padding: 20px;
        }}
        @keyframes gradient-shift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .container {{
            max-width: 500px;
            width: 100%;
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            padding: 50px 40px;
            box-shadow: 0 25px 70px rgba(255, 105, 180, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
            text-align: center;
        }}
        .avatar {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 4px solid rgba(255, 182, 193, 0.8);
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(255, 105, 180, 0.4);
        }}
        .success-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
            animation: bounce 2s ease-in-out infinite;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-15px); }}
        }}
        h1 {{
            font-family: 'Pacifico', cursive;
            font-size: 2.2rem;
            background: linear-gradient(135deg, #ff1493 0%, #ff69b4 50%, #ffb6c1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
        }}
        .username {{
            color: #fff;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}
        p {{
            color: rgba(255,255,255,0.95);
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .status-box {{
            background: rgba(0, 255, 136, 0.2);
            border: 2px solid rgba(0, 255, 136, 0.5);
            border-radius: 15px;
            padding: 15px 25px;
            margin: 20px 0;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }}
        .status-dot {{
            width: 12px;
            height: 12px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.2); }}
        }}
        .benefits {{
            text-align: left;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }}
        .benefit-item {{
            color: #fff;
            padding: 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .close-btn {{
            display: inline-block;
            margin-top: 20px;
            padding: 15px 40px;
            background: linear-gradient(135deg, #ff1493, #ff69b4);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .close-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255, 105, 180, 0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{avatar_url}" alt="Avatar" class="avatar" onerror="this.style.display='none'">
        <div class="success-icon">✅</div>
        <h1>¡Verificación Exitosa! 💖</h1>
        <p class="username">{display_name}</p>
        
        <div class="status-box">
            <div class="status-dot"></div>
            <span style="color: #fff; font-weight: 600;">Cuenta Vinculada</span>
        </div>
        
        <p>Tu cuenta de Discord ha sido vinculada exitosamente con DESFCITA Bot 🌸</p>
        
        <div class="benefits">
            <div class="benefit-item">✨ Rol verificado activado</div>
            <div class="benefit-item">💖 Acceso a funciones exclusivas</div>
            <div class="benefit-item">🌸 Linked Roles habilitados</div>
        </div>
        
        <button class="close-btn" onclick="window.close()">Cerrar Ventana 💕</button>
    </div>
    
    <script>
        // Auto-cerrar después de 10 segundos
        setTimeout(() => {{
            window.close();
        }}, 10000);
    </script>
</body>
</html>
"""

CALLBACK_ERROR_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - DESFCITA Bot 💖</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8dc7 25%, #ffc1e3 50%, #ff8dc7 75%, #ff6b9d 100%);
            font-family: 'Quicksand', sans-serif;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            width: 100%;
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            padding: 50px 40px;
            box-shadow: 0 25px 70px rgba(255, 105, 180, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
            text-align: center;
        }}
        .error-icon {{ font-size: 4rem; margin-bottom: 20px; }}
        h1 {{
            font-family: 'Pacifico', cursive;
            font-size: 2rem;
            color: #ff6b6b;
            margin-bottom: 15px;
        }}
        p {{
            color: #fff;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }}
        .error-msg {{
            background: rgba(255, 100, 100, 0.2);
            border: 2px solid rgba(255, 100, 100, 0.5);
            border-radius: 10px;
            padding: 15px;
            color: #ffcccc;
            font-family: monospace;
            margin: 20px 0;
        }}
        .retry-btn {{
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(135deg, #ff1493, #ff69b4);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Error de Verificación</h1>
        <p>Hubo un problema al vincular tu cuenta.</p>
        <div class="error-msg">{error_message}</div>
        <a href="/verify-user" class="retry-btn">Intentar de Nuevo 💖</a>
    </div>
</body>
</html>
"""

def render_success(user_data, avatar_url):
    """Renderizar página de éxito"""
    from info.discord_oauth import format_user_display
    return CALLBACK_SUCCESS_HTML.format(
        avatar_url=avatar_url,
        display_name=format_user_display(user_data)
    )

def render_error(error_message):
    """Renderizar página de error"""
    return CALLBACK_ERROR_HTML.format(error_message=error_message)
