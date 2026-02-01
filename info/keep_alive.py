from flask import Flask, jsonify
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
    <meta name="theme-color" content="#1a1a2e">
    <title>DESFCITA Bot</title>
    <link rel="icon" type="image/png" href="https://cdn.discordapp.com/attachments/1465306003389026314/1467410893846348029/Screenshot_20260112-172303.png">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            color: #fff;
        }
        .card {
            text-align: center;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 24px;
            padding: 48px 40px;
            max-width: 400px;
        }
        .logo {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,0.2);
            box-shadow: 0 12px 40px rgba(255,107,157,0.4);
            margin-bottom: 24px;
        }
        h1 {
            font-size: 1.75rem;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #fff, #FFB4D0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(52,211,153,0.15);
            border: 1px solid rgba(52,211,153,0.3);
            padding: 12px 24px;
            border-radius: 100px;
            margin-top: 20px;
        }
        .dot {
            width: 8px;
            height: 8px;
            background: #34D399;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-text { color: #34D399; font-weight: 500; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://cdn.discordapp.com/attachments/1465306003389026314/1467410893846348029/Screenshot_20260112-172303.png" alt="DESFCITA" class="logo">
        <h1>DESFCITA</h1>
        <p style="color: rgba(255,255,255,0.7);">Discord Bot</p>
        <div class="status">
            <div class="dot"></div>
            <span class="status-text">En línea</span>
        </div>
    </div>
</body>
</html>
    """

@app.route("/health")
def health():
    return jsonify({'status': 'ok', 'bot': 'DESFCITA'})

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
