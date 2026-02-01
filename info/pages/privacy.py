from info.pages.styles import BASE_STYLES, META_TAGS

PRIVACY_HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    {META_TAGS}
    <title>Política de Privacidad — DESFCITA</title>
    {BASE_STYLES}
</head>
<body>
    <div class="container">
        <div class="glass-card large">
            <div class="icon-large">🔐</div>
            <h1>Política de Privacidad</h1>
            <p class="subtitle">Tu privacidad es nuestra prioridad</p>
            
            <div class="info-box">
                <p style="margin: 0; text-align: center;">Esta política explica qué datos recopilamos y cómo los usamos.</p>
            </div>
            
            <h2><span class="icon">✦</span> Datos Recopilados</h2>
            <ul>
                <li>IDs de Discord (usuarios, servidores, canales)</li>
                <li>Configuraciones personalizadas del servidor</li>
                <li>Mensajes de tickets (solo mientras están activos)</li>
            </ul>
            
            <h2><span class="icon">✦</span> Uso de Datos</h2>
            <ul>
                <li>Proporcionar funcionalidades del bot</li>
                <li>Personalizar la experiencia</li>
                <li>Mejorar nuestros servicios</li>
            </ul>
            
            <h2><span class="icon">✦</span> Almacenamiento</h2>
            <p>Los datos se almacenan de forma segura y solo se mantienen mientras sean necesarios.</p>
            
            <h2><span class="icon">✦</span> Tus Derechos</h2>
            <ul>
                <li>Solicitar eliminación de tus datos</li>
                <li>Acceder a tu información</li>
                <li>Retirar el bot en cualquier momento</li>
            </ul>
            
            <div class="btn-group">
                <a href="/" class="btn btn-primary">← Volver al inicio</a>
            </div>
            
            <div class="footer">
                DESFCITA Bot · Última actualización: Febrero 2026
            </div>
        </div>
    </div>
</body>
</html>
"""
