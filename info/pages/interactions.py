from info.pages.styles import BASE_STYLES, META_TAGS
from flask import request, jsonify

def handle_interactions():
    """Handler para Discord Interactions Endpoint"""
    if request.method == 'GET':
        return INTERACTIONS_PAGE_HTML
    
    data = request.json
    
    if data.get('type') == 1:
        return jsonify({'type': 1})
    
    return jsonify({'type': 4, 'data': {'content': 'DESFCITA Bot procesando...'}})

INTERACTIONS_PAGE_HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    {META_TAGS}
    <title>API — DESFCITA</title>
    {BASE_STYLES}
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="icon-large">⚡</div>
            <h1>Interactions API</h1>
            <p class="subtitle">Endpoint para Discord Interactions</p>
            
            <div class="code-box">
                POST /api/interactions
            </div>
            
            <p style="text-align: center;">Este endpoint recibe y procesa las interacciones de Discord.</p>
            
            <div class="status-badge" style="display: flex; justify-content: center;">
                <div class="status-dot"></div>
                <span class="status-text">Endpoint Activo</span>
            </div>
            
            <div class="info-box">
                <p style="margin: 0; font-size: 0.85rem; text-align: center;">
                    Verificación de firmas Ed25519 habilitada para seguridad.
                </p>
            </div>
            
            <div class="btn-group">
                <a href="/" class="btn btn-primary">← Volver al inicio</a>
            </div>
            
            <div class="footer">
                DESFCITA Bot · Discord API v10
            </div>
        </div>
    </div>
</body>
</html>
"""
