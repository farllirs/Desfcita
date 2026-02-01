VERIFY_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificación - DESFCITA Bot 💖</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8dc7 25%, #ffc1e3 50%, #ff8dc7 75%, #ff6b9d 100%);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            font-family: 'Quicksand', sans-serif;
            padding: 20px;
        }
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            padding: 50px 40px;
            box-shadow: 0 25px 70px rgba(255, 105, 180, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
            text-align: center;
        }
        .icon {
            font-size: 5rem;
            margin-bottom: 20px;
            animation: bounce 2s ease-in-out infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        h1 {
            font-family: 'Pacifico', cursive;
            font-size: 2.5rem;
            background: linear-gradient(135deg, #ff1493 0%, #ff69b4 50%, #ffb6c1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        p {
            color: #fff;
            font-size: 1.2rem;
            line-height: 1.8;
            margin-bottom: 25px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .status-box {
            background: rgba(255, 182, 193, 0.4);
            border: 3px solid rgba(255, 105, 180, 0.6);
            border-radius: 20px;
            padding: 25px;
            margin: 25px 0;
        }
        .status-text {
            color: #fff;
            font-size: 1.3rem;
            font-weight: 600;
        }
        .check-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔐</div>
        <h1>Verificación 💖</h1>
        <p>Sistema de verificación de roles vinculados para DESFCITA Bot</p>
        
        <div class="status-box">
            <div class="check-icon">✅</div>
            <div class="status-text">Conexión Verificada 💕</div>
        </div>
        
        <p>Tu cuenta ha sido verificada correctamente con DESFCITA Bot. ¡Ya puedes disfrutar de todas las funciones! 🌸</p>
        
        <a href="/" class="back-link">← Volver al Inicio 💖</a>
    </div>
</body>
</html>
"""
