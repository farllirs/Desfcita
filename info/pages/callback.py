"""
Páginas de callback OAuth2 - Glassmorphism
"""
from info.pages.styles import BASE_STYLES, META_TAGS

CALLBACK_SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    {meta}
    <title>Verificado — DESFCITA</title>
    {styles}
    <style>
        .success-check {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #34D399, #10B981);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 2.5rem;
            box-shadow: 0 8px 24px rgba(52, 211, 153, 0.4);
            animation: scaleIn 0.4s ease-out;
        }}
        
        @keyframes scaleIn {{
            from {{ transform: scale(0); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        
        .user-info {{
            text-align: center;
            margin-bottom: 24px;
        }}
        
        .user-avatar {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            border: 3px solid var(--glass-border);
            margin-bottom: 12px;
        }}
        
        .user-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .benefits-list {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            margin: 24px 0;
        }}
        
        .benefit {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .benefit-icon {{
            width: 28px;
            height: 28px;
            border-radius: 8px;
            background: rgba(52, 211, 153, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="success-check">✓</div>
            
            <h1>Cuenta Verificada</h1>
            
            <div class="user-info">
                <img src="{avatar_url}" alt="Avatar" class="user-avatar" onerror="this.style.display='none'">
                <div class="user-name">{display_name}</div>
            </div>
            
            <div class="status-badge" style="display: flex; justify-content: center;">
                <div class="status-dot"></div>
                <span class="status-text">Vinculación exitosa</span>
            </div>
            
            <div class="benefits-list">
                <div class="benefit">
                    <span class="benefit-icon">✓</span>
                    <span>Rol verificado activado</span>
                </div>
                <div class="benefit">
                    <span class="benefit-icon">⚡</span>
                    <span>Linked Roles habilitados</span>
                </div>
                <div class="benefit">
                    <span class="benefit-icon">★</span>
                    <span>Acceso a funciones exclusivas</span>
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" onclick="window.close()">Cerrar ventana</button>
                <a href="/" class="btn btn-secondary">Ir al inicio</a>
            </div>
            
            <div class="footer">
                Puedes cerrar esta ventana
            </div>
        </div>
    </div>
    
    <script>
        setTimeout(() => window.close(), 8000);
    </script>
</body>
</html>
"""

CALLBACK_ERROR_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    {meta}
    <title>Error — DESFCITA</title>
    {styles}
    <style>
        .error-icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #F87171, #EF4444);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 2.5rem;
            box-shadow: 0 8px 24px rgba(248, 113, 113, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="error-icon">✕</div>
            
            <h1>Error de Verificación</h1>
            <p class="subtitle">No se pudo completar la vinculación</p>
            
            <div class="info-box error">
                <p style="margin: 0; text-align: center; color: var(--error);">
                    {error_message}
                </p>
            </div>
            
            <div class="btn-group">
                <a href="/verify-user" class="btn btn-primary">Intentar de nuevo</a>
                <a href="/" class="btn btn-secondary">Volver al inicio</a>
            </div>
            
            <div class="footer">
                Si el problema persiste, contacta soporte
            </div>
        </div>
    </div>
</body>
</html>
"""

def render_success(user_data, avatar_url):
    """Renderizar página de éxito"""
    from info.discord_oauth import format_user_display
    return CALLBACK_SUCCESS_HTML.format(
        meta=META_TAGS,
        styles=BASE_STYLES,
        avatar_url=avatar_url,
        display_name=format_user_display(user_data)
    )

def render_error(error_message):
    """Renderizar página de error"""
    return CALLBACK_ERROR_HTML.format(
        meta=META_TAGS,
        styles=BASE_STYLES,
        error_message=error_message
    )
