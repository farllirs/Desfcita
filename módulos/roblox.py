import discord
from discord.ext import commands, tasks
from discord import ui
import aiohttp
import json
import os
from datetime import datetime
import io
import traceback
from dotenv import load_dotenv
import asyncio
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp as aio

load_dotenv()

# ════════════════════════════════════════════════════════════════
# 📁 CONFIGURACIÓN GLOBAL
# ════════════════════════════════════════════════════════════════

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
CACHE_FILE = os.path.join(DATA_DIR, 'roblox_cache.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'roblox_config.json')
FONT_CLASSIC = os.path.join(FONTS_DIR, 'classic.ttf')

os.makedirs(DATA_DIR, exist_ok=True)

# ════════════════════════════════════════════════════════════════
# 🎨 CONFIGURACIÓN EDITABLE DEL PANEL
# ════════════════════════════════════════════════════════════════

PANEL_COLORS = {
    "bg_primary": (15, 15, 35),      # Fondo oscuro
    "bg_secondary": (40, 30, 80),    # Fondo secundario
    "accent_1": (120, 200, 255),     # Azul claro (cyan)
    "accent_2": (200, 100, 255),     # Morado claro
    "text_white": (255, 255, 255),
    "text_gray": (150, 180, 220),
    "success": (100, 255, 150),
    "warning": (255, 200, 80),
}

PANEL_SIZES = {
    "width": 1200,
    "height": 700,
    "title_font": 80,
    "subtitle_font": 35,
    "text_font": 28,
    "button_font": 22,
}

# ════════════════════════════════════════════════════════════════
# 🖼️ FUNCIONES DE IMAGEN
# ════════════════════════════════════════════════════════════════

def create_gradient_bg(width: int, height: int, color1: tuple, color2: tuple) -> Image.Image:
    """Crear fondo con gradiente"""
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        
        for x in range(width):
            pixels[x, y] = (r, g, b, 255)
    
    return img

def download_image_bytes(url: str) -> Image.Image:
    """Descargar imagen desde URL y retornar como PIL Image"""
    try:
        import requests
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except:
        pass
    return None

def create_circular_image(image: Image.Image, size: int) -> Image.Image:
    """Crear imagen circular con máscara y borde"""
    try:
        # Redimensionar a cuadrado
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        
        # Crear máscara circular
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, size, size], fill=255)
        
        # Aplicar máscara
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(image.convert('RGBA'), (0, 0), mask)
        return output
    except:
        return Image.new('RGBA', (size, size), (0, 0, 0, 0))

def create_glass_rect(width: int, height: int, color_rgb: tuple, opacity: int = 25) -> Image.Image:
    """Crear rectángulo con efecto glass type iPhone"""
    glass = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glass)
    
    # Fondo glass semi-transparente con white
    draw.rectangle([0, 0, width, height], 
                   fill=(255, 255, 255, opacity),
                   outline=color_rgb + (120,),
                   width=2)
    
    # Pequeños highlights para efecto glass
    draw.line([(2, 2), (width-2, 2)], fill=(255, 255, 255, 80), width=1)
    
    return glass

def apply_shadow(image: Image.Image, offset: int = 10, blur: int = 15) -> Image.Image:
    """Aplicar sombra suave a una imagen"""
    shadow = Image.new('RGBA', 
                       (image.width + offset*2, image.height + offset*2), 
                       (0, 0, 0, 0))
    
    shadow_layer = Image.new('RGBA', 
                            (image.width + offset*2, image.height + offset*2), 
                            (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.rectangle([offset, offset, image.width + offset, image.height + offset],
                         fill=(0, 0, 0, 40))
    
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur))
    shadow = Image.alpha_composite(shadow, shadow_layer)
    shadow.paste(image, (offset//2, offset//2), image)
    
    return shadow

def create_rounded_rectangle(draw, xy, radius=20, fill=None, outline=None, width=1):
    """Dibujar rectángulo redondeado"""
    x1, y1, x2, y2 = xy
    
    # Esquinas
    draw.arc([x1, y1, x1 + radius*2, y1 + radius*2], 180, 270, fill=outline, width=width)
    draw.arc([x2 - radius*2, y1, x2, y1 + radius*2], 270, 360, fill=outline, width=width)
    draw.arc([x1, y2 - radius*2, x1 + radius*2, y2], 90, 180, fill=outline, width=width)
    draw.arc([x2 - radius*2, y2 - radius*2, x2, y2], 0, 90, fill=outline, width=width)
    
    # Líneas
    draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
    draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
    draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
    draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)
    
    if fill:
        draw.rectangle([x1 + width, y1 + width, x2 - width, y2 - width], fill=fill)

def load_font(size: int):
    """Cargar font classic.ttf con fallback a default"""
    try:
        if os.path.exists(FONT_CLASSIC):
            return ImageFont.truetype(FONT_CLASSIC, size)
    except:
        pass
    return ImageFont.load_default()

def create_roblox_verification_panel(group_id: int, server_name: str) -> io.BytesIO:
    """Crear imagen del panel de verificación Roblox con estilo mejorado"""
    
    try:
        w, h = PANEL_SIZES["width"], PANEL_SIZES["height"]
        pos = PANEL_POSITIONS  # Alias para acceso rápido
        
        # Fondo con gradiente
        bg = create_gradient_bg(w, h, PANEL_COLORS["bg_primary"], PANEL_COLORS["bg_secondary"])
        draw = ImageDraw.Draw(bg)
        
        # ════════════════════════════════════════════════════════════════
        # BANNER CON LÍNEAS DECORATIVAS
        # ════════════════════════════════════════════════════════════════
        
        banner_y = pos["banner_y"]
        banner_h = pos["banner_h"]
        
        # Línea superior
        draw.line([(50, banner_y), (w - 50, banner_y)], fill=PANEL_COLORS["accent_1"], width=3)
        
        # Título principal
        try:
            title_font = load_font(PANEL_SIZES["title_font"])
            title_x, title_y = pos["banner_title"]
            draw.text((title_x, banner_y + title_y), PANEL_TEXTS.get("title", "🎮 ROBLOX"), font=title_font, fill=PANEL_COLORS["accent_1"])
            
            # Subtítulo
            subtitle_font = load_font(PANEL_SIZES["subtitle_font"])
            subtitle_x, subtitle_y = pos["banner_subtitle"]
            draw.text((subtitle_x, banner_y + subtitle_y), PANEL_TEXTS.get("subtitle", "Verificación de Cuenta"), font=subtitle_font, fill=PANEL_COLORS["accent_2"])
        except:
            pass
        
        # Línea inferior del banner
        draw.line([(50, banner_y + banner_h), (w - 50, banner_y + banner_h)], fill=PANEL_COLORS["accent_2"], width=2)
        
        # ════════════════════════════════════════════════════════════════
        # CONTENIDO PRINCIPAL
        # ════════════════════════════════════════════════════════════════
        
        content_y = banner_y + banner_h + pos["content_offset"]
        
        try:
            text_font = load_font(PANEL_SIZES["text_font"])
            
            # Sección: Grupo Roblox
            group_x, group_y_offset = pos["group_section"]
            draw.text((group_x, content_y + group_y_offset), PANEL_TEXTS.get("group_section", "📍 Grupo Roblox"), font=text_font, fill=PANEL_COLORS["accent_1"])
            
            id_x, id_y_offset = pos["group_id"]
            draw.text((id_x, content_y + id_y_offset), f"{PANEL_TEXTS.get('group_id_prefix', 'ID: ')}{group_id}", font=text_font, fill=PANEL_COLORS["text_white"])
            
            content_y += pos["group_content_gap"]
            
            # Pasos
            steps_x, steps_y_offset = pos["steps_header"]
            draw.text((steps_x, content_y + steps_y_offset), PANEL_TEXTS.get("steps_header", "📋 Pasos para verificar:"), font=text_font, fill=PANEL_COLORS["accent_1"])
            content_y += 35
            
            steps = [
                PANEL_TEXTS.get("step_1", "1️⃣  Abre el enlace del grupo (botón verde)"),
                PANEL_TEXTS.get("step_2", "2️⃣  Haz clic en 'Unirse al Grupo'"),
                PANEL_TEXTS.get("step_3", "3️⃣  Regresa y presiona '✅ Ya me uní'"),
                PANEL_TEXTS.get("step_4", "4️⃣  Recibe tu rol automáticamente")
            ]
            
            step_x, _ = pos["steps_offset"]
            for step in steps:
                draw.text((step_x, content_y), step, font=text_font, fill=PANEL_COLORS["text_white"])
                content_y += pos["steps_gap"]
        
        except:
            pass
        
        # ════════════════════════════════════════════════════════════════
        # FOOTER
        # ════════════════════════════════════════════════════════════════
        
        footer_y = h - 50
        draw.line([(50, footer_y), (w - 50, footer_y)], fill=PANEL_COLORS["accent_1"], width=2)
        
        try:
            footer_font = load_font(PANEL_SIZES.get("footer_size", 18))
            footer_text = f"🎮 Servidor: {server_name} • Sistema Automático de Verificación"
            footer_x, footer_y_offset = pos["footer_text"]
            draw.text((footer_x, footer_y + footer_y_offset), footer_text, font=footer_font, fill=PANEL_COLORS["text_gray"])
        except:
            pass
        
        # Guardar imagen
        img_bytes = io.BytesIO()
        bg.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    except:
        pass
        
        # Imagen de fallback
        blank = Image.new('RGBA', (PANEL_SIZES["width"], PANEL_SIZES["height"]), PANEL_COLORS["bg_primary"])
        img_bytes = io.BytesIO()
        blank.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

# ════════════════════════════════════════════════════════════════
# 📦 FUNCIONES DE CACHÉ
# ════════════════════════════════════════════════════════════════

def load_cache() -> dict:
    """Cargar caché de usuarios"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_cache(cache: dict):
    """Guardar caché"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except:
        pass

def load_config() -> dict:
    """Cargar configuración de gremios"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_config(config: dict):
    """Guardar configuración"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except:
        pass

# ════════════════════════════════════════════════════════════════
# 🎮 MODALES Y VISTAS
# ════════════════════════════════════════════════════════════════

class PersonalizarPerfilModal(ui.Modal, title="🎨 Personalizar Perfil"):
    """Modal para personalizar perfil del clan con fondo"""
    
    descripcion = ui.TextInput(
        label="📝 Descripción",
        placeholder="Mi descripción en el clan...",
        required=False,
        max_length=200
    )
    
    color_principal = ui.TextInput(
        label="🎨 Color Principal (Hex sin #)",
        placeholder="FF1493",
        required=False,
        max_length=6
    )
    
    color_secundario = ui.TextInput(
        label="🎨 Color Secundario (Hex sin #)",
        placeholder="00BFFF",
        required=False,
        max_length=6
    )
    
    url_fondo = ui.TextInput(
        label="🖼️ URL Fondo (imagen/GIF)",
        placeholder="https://ejemplo.com/imagen.png",
        required=False,
        max_length=500
    )
    
    opacidad = ui.TextInput(
        label="💫 Opacidad Fondo (0-100)",
        placeholder="50",
        required=False,
        max_length=3
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Validar opacidad
        try:
            opacidad = int(self.opacidad.value) if self.opacidad.value else 50
            opacidad = max(0, min(100, opacidad))  # Limitar entre 0-100
        except:
            opacidad = 50
        
        personalizacion = {
            "descripcion": self.descripcion.value or "Miembro del Clan",
            "color_principal": self.color_principal.value or "FF1493",
            "color_secundario": self.color_secundario.value or "00BFFF",
            "url_fondo": self.url_fondo.value or "",
            "opacidad": opacidad,
        }
        
        user_key = str(interaction.user.id)
        if user_key not in self.cog.cache:
            await interaction.followup.send("❌ Debes vincularte primero", ephemeral=True)
            return
        
        self.cog.cache[user_key]["personalizacion"] = personalizacion
        save_cache(self.cog.cache)
        
        embed = discord.Embed(
            title="✅ Perfil Actualizado",
            description="Tu perfil ha sido personalizado",
            color=0x00FF00
        )
        embed.add_field(name="📝 Descripción", value=personalizacion["descripcion"], inline=False)
        embed.add_field(name="🎨 Colores", value=f"Principal: #{personalizacion['color_principal']}\nSecundario: #{personalizacion['color_secundario']}", inline=False)
        if personalizacion["url_fondo"]:
            embed.add_field(name="🖼️ Fondo", value=f"✅ Configurado (Opacidad: {personalizacion['opacidad']}%)", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class RobloxVerificationModal(ui.Modal, title="🎮 Vinculación Roblox"):
    """Modal para ingresar usuario de Roblox"""
    
    username = ui.TextInput(
        label="Usuario de Roblox",
        placeholder="Ej: BuilderMan",
        required=True,
        min_length=1,
        max_length=20
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.cog.verify_roblox_user(interaction, self.username.value)

class PersonalizarPerfilView(ui.View):
    """Vista para abrir modal de personalización"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @ui.button(label="🎨 Personalizar Perfil", style=discord.ButtonStyle.primary, emoji="✨")
    async def personalize(self, interaction: discord.Interaction, button: ui.Button):
        user_key = str(interaction.user.id)
        if user_key not in self.cog.cache:
            await interaction.response.send_message("❌ Debes vincular tu cuenta primero", ephemeral=True)
            return
        
        modal = PersonalizarPerfilModal(self.cog)
        await interaction.response.send_modal(modal)

class VerificationView(ui.View):
    """Vista con botones de verificación"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @ui.button(label="🎮 Verificar Roblox", style=discord.ButtonStyle.primary)
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = RobloxVerificationModal(self.cog)
        await interaction.response.send_modal(modal)

class AñadirAmigoView(ui.View):
    """Vista para añadir como amigo y ver perfil"""
    
    def __init__(self, target_user_id: int, target_username: str, roblox_user_id: int, cog):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id
        self.target_username = target_username
        self.roblox_user_id = roblox_user_id
        self.cog = cog
        
        # Botón para ir al perfil de Roblox
        self.add_item(ui.Button(
            label="👤 Ir al Perfil Roblox",
            style=discord.ButtonStyle.link,
            url=f"https://www.roblox.com/users/{roblox_user_id}/profile",
            emoji="🎮"
        ))
    
    @ui.button(label="➕ Añadir Amigo", style=discord.ButtonStyle.success, emoji="👥")
    async def add_friend(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id == self.target_user_id:
            await interaction.response.send_message("No puedes añadirte a ti mismo", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Guardar solicitud de amistad
        if "friend_requests" not in self.cog.cache:
            self.cog.cache["friend_requests"] = {}
        
        request_key = f"{interaction.user.id}_{self.target_user_id}"
        
        if request_key in self.cog.cache.get("friend_requests", {}):
            await interaction.followup.send("Ya enviaste una solicitud a este usuario", ephemeral=True)
            return
        
        self.cog.cache["friend_requests"][request_key] = {
            "from_id": interaction.user.id,
            "from_name": interaction.user.name,
            "to_id": self.target_user_id,
            "to_name": self.target_username,
            "sent_at": datetime.now().isoformat()
        }
        save_cache(self.cog.cache)
        
        embed = discord.Embed(
            title="✅ Solicitud Enviada",
            description=f"Solicitud de amistad enviada a **{self.target_username}**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Espera a que acepten tu solicitud")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class ConfirmVerificationView(ui.View):
    """Vista con botón de confirmación después de verificar"""
    
    def __init__(self, cog, user_id: int, roblox_username: str, roblox_user_id: int, guild_id: int, group_id: int = 0):
        super().__init__(timeout=3600)
        self.cog = cog
        self.user_id = user_id
        self.roblox_username = roblox_username
        self.roblox_user_id = roblox_user_id
        self.guild_id = guild_id
        self.group_id = group_id
        
        # Agregar botón de link
        if group_id > 0:
            self.add_item(ui.Button(
                label="🔗 Ir al grupo",
                style=discord.ButtonStyle.link,
                url=f"https://www.roblox.com/communities/{group_id}/redirect"
            ))
    
    @ui.button(label="✅ Ya me uní al grupo", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botón no es para ti", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.cog.confirm_verification(interaction, self.roblox_username, self.roblox_user_id)

async def setup(bot):
    await bot.add_cog(Roblox(bot))

# ════════════════════════════════════════════════════════════════
# 🎮 CLASE PRINCIPAL - ROBLOX COG
# ════════════════════════════════════════════════════════════════

class Roblox(commands.Cog):
    """Sistema de Vinculación de Cuentas Roblox - Únete al Clan"""
    
    def __init__(self, bot):
        self.bot = bot
        self.cache = load_cache()
        self.config = load_config()
        self.session = None
        self.sync_cache.start()
    
    def cog_unload(self):
        """Limpiar recursos al descargar el cog"""
        if self.sync_cache.is_running():
            self.sync_cache.cancel()
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Obtener o crear sesión HTTP"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    @tasks.loop(minutes=5)
    async def sync_cache(self):
        """Sincronizar caché cada 5 minutos"""
        save_cache(self.cache)
        save_config(self.config)
    
    @sync_cache.before_loop
    async def before_sync(self):
        await self.bot.wait_until_ready()
    
    # ════════════════════════════════════════════════════════════════
    # ✅ VERIFICACIÓN DE USUARIOS
    # ════════════════════════════════════════════════════════════════
    
    async def verify_roblox_user(self, interaction: discord.Interaction, roblox_username: str):
        """Vincular cuenta de Roblox y unirse al clan"""
        
        try:
            session = await self.get_session()
            
            # Obtener ID de usuario de Roblox
            async with session.post(
                f"https://users.roblox.com/v1/usernames/users",
                json={"usernames": [roblox_username]}
            ) as resp:
                if resp.status != 200:
                    await interaction.followup.send(
                        "❌ Usuario de Roblox no encontrado. Verifica el nombre.",
                        ephemeral=True
                    )
                    return
                
                data = await resp.json()
                if not data.get("data") or len(data.get("data", [])) == 0:
                    await interaction.followup.send(
                        "❌ Usuario de Roblox no encontrado. Verifica el nombre.",
                        ephemeral=True
                    )
                    return
                
                roblox_user_id = data["data"][0]["id"]
            
            # Obtener configuración del servidor
            guild_id = interaction.guild.id
            guild_config = self.config.get(str(guild_id))
            
            if not guild_config:
                await interaction.followup.send(
                    "⚠️ Este servidor no está configurado. Pide a un admin que use `-roblox-setup`",
                    ephemeral=True
                )
                return
            
            group_id = guild_config.get("group_id")
            role_id = guild_config.get("role_id")
            
            # Guardar en caché
            user_key = str(interaction.user.id)
            self.cache[user_key] = {
                "discord_id": interaction.user.id,
                "roblox_username": roblox_username,
                "roblox_user_id": roblox_user_id,
                "guild_id": guild_id,
                "verified": False,
                "verified_at": None
            }
            save_cache(self.cache)
            
            # Crear vista de confirmación
            view = ConfirmVerificationView(self, interaction.user.id, roblox_username, roblox_user_id, guild_id, group_id)
            
            embed = discord.Embed(
                title="🎮 Vinculación de Cuenta Roblox",
                description=f"**Tu usuario Roblox:** {roblox_username}",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🔗 Únete al Clan",
                value="1️⃣ Abre el enlace (botón verde)\n2️⃣ Haz clic en '➕ Unirse al Grupo'\n3️⃣ Presiona el botón '✅ Ya me uní'\n4️⃣ ¡Recibe tu rol automáticamente!",
                inline=False
            )
            
            embed.add_field(
                name="💎 Beneficios",
                value="✨ Rol exclusivo del clan\n🏆 Acceso a canales privados\n🎮 Conexión con el grupo Roblox",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        except:
            await interaction.followup.send(
                "❌ Error durante la verificación",
                ephemeral=True
            )
    
    async def confirm_verification(self, interaction: discord.Interaction, roblox_username: str, roblox_user_id: int):
        """Confirmar vinculación y asignar rol del clan"""
        
        try:
            guild_id = interaction.guild.id
            guild_config = self.config.get(str(guild_id))
            
            if not guild_config:
                await interaction.followup.send("⚠️ Configuración no encontrada", ephemeral=True)
                return
            
            role_id = guild_config.get("role_id")
            role = interaction.guild.get_role(role_id)
            
            if not role:
                await interaction.followup.send("❌ El rol no existe en este servidor", ephemeral=True)
                return
            
            # Asignar rol automáticamente
            try:
                await interaction.user.add_roles(role)
            except discord.Forbidden:
                await interaction.followup.send(
                    f"⚠️ No tengo permisos para asignar el rol {role.mention}",
                    ephemeral=True
                )
                return
            
            # Actualizar caché
            user_key = str(interaction.user.id)
            if user_key in self.cache:
                self.cache[user_key]["verified"] = True
                self.cache[user_key]["verified_at"] = datetime.now().isoformat()
            
            save_cache(self.cache)
            
            # Respuesta de éxito
            embed = discord.Embed(
                title="✅ ¡Cuenta Vinculada!",
                description=f"¡Bienvenido al clan en {interaction.guild.name}!",
                color=discord.Color.green()
            )
            embed.add_field(name="🎮 Usuario Roblox", value=f"**{roblox_username}**", inline=True)
            embed.add_field(name="🎭 Rol Clan", value=f"{role.mention}", inline=True)
            embed.add_field(name="💎 Estado", value="✅ Miembro del Clan", inline=False)
            embed.add_field(name="📅 Vinculado", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=False)
            embed.set_footer(text="¡Disfruta con el clan!")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except:
            await interaction.followup.send("❌ Error durante la confirmación", ephemeral=True)
    
    # ════════════════════════════════════════════════════════════════
    # ⚙️ COMANDOS DE ADMINISTRACIÓN
    # ════════════════════════════════════════════════════════════════
    
    @commands.command(name="roblox-setup", aliases=["clan-setup"])
    @commands.has_permissions(administrator=True)
    async def setup_roblox(self, ctx, group_id: int, role: discord.Role):
        """Configurar Sistema de Vinculación al Clan Roblox
        
        Uso: -clan-setup <group_id> @role
        Ej: -clan-setup 12345678 @Miembro del Clan
        """
        
        try:
            # Verificar que el grupo existe
            session = await self.get_session()
            async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Grupo de Roblox no encontrado", delete_after=10)
                    return
                
                group_data = await resp.json()
                group_name = group_data.get("name", f"Grupo {group_id}")
            
            # Guardar configuración
            guild_id = str(ctx.guild.id)
            self.config[guild_id] = {
                "group_id": group_id,
                "group_name": group_name,
                "role_id": role.id,
                "role_name": role.name,
                "setup_by": str(ctx.author),
                "setup_at": datetime.now().isoformat()
            }
            save_config(self.config)
            
            # Respuesta
            embed = discord.Embed(
                title="✅ Clan Configurado",
                description="Sistema de vinculación Roblox activado",
                color=discord.Color.green()
            )
            embed.add_field(name="🎮 Clan Roblox", value=f"**{group_name}** (ID: `{group_id}`)", inline=False)
            embed.add_field(name="🎭 Rol Miembro", value=role.mention, inline=False)
            embed.add_field(name="📝 Siguiente", value="Usa `-clan-panel` para mostrar el panel de vinculación", inline=False)
            embed.set_footer(text="Listo para que se unan!")
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logging.error(f"Error en setup: {e}")
            await ctx.send(f"❌ Error: {str(e)[:100]}", delete_after=10)
    
    @commands.command(name="clan-panel", aliases=["panel-roblox"])
    @commands.has_permissions(administrator=True)
    async def show_panel(self, ctx):
        """Mostrar panel de vinculación al clan Roblox"""
        
        try:
            guild_id = str(ctx.guild.id)
            guild_config = self.config.get(guild_id)
            
            if not guild_config:
                await ctx.send(
                    "⚠️ Clan no configurado. Usa `-clan-setup <group_id> @role`",
                    delete_after=10
                )
                return
            
            group_id = guild_config.get("group_id")
            
            async with ctx.typing():
                # Crear imagen del panel
                panel_image = create_roblox_verification_panel(group_id, ctx.guild.name)
                file = discord.File(panel_image, filename="roblox_panel.png")
                
                # Crear embed
                embed = discord.Embed(
                    title="🎮 Únete al Clan Roblox",
                    description="Vincula tu cuenta y únete a nuestro clan",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="🎯 Clan Roblox",
                    value=f"**{guild_config.get('group_name', 'Clan')}**\n[🔗 Ir al Clan]({f'https://www.roblox.com/communities/{group_id}/redirect'})",
                    inline=False
                )
                
                embed.add_field(
                    name="🎭 Rol Miembro",
                    value=f"<@&{guild_config.get('role_id')}>",
                    inline=True
                )
                
                embed.add_field(
                    name="⚡ Automático",
                    value="El rol se asigna al vincularte",
                    inline=True
                )
                
                embed.set_image(url="attachment://roblox_panel.png")
                embed.set_footer(text="Sistema automático de verificación")
                
                # Vista con botones
                view = VerificationView(self)
                
                await ctx.send(embed=embed, file=file, view=view)
        
        except Exception as e:
            logging.error(f"Error mostrando panel: {e}")
            traceback.print_exc()
            await ctx.send(f"❌ Error: {str(e)[:100]}")
    
    @commands.command(name="mi-clan", aliases=["mi-roblox"])
    async def my_roblox(self, ctx):
        """🎮 Ver tu perfil en el clan con panel visual"""
        
        user_key = str(ctx.author.id)
        user_data = self.cache.get(user_key)
        
        if not user_data:
            embed = discord.Embed(
                title="ℹ️ No Vinculado",
                description="Usa `-clan-panel` para vincular tu cuenta",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        async with ctx.typing():
            try:
                # Obtener personalización
                personalizacion = user_data.get("personalizacion", {})
                descripcion = personalizacion.get("descripcion", "Miembro del Clan")
                color_principal = personalizacion.get("color_principal", "FF1493")
                color_secundario = personalizacion.get("color_secundario", "00BFFF")
                url_fondo = personalizacion.get("url_fondo", "")
                opacidad_fondo = personalizacion.get("opacidad", 50)
                
                # Obtener configuración del clan
                guild_config = self.config.get(str(ctx.guild.id), {})
                
                # Obtener roles del usuario
                user_roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
                roles_str = ", ".join(user_roles[:3]) if user_roles else "Sin roles"
                
                # Crear panel visual con efecto glass tipo iPhone - ULTRA ALTA RESOLUCIÓN
                try:
                    w, h = 1800, 800  # Aumentado de 1600x700
                    panel = Image.new('RGBA', (w, h), (15, 15, 35, 255))
                    draw = ImageDraw.Draw(panel, 'RGBA')
                    
                    # Colores personalizados
                    try:
                        color_hex_principal = tuple(int(color_principal[i:i+2], 16) for i in (0, 2, 4))
                        color_hex_secundario = tuple(int(color_secundario[i:i+2], 16) for i in (0, 2, 4))
                    except:
                        color_hex_principal = (255, 20, 147)
                        color_hex_secundario = (0, 191, 255)
                    
                    # Fondo con gradiente mejorado
                    for y in range(h):
                        ratio = y / h
                        r = int(10 + (color_hex_principal[0] - 10) * ratio * 0.25)
                        g = int(10 + (color_hex_principal[1] - 10) * ratio * 0.25)
                        b = int(30 + (color_hex_principal[2] - 30) * ratio * 0.25)
                        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
                    
                    # Aplicar fondo personalizado si existe
                    if url_fondo:
                        try:
                            fondo_img = download_image_bytes(url_fondo)
                            if fondo_img:
                                # Redimensionar al tamaño del panel (rápido)
                                fondo_img = fondo_img.resize((w, h), Image.Resampling.BILINEAR)
                                fondo_img = fondo_img.convert('RGBA')
                                
                                # Ajustar opacidad eficientemente (sin loops)
                                r, g, b, alpha_channel = fondo_img.split()
                                alpha_channel = alpha_channel.point(lambda p: int(p * opacidad_fondo / 100))
                                fondo_img.putalpha(alpha_channel)
                                
                                # Combinar fondos (operación optimizada en C)
                                panel = Image.alpha_composite(panel, fondo_img)
                        except:
                            pass  # Si falla, continúa con el fondo gradiente
                    
                    # ═══ SECCIÓN IZQUIERDA (DISCORD) ═══
                    glass_x1, glass_y1 = 40, 40
                    glass_x2, glass_y2 = 580, 760
                    
                    # Crear glass rect y aplicar
                    glass_discord = create_glass_rect(glass_x2 - glass_x1, glass_y2 - glass_y1, 
                                                      color_hex_principal, opacity=18)
                    panel.paste(glass_discord, (glass_x1, glass_y1), glass_discord)
                    draw = ImageDraw.Draw(panel)
                    
                    # Avatar de Discord - ARRIBA
                    discord_avatar = download_image_bytes(str(ctx.author.display_avatar.url))
                    if discord_avatar:
                        discord_avatar = create_circular_image(discord_avatar, 200)
                        avatar_x = glass_x1 + (glass_x2 - glass_x1 - 200) // 2
                        panel.paste(discord_avatar, (avatar_x, glass_y1 + 40), discord_avatar)
                    
                    # Nombre Discord - DEBAJO DEL AVATAR
                    try:
                        font_name = load_font(40)
                        font_label = load_font(20)
                        font_roles = load_font(18)   # Nuevo: más grande para roles
                        
                        # Nombre centrado debajo del avatar
                        draw.text((glass_x1 + 30, glass_y1 + 270), ctx.author.name, font=font_name, 
                                 fill=(255, 255, 255))
                        
                        # Label "Discord" debajo del nombre
                        draw.text((glass_x1 + 30, glass_y1 + 320), "Discord", font=font_label, 
                                 fill=color_hex_secundario)
                        
                        # Roles - TODOS (sin limite) pero máximo 8 para no saturar
                        roles_list = [role.name for role in ctx.author.roles if role.name != "@everyone"][:8]
                        
                        if roles_list:
                            # Título de roles
                            draw.text((glass_x1 + 30, glass_y1 + 370), "🎭 Roles", font=font_label, 
                                     fill=color_hex_secundario)
                            
                            # Mostrar cada rol en su propia línea con separación
                            y_offset = glass_y1 + 420
                            for idx, role in enumerate(roles_list):
                                truncated_role = role[:20] if len(role) > 20 else role
                                draw.text((glass_x1 + 40, y_offset + (idx * 30)), 
                                         f"• {truncated_role}", font=font_roles, 
                                         fill=(200, 200, 220))
                        else:
                            draw.text((glass_x1 + 30, glass_y1 + 370), "🎭 Miembro", font=font_label, 
                                     fill=color_hex_secundario)
                    except:
                        pass
                    
                    # ═══ SECCIÓN DERECHA (CLAN) ═══
                    clan_x1, clan_y1 = 620, 40
                    clan_x2, clan_y2 = 1760, 760
                    
                    glass_clan = create_glass_rect(clan_x2 - clan_x1, clan_y2 - clan_y1, 
                                                   color_hex_secundario, opacity=15)
                    panel.paste(glass_clan, (clan_x1, clan_y1), glass_clan)
                    draw = ImageDraw.Draw(panel, 'RGBA')
                    
                    # Icono Roblox (PNG)
                    try:
                        roblox_icon_path = "fonts/roblox_icon.png"
                        if os.path.exists(roblox_icon_path):
                            roblox_icon = Image.open(roblox_icon_path).convert('RGBA')
                            roblox_icon = roblox_icon.resize((160, 160), Image.Resampling.LANCZOS)
                            icon_x = clan_x1 + (clan_x2 - clan_x1 - 160) // 2
                            panel.paste(roblox_icon, (icon_x, clan_y1 + 30), roblox_icon)
                        else:
                            # Fallback: emoji
                            try:
                                emoji_font = load_font(120)
                                draw.text((clan_x1 + 400, clan_y1 + 30), "🎮", font=emoji_font)
                            except:
                                pass
                    except:
                        pass
                    
                    # Información del clan
                    try:
                        font_title = load_font(48)   # Aumentado de 34
                        font_text = load_font(24)    # Aumentado de 17
                        font_label = load_font(20)   # Aumentado de 14
                        
                        clan_name = guild_config.get('group_name', 'Tu Clan')
                        
                        draw.text((clan_x1 + 40, clan_y1 + 220), "🎯 TU CLAN", font=font_label, 
                                 fill=color_hex_secundario)
                        draw.text((clan_x1 + 40, clan_y1 + 260), clan_name, font=font_title, 
                                 fill=(255, 255, 255))
                        
                        # Separador
                        draw.line([(clan_x1 + 40, clan_y1 + 330), (clan_x2 - 40, clan_y1 + 330)],
                                 fill=color_hex_secundario + (80,), width=2)
                        
                        # Usuario Roblox
                        draw.text((clan_x1 + 40, clan_y1 + 360), "🎮 Usuario", font=font_label, 
                                 fill=color_hex_secundario)
                        draw.text((clan_x1 + 40, clan_y1 + 410), user_data.get('roblox_username'), 
                                 font=font_title, fill=(255, 255, 255))
                        
                        # Separador
                        draw.line([(clan_x1 + 40, clan_y1 + 480), (clan_x2 - 40, clan_y1 + 480)],
                                 fill=color_hex_secundario + (80,), width=2)
                        
                        # Estado
                        if user_data.get('verified'):
                            draw.text((clan_x1 + 40, clan_y1 + 510), "✅ Vinculado", font=font_text, 
                                     fill=(100, 255, 150))
                        else:
                            draw.text((clan_x1 + 40, clan_y1 + 510), "⏳ Pendiente", font=font_text, 
                                     fill=(255, 200, 80))
                        
                        # Descripción
                        draw.text((clan_x1 + 40, clan_y1 + 580), f"✨ {descripcion}", font=font_label, 
                                 fill=(200, 200, 220))
                        
                    except:
                        pass
                    
                    # Línea decorativa superior
                    draw.line([(40, 20), (1760, 20)], fill=color_hex_principal + (100,), width=3)
                    
                    # Línea decorativa inferior
                    draw.line([(40, 775), (1760, 775)], fill=color_hex_secundario + (100,), width=3)
                    
                    # Guardar imagen
                    panel_bytes = io.BytesIO()
                    panel.save(panel_bytes, format='PNG')
                    panel_bytes.seek(0)
                    
                    file = discord.File(panel_bytes, filename="perfil_clan.png")
                    embed = discord.Embed(
                        title="🎮 Tu Perfil en el Clan",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="attachment://perfil_clan.png")
                    embed.add_field(name="🔢 Roblox ID", value=f"`{user_data.get('roblox_user_id')}`", inline=False)
                    
                    if user_data.get('verified_at'):
                        verified_timestamp = int(datetime.fromisoformat(user_data['verified_at']).timestamp())
                        embed.add_field(name="📅 Vinculado", value=f"<t:{verified_timestamp}:R>", inline=False)
                    
                    embed.set_footer(text="Usa -mi-roblox-custom para personalizar tu perfil")
                    
                    # Crear vista con botones de añadir amigo e ir al perfil
                    view = AñadirAmigoView(ctx.author.id, user_data.get('roblox_username'), 
                                          user_data.get('roblox_user_id'), self)
                    
                    await ctx.send(embed=embed, file=file, view=view)
                
                except Exception as e:
                    # Si falla la imagen, mostrar embed normal
                    embed = discord.Embed(title="🎮 Tu Vinculación al Clan", color=discord.Color.blue())
                    embed.add_field(name="🎮 Roblox", value=f"**{user_data.get('roblox_username')}**", inline=True)
                    embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
                    embed.add_field(name="✅ Estado", value="Vinculado al Clan" if user_data.get('verified') else "Pendiente", inline=False)
                    await ctx.send(embed=embed)
            
            except:
                embed = discord.Embed(title="❌ Error", description="No pude generar tu perfil", color=discord.Color.red())
                await ctx.send(embed=embed)
    
    @commands.command(name="mi-roblox-custom")
    async def customize_profile(self, ctx):
        """🎨 Personalizar tu perfil en el clan"""
        
        user_key = str(ctx.author.id)
        if user_key not in self.cache:
            embed = discord.Embed(
                title="❌ No Vinculado",
                description="Debes vincular tu cuenta primero con `-clan-panel`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎨 Personalizar Tu Perfil",
            description="Personaliza tu descripción y colores en el panel",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Descripción", value="Texto personal que aparecerá en tu perfil (máx 200 caracteres)", inline=False)
        embed.add_field(name="🎨 Color Principal", value="Código HEX sin # (ej: FF1493)", inline=True)
        embed.add_field(name="🎨 Color Secundario", value="Código HEX sin # (ej: 00BFFF)", inline=True)
        embed.set_footer(text="Haz clic en el botón para abrir el formulario de personalización")
        
        view = PersonalizarPerfilView(self)
        await ctx.send(embed=embed, view=view, ephemeral=True)
    
    @commands.command(name="mis-amigos")
    async def my_friends(self, ctx):
        """👥 Ver solicitudes de amistad pendientes"""
        
        user_id = ctx.author.id
        friend_requests = self.cache.get("friend_requests", {})
        
        # Solicitudes recibidas
        received = [req for req in friend_requests.values() if req.get("to_id") == user_id]
        
        # Solicitudes enviadas
        sent = [req for req in friend_requests.values() if req.get("from_id") == user_id]
        
        embed = discord.Embed(
            title="👥 Mis Solicitudes de Amistad",
            color=discord.Color.blue()
        )
        
        if received:
            recibidas_text = "\n".join([f"• **{req['from_name']}** - <t:{int(datetime.fromisoformat(req['sent_at']).timestamp())}:R>" 
                                       for req in received[:5]])
            embed.add_field(name="📬 Recibidas", value=recibidas_text, inline=False)
        else:
            embed.add_field(name="📬 Recibidas", value="Sin solicitudes", inline=False)
        
        if sent:
            enviadas_text = "\n".join([f"• **{req['to_name']}** - <t:{int(datetime.fromisoformat(req['sent_at']).timestamp())}:R>" 
                                      for req in sent[:5]])
            embed.add_field(name="📤 Enviadas", value=enviadas_text, inline=False)
        else:
            embed.add_field(name="📤 Enviadas", value="Sin solicitudes", inline=False)
        
        embed.set_footer(text="Las solicitudes se guardan automáticamente")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.command(name="amigos-limpiar")
    async def clear_friends(self, ctx):
        """🗑️ Limpiar solicitudes de amistad expiradas (>30 días)"""
        
        friend_requests = self.cache.get("friend_requests", {})
        now = datetime.now()
        
        to_delete = []
        for key, req in friend_requests.items():
            sent_at = datetime.fromisoformat(req['sent_at'])
            if (now - sent_at).days > 30:
                to_delete.append(key)
        
        for key in to_delete:
            del friend_requests[key]
        
        self.cache["friend_requests"] = friend_requests
        save_cache(self.cache)
        
        embed = discord.Embed(
            title="✅ Limpieza Completada",
            description=f"Se eliminaron {len(to_delete)} solicitudes expiradas",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.command(name="clan-stats", aliases=["roblox-stats"])
    async def roblox_stats(self, ctx):
        """📊 Estadísticas de miembros del clan"""
        
        guild_id = ctx.guild.id
        guild_users = [u for u in self.cache.values() if u.get('guild_id') == guild_id]
        verified_count = sum(1 for u in guild_users if u.get('verified'))
        
        embed = discord.Embed(
            title="📊 Estadísticas del Clan",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 Vinculados",
            value=f"`{verified_count}`",
            inline=True
        )
        
        embed.add_field(
            name="👥 Servidor",
            value=f"`{ctx.guild.member_count}`",
            inline=True
        )
        
        if ctx.guild.member_count > 0:
            percentage = (verified_count / ctx.guild.member_count) * 100
            embed.add_field(
                name="📈 Porcentaje",
                value=f"`{percentage:.1f}%`",
                inline=True
            )
        
        # Últimos verificados
        if guild_users:
            recent = sorted(
                [u for u in guild_users if u.get('verified_at')],
                key=lambda x: x.get('verified_at', ''),
                reverse=True
            )[:5]
            
            if recent:
                recent_list = "\n".join([f"• **{u['roblox_username']}**" for u in recent])
                embed.add_field(
                    name="🔥 Últimos Vinculados",
                    value=recent_list,
                    inline=False
                )
        
        embed.set_footer(text="📊 Estadísticas en Vivo")
        
        await ctx.send(embed=embed, ephemeral=True)

# ════════════════════════════════════════════════════════════════
# 📝 SECCIÓN EDITABLE - PERSONALIZA AQUÍ
# ════════════════════════════════════════════════════════════════

# 🎨 COLORES DEL PANEL (RGB)
# Edita aquí los colores que desees:
# PANEL_COLORS = {
#     "bg_primary": (15, 15, 35),      # Fondo oscuro
#     "bg_secondary": (40, 30, 80),    # Fondo secundario
#     "accent_1": (120, 200, 255),     # Azul claro (cyan)
#     "accent_2": (200, 100, 255),     # Morado claro
#     "text_white": (255, 255, 255),   # Texto blanco
#     "text_gray": (150, 180, 220),    # Texto gris
#     "success": (100, 255, 150),      # Verde éxito
#     "warning": (255, 200, 80),       # Naranja advertencia
# }

# 📏 TAMAÑOS DE FUENTES
# Edita aquí los tamaños:
# PANEL_SIZES = {
#     "width": 1200,        # Ancho de imagen
#     "height": 700,        # Alto de imagen
#     "title_font": 80,     # Tamaño título principal
#     "subtitle_font": 35,  # Tamaño subtítulo
#     "text_font": 28,      # Tamaño texto general
#     "button_font": 22,    # Tamaño botones
# }

# 📝 TEXTOS DEL PANEL
# Edita aquí los textos que aparecen en la imagen:
PANEL_TEXTS = {
    "title": "🎮 ROBLOX",
    "subtitle": "Verificación de Cuenta",
    "group_section": "📍 Grupo Roblox",
    "group_id_prefix": "ID: ",
    "steps_header": "📋 Pasos para verificar:",
    "step_1": "1️⃣  Abre el enlace del grupo (botón verde)",
    "step_2": "2️⃣  Haz clic en 'Unirse al Grupo'",
    "step_3": "3️⃣  Regresa y presiona '✅ Ya me uní'",
    "step_4": "4️⃣  Recibe tu rol automáticamente",
}

# 📍 POSICIONES DE TEXTO (X, Y)
# Edita aquí las posiciones para mover el texto:
PANEL_POSITIONS = {
    "banner_title": (60, 15),           # Posición del título "ROBLOX"
    "banner_subtitle": (60, 60),        # Posición del subtítulo "Verificación de Cuenta"
    "group_section": (60, 0),           # Posición relativa al content_y para "Grupo Roblox"
    "group_id": (80, 35),               # Posición relativa al group_section para el ID
    "steps_header": (60, 0),            # Posición relativa para "Pasos para verificar"
    "steps_offset": (80, 0),            # Offset X para cada paso y offset Y entre pasos
    "footer_text": (60, 10),            # Posición del footer
    "banner_y": 40,                     # Altura del banner desde arriba
    "banner_h": 120,                    # Altura del banner
    "content_offset": 40,               # Espacio después del banner
    "group_content_gap": 90,            # Espacio entre grupo y pasos
    "steps_gap": 30,                    # Espacio entre pasos
}

# 🔧 CONFIGURACIÓN AVANZADA
# - Modificar create_roblox_verification_panel() para cambiar el diseño visual
# - Modificar verify_roblox_user() para cambiar la lógica de verificación
# - Modificar confirm_verification() para cambiar la asignación de rol
# - Agregar nuevos comandos en la clase Roblox extendiendo la clase
# - Cambiar animaciones, efectos o estilos de embeds en los comandos

# 💡 EJEMPLOS DE USO:
# 1. Cambiar colores: Edita PANEL_COLORS arriba
# 2. Cambiar tamaños: Edita PANEL_SIZES arriba
# 3. Cambiar textos: Edita PANEL_TEXTS arriba
# 4. Agregar más pasos: Agrega en PANEL_TEXTS y en create_roblox_verification_panel()
# 5. Personalizar embeds: Busca discord.Embed en los comandos y modifica
