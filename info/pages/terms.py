from info.pages.styles import BASE_STYLES, META_TAGS

TERMS_HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    {META_TAGS}
    <title>Términos de Servicio — DESFCITA</title>
    {BASE_STYLES}
</head>
<body>
    <div class="container">
        <div class="glass-card large">
            <div class="icon-large">📋</div>
            <h1>Términos de Servicio</h1>
            <p class="subtitle">Última actualización: Febrero 2026</p>
            
            <h2><span class="icon">✦</span> Aceptación</h2>
            <p>Al usar DESFCITA Bot, aceptas estos términos. Si no estás de acuerdo, por favor no uses el bot.</p>
            
            <h2><span class="icon">✦</span> Uso del Bot</h2>
            <ul>
                <li>DESFCITA es un servicio gratuito para servidores de Discord</li>
                <li>No uses el bot para actividades ilegales o dañinas</li>
                <li>No intentes explotar vulnerabilidades</li>
                <li>Respeta las políticas de Discord</li>
            </ul>
            
            <h2><span class="icon">✦</span> Disponibilidad</h2>
            <p>Nos esforzamos por mantener el bot disponible 24/7, pero no garantizamos disponibilidad ininterrumpida.</p>
            
            <h2><span class="icon">✦</span> Privacidad</h2>
            <p>Consulta nuestra <a href="/privacy">Política de Privacidad</a> para más información.</p>
            
            <h2><span class="icon">✦</span> Modificaciones</h2>
            <p>Podemos modificar estos términos en cualquier momento. Los cambios serán efectivos inmediatamente.</p>
            
            <div class="btn-group">
                <a href="/" class="btn btn-primary">← Volver al inicio</a>
            </div>
            
            <div class="footer">
                DESFCITA Bot · Todos los derechos reservados
            </div>
        </div>
    </div>
</body>
</html>
"""
