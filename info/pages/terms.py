TERMS_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Términos de Servicio - DESFCITA Bot 💖</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8dc7 25%, #ffc1e3 50%, #ff8dc7 75%, #ff6b9d 100%);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            font-family: 'Quicksand', sans-serif;
            padding: 40px 20px;
        }
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            padding: 50px 40px;
            box-shadow: 0 25px 70px rgba(255, 105, 180, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
        }
        h1 {
            font-family: 'Pacifico', cursive;
            font-size: 2.8rem;
            background: linear-gradient(135deg, #ff1493 0%, #ff69b4 50%, #ffb6c1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 30px;
        }
        h2 {
            color: #ff1493;
            font-size: 1.5rem;
            margin: 25px 0 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        p, li {
            color: #fff;
            font-size: 1.1rem;
            line-height: 1.8;
            margin-bottom: 15px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        ul { margin-left: 25px; }
        .back-link {
            display: inline-block;
            margin-top: 30px;
            padding: 15px 35px;
            background: linear-gradient(135deg, #ff1493, #ff69b4);
            color: #fff;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .back-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255, 105, 180, 0.5);
        }
        .updated {
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Términos de Servicio 📜💖</h1>
        
        <h2>💕 1. Aceptación de los Términos</h2>
        <p>Al usar DESFCITA Bot, aceptas estos términos de servicio. Si no estás de acuerdo, por favor no uses el bot.</p>
        
        <h2>🌸 2. Uso del Bot</h2>
        <ul>
            <li>DESFCITA Bot es un servicio gratuito para servidores de Discord</li>
            <li>No debes usar el bot para actividades ilegales o dañinas</li>
            <li>No intentes explotar vulnerabilidades del bot</li>
            <li>Respeta las políticas de Discord al usar el bot</li>
        </ul>
        
        <h2>✨ 3. Disponibilidad del Servicio</h2>
        <p>Nos esforzamos por mantener el bot disponible 24/7, pero no garantizamos disponibilidad ininterrumpida. Pueden ocurrir mantenimientos o actualizaciones.</p>
        
        <h2>💗 4. Datos y Privacidad</h2>
        <p>Consulta nuestra <a href="/privacy" style="color: #ffb6c1;">Política de Privacidad</a> para información sobre cómo manejamos tus datos.</p>
        
        <h2>🌺 5. Modificaciones</h2>
        <p>Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios serán efectivos inmediatamente.</p>
        
        <h2>💝 6. Contacto</h2>
        <p>Para preguntas sobre estos términos, contáctanos en nuestro servidor de Discord.</p>
        
        <div style="text-align: center;">
            <a href="/" class="back-link">← Volver al Inicio 💖</a>
        </div>
        
        <p class="updated">Última actualización: Febrero 2026 🌸</p>
    </div>
</body>
</html>
"""
