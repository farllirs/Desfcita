from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DESFCITA Bot</title>
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
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }
        
        .container {
            text-align: center;
            z-index: 10;
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
            animation: bounce 2s ease-in-out infinite;
        }
        
        h1 {
            font-size: 3rem;
            color: #e94560;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        .status {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px 30px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            margin-top: 20px;
            animation: fadeInUp 1s ease-out;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite;
            box-shadow: 0 0 20px #00ff88;
        }
        
        .status-text {
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 500;
        }
        
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
        }
        
        .particle {
            position: absolute;
            width: 6px;
            height: 6px;
            background: rgba(233, 69, 96, 0.6);
            border-radius: 50%;
            animation: float 15s infinite;
        }
        
        .particle:nth-child(1) { left: 10%; animation-delay: 0s; }
        .particle:nth-child(2) { left: 20%; animation-delay: 2s; background: rgba(0, 255, 136, 0.6); }
        .particle:nth-child(3) { left: 30%; animation-delay: 4s; }
        .particle:nth-child(4) { left: 40%; animation-delay: 1s; background: rgba(0, 255, 136, 0.6); }
        .particle:nth-child(5) { left: 50%; animation-delay: 3s; }
        .particle:nth-child(6) { left: 60%; animation-delay: 5s; background: rgba(0, 255, 136, 0.6); }
        .particle:nth-child(7) { left: 70%; animation-delay: 2.5s; }
        .particle:nth-child(8) { left: 80%; animation-delay: 1.5s; background: rgba(0, 255, 136, 0.6); }
        .particle:nth-child(9) { left: 90%; animation-delay: 3.5s; }
        .particle:nth-child(10) { left: 95%; animation-delay: 4.5s; background: rgba(0, 255, 136, 0.6); }
        
        .wave {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 200%;
            height: 200px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23e94560' fill-opacity='0.2' d='M0,160L48,170.7C96,181,192,203,288,197.3C384,192,480,160,576,165.3C672,171,768,213,864,213.3C960,213,1056,171,1152,149.3C1248,128,1344,128,1392,128L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") repeat-x;
            animation: wave 10s linear infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 20px rgba(233, 69, 96, 0.5); }
            to { text-shadow: 0 0 40px rgba(233, 69, 96, 0.8), 0 0 60px rgba(233, 69, 96, 0.4); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
        }
        
        @keyframes wave {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
    </style>
</head>
<body>
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="wave"></div>
    
    <div class="container">
        <div class="logo">🤖</div>
        <h1>DESFCITA</h1>
        <div class="status">
            <div class="status-dot"></div>
            <span class="status-text">Bot Activo</span>
        </div>
    </div>
</body>
</html>
    """

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
