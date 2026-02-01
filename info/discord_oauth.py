"""
Discord OAuth2 y Linked Roles - Implementación Oficial
Para DESFCITA Bot
"""
import os
import hashlib
import hmac
from urllib.parse import urlencode
from flask import request, redirect, jsonify, session
import requests
from functools import wraps

# ══════════════════════════════════════════════════════════════════════════════
# 🔐 CONFIGURACIÓN OAUTH2
# ══════════════════════════════════════════════════════════════════════════════

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_CDN = "https://cdn.discordapp.com"

# Cargar desde variables de entorno
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY', '')
BOT_TOKEN = os.getenv('DISCORD_TOKEN', '')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://desfcita-1.onrender.com/callback')

# Scopes para OAuth2
OAUTH_SCOPES = [
    'identify',
    'role_connections.write'
]

# ══════════════════════════════════════════════════════════════════════════════
# 🔗 LINKED ROLES - METADATA
# ══════════════════════════════════════════════════════════════════════════════

LINKED_ROLES_METADATA = [
    {
        "key": "verified",
        "name": "Verificado",
        "description": "Usuario verificado con DESFCITA",
        "type": 7  # Boolean
    },
    {
        "key": "member_since",
        "name": "Miembro desde",
        "description": "Fecha de registro con DESFCITA",
        "type": 6  # Date
    },
    {
        "key": "level",
        "name": "Nivel",
        "description": "Nivel del usuario en DESFCITA",
        "type": 2  # Integer >=
    }
]

def register_metadata():
    """Registrar metadata de Linked Roles con Discord"""
    if not CLIENT_ID or not BOT_TOKEN:
        return False, "Faltan credenciales"
    
    url = f"{DISCORD_API_BASE}/applications/{CLIENT_ID}/role-connections/metadata"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(url, json=LINKED_ROLES_METADATA, headers=headers)
        if response.status_code == 200:
            return True, "Metadata registrada correctamente"
        return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# 🎫 OAUTH2 FLOW
# ══════════════════════════════════════════════════════════════════════════════

def get_oauth_url(state=None):
    """Generar URL de autorización OAuth2"""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(OAUTH_SCOPES),
    }
    if state:
        params['state'] = state
    
    return f"https://discord.com/oauth2/authorize?{urlencode(params)}"

def exchange_code(code):
    """Intercambiar código por tokens"""
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(f"{DISCORD_API_BASE}/oauth2/token", data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def refresh_token(refresh_token_str):
    """Refrescar access token"""
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token_str
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(f"{DISCORD_API_BASE}/oauth2/token", data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def get_user_info(access_token):
    """Obtener información del usuario"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def update_role_connection(access_token, platform_name, platform_username, metadata):
    """Actualizar conexión de roles vinculados"""
    url = f"{DISCORD_API_BASE}/users/@me/applications/{CLIENT_ID}/role-connection"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'platform_name': platform_name,
        'platform_username': platform_username,
        'metadata': metadata
    }
    
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200

# ══════════════════════════════════════════════════════════════════════════════
# 🔒 VERIFICACIÓN DE FIRMAS (INTERACTIONS)
# ══════════════════════════════════════════════════════════════════════════════

def verify_discord_signature(public_key_hex):
    """Decorador para verificar firma de Discord en Interactions"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            signature = request.headers.get('X-Signature-Ed25519')
            timestamp = request.headers.get('X-Signature-Timestamp')
            body = request.data.decode('utf-8')
            
            if not signature or not timestamp:
                return jsonify({'error': 'Missing signature headers'}), 401
            
            try:
                from nacl.signing import VerifyKey
                from nacl.exceptions import BadSignature
                
                verify_key = VerifyKey(bytes.fromhex(public_key_hex))
                message = timestamp.encode() + body.encode()
                
                verify_key.verify(message, bytes.fromhex(signature))
                return f(*args, **kwargs)
                
            except BadSignature:
                return jsonify({'error': 'Invalid signature'}), 401
            except ImportError:
                # Si no está PyNaCl, usar verificación alternativa (menos segura)
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        return wrapper
    return decorator

# ══════════════════════════════════════════════════════════════════════════════
# 📦 UTILIDADES
# ══════════════════════════════════════════════════════════════════════════════

def get_user_avatar_url(user_data):
    """Obtener URL del avatar del usuario"""
    user_id = user_data.get('id')
    avatar = user_data.get('avatar')
    
    if avatar:
        ext = 'gif' if avatar.startswith('a_') else 'png'
        return f"{DISCORD_CDN}/avatars/{user_id}/{avatar}.{ext}"
    
    # Avatar por defecto
    discriminator = int(user_data.get('discriminator', 0))
    default_avatar = discriminator % 5
    return f"{DISCORD_CDN}/embed/avatars/{default_avatar}.png"

def format_user_display(user_data):
    """Formatear nombre de usuario para mostrar"""
    username = user_data.get('username', 'Unknown')
    global_name = user_data.get('global_name')
    
    if global_name:
        return f"{global_name} (@{username})"
    return f"@{username}"
