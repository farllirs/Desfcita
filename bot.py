import discord
from discord.ext import commands, tasks
from discord import ui
import json
import os
from datetime import datetime, timedelta
import pytz
import asyncio
import sys
import time
import random
import traceback
import importlib
import inspect
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
keep_alive()

# ══════════════════════════════════════════════════════════════════════════════
# 🔇 SILENCIAR LOGS DE DISCORD.PY
# ══════════════════════════════════════════════════════════════════════════════
logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('discord.http').setLevel(logging.CRITICAL)
logging.getLogger('discord.gateway').setLevel(logging.CRITICAL)
logging.getLogger('discord.client').setLevel(logging.CRITICAL)
logging.getLogger('discord.ext').setLevel(logging.CRITICAL)

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 CONFIGURACIÓN PERSONALIZABLE - EDITA AQUÍ TUS PREFERENCIAS
# ══════════════════════════════════════════════════════════════════════════════

class BotConfig:
    TOKEN = os.getenv('DISCORD_TOKEN', '')  # Cargar desde .env o variable de entorno
    PREFIX = '-'
    OWNER_IDS = []
    MEMBER_ROLE_ID = 1461863342573621379
    
    BOT_NAME = "DESFCITA"
    BOT_DESCRIPTION = "Sistema de Gestión Premium"
    BOT_VERSION = "v2.1.0"
    BOT_EMOJI = "🌸"
    
    STATUS_TYPE = discord.ActivityType.playing
    STATUS_TEXT = "✨ -help | 🌸 Premium"
    STATUS_ROTATION = [
        (discord.ActivityType.playing, "✨ -help | Sistema Premium"),
        (discord.ActivityType.watching, "🌸 {servers} servidores"),
        (discord.ActivityType.listening, "💖 {users} usuarios"),
    ]
    STATUS_INTERVAL = 60
    
    MODULES_FOLDER = 'módulos'
    DATA_FOLDER = 'data'
    AUTO_RELOAD = True
    DEBUG_MODE = False
    
    # 🖼️ Banner de Carga
    BANNER_TITLE = "D E S F C I T A  •  B O T  S Y S T E M"
    BANNER_SUBTITLE = "Premium Management System"
    LOADING_MESSAGES = [
        ("🔮 Despertando conciencia artificial...", "pink"),
        ("🎀 Ajustando lazos de belleza...", "violet"),
        ("⭐ Sincronizando con el servidor estelar...", "cyan"),
        ("✨ Preparando interfaz divina...", "yellow"),
        ("🌸 Verificando módulos de amor...", "pink"),
        ("💎 Optimizando rendimiento premium...", "green"),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# 🌈 PALETA DE COLORES Y ESTÉTICA
# ══════════════════════════════════════════════════════════════════════════════

class Colors:
    # Colores principales
    PINK = 0xFFB6C1
    ROSE = 0xFF69B4
    LAVENDER = 0xE6E6FA
    PEACH = 0xFFDAB9
    MINT = 0x98FB98
    SKY = 0x87CEEB
    CORAL = 0xF08080
    GOLD = 0xFFD700
    LILAC = 0xDDA0DD
    CREAM = 0xFFFDD0
    WHITE = 0xFFFFFF
    SOFT_RED = 0xFF5C5C
    SOFT_GREEN = 0x5CFF9D
    PURPLE = 0x9B59B6
    CYAN = 0x1ABC9C
    
    # Colores de terminal (ANSI)
    class Terminal:
        PINK = "\033[38;5;213m"
        PINK_LIGHT = "\033[38;5;219m"
        VIOLET = "\033[38;5;141m"
        VIOLET_LIGHT = "\033[38;5;147m"
        CYAN = "\033[38;5;123m"
        GREEN = "\033[38;5;120m"
        WHITE = "\033[38;5;255m"
        YELLOW = "\033[38;5;228m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

class Icons:
    TICKET = "🎫"
    SHIELD = "🛡️"
    HEART = "🌸"
    STAR = "✨"
    WARN = "⚠️"
    SUCCESS = "✅"
    ERROR = "❌"
    MOD = "🔨"
    TIME = "⏰"
    USER = "👤"
    MAIL = "📩"
    LOCK = "🔒"
    TRASH = "🗑️"
    INFO = "ℹ️"
    RIGHT = "➔"
    DOT = "•"
    ARROW = "→"
    REFRESH = "🔄"
    ROCKET = "🚀"
    CROWN = "👑"
    TOOLS = "🛠️"
    CHART = "📊"
    FIRE = "🔥"
    SPARKLES = "✨"

# ══════════════════════════════════════════════════════════════════════════════
# 🌎 CONFIGURACIÓN DE PAÍSES LATAM
# ══════════════════════════════════════════════════════════════════════════════

PAISES_LATAM = {
    "argentina": {"bandera": "🇦🇷", "nombre": "Argentina", "color": 0x75AADB, "zona": "America/Argentina/Buenos_Aires"},
    "bolivia": {"bandera": "🇧🇴", "nombre": "Bolivia", "color": 0xD52B1E, "zona": "America/La_Paz"},
    "brasil": {"bandera": "🇧🇷", "nombre": "Brasil", "color": 0x009739, "zona": "America/Sao_Paulo"},
    "chile": {"bandera": "🇨🇱", "nombre": "Chile", "color": 0xD52B1E, "zona": "America/Santiago"},
    "colombia": {"bandera": "🇨🇴", "nombre": "Colombia", "color": 0xFCD116, "zona": "America/Bogota"},
    "costarica": {"bandera": "🇨🇷", "nombre": "Costa Rica", "color": 0x002B7F, "zona": "America/Costa_Rica"},
    "cuba": {"bandera": "🇨🇺", "nombre": "Cuba", "color": 0x002A8F, "zona": "America/Havana"},
    "ecuador": {"bandera": "🇪🇨", "nombre": "Ecuador", "color": 0xFFD100, "zona": "America/Guayaquil"},
    "elsalvador": {"bandera": "🇸🇻", "nombre": "El Salvador", "color": 0x0F47AF, "zona": "America/El_Salvador"},
    "guatemala": {"bandera": "🇬🇹", "nombre": "Guatemala", "color": 0x4997D0, "zona": "America/Guatemala"},
    "honduras": {"bandera": "🇭🇳", "nombre": "Honduras", "color": 0x0073CF, "zona": "America/Tegucigalpa"},
    "mexico": {"bandera": "🇲🇽", "nombre": "Mexico", "color": 0x006341, "zona": "America/Mexico_City"},
    "nicaragua": {"bandera": "🇳🇮", "nombre": "Nicaragua", "color": 0x0067C6, "zona": "America/Managua"},
    "panama": {"bandera": "🇵🇦", "nombre": "Panama", "color": 0xDA121A, "zona": "America/Panama"},
    "paraguay": {"bandera": "🇵🇾", "nombre": "Paraguay", "color": 0xDA121A, "zona": "America/Asuncion"},
    "peru": {"bandera": "🇵🇪", "nombre": "Peru", "color": 0xD91023, "zona": "America/Lima"},
    "dominicanrep": {"bandera": "🇩🇴", "nombre": "Rep. Dominicana", "color": 0x002D62, "zona": "America/Santo_Domingo"},
    "uruguay": {"bandera": "🇺🇾", "nombre": "Uruguay", "color": 0x0038A8, "zona": "America/Montevideo"},
    "venezuela": {"bandera": "🇻🇪", "nombre": "Venezuela", "color": 0xFFCC00, "zona": "America/Caracas"},
    "puertorico": {"bandera": "🇵🇷", "nombre": "Puerto Rico", "color": 0x0050EF, "zona": "America/Puerto_Rico"},
    "espana": {"bandera": "🇪🇸", "nombre": "España", "color": 0xAA151B, "zona": "Europe/Madrid"},
    "usa": {"bandera": "🇺🇸", "nombre": "Estados Unidos", "color": 0x3C3B6E, "zona": "America/New_York"},
}

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️ INICIALIZACIÓN DEL BOT
# ══════════════════════════════════════════════════════════════════════════════

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=BotConfig.PREFIX, intents=intents, help_command=None)

# Inyectar configuraciones en el bot
bot.Colors = Colors
bot.Icons = Icons
bot.PAISES_LATAM = PAISES_LATAM
bot.BotConfig = BotConfig

# ═══════════════════════════════════════════════════════════════════════════════
# 🎭 ROTACIÓN DE STATUS EN CALIENTE
# ═══════════════════════════════════════════════════════════════════════════════

@tasks.loop(seconds=BotConfig.STATUS_INTERVAL)
async def status_rotator():
    """Rotar status automáticamente"""
    if not hasattr(BotConfig, 'STATUS_ROTATION') or not BotConfig.STATUS_ROTATION:
        return
    
    try:
        activity_type, status_text = random.choice(BotConfig.STATUS_ROTATION)
        
        # Reemplazar variables
        status_text = status_text.format(
            servers=len(bot.guilds),
            users=sum(g.member_count or 0 for g in bot.guilds)
        )
        
        await bot.change_presence(
            activity=discord.Activity(
                type=activity_type,
                name=status_text
            ),
            status=discord.Status.online
        )
    except Exception as e:
        if BotConfig.DEBUG_MODE:
            print(f"Error en rotación de status: {e}")

bot.status_rotator = status_rotator

# ══════════════════════════════════════════════════════════════════════════════
# 📁 SISTEMA DE ARCHIVOS Y DATOS
# ══════════════════════════════════════════════════════════════════════════════

CONFIG_FILE = 'data/config.json'
WARNS_FILE = 'data/warns.json'
TICKETS_FILE = 'data/tickets.json'
LOGS_FILE = 'data/logs.json'
ANONYMOUS_STORIES_FILE = 'data/anonymous_stories.json'

if not os.path.exists('data'):
    os.makedirs('data')

def load_config():
    default_config = {
        "welcome_channel": None,
        "leave_channel": None,
        "admin_roles": [],
        "mod_roles": [],
        "pais_channel": None,
        "pais_message": None,
        "announcement_channel": None,
        "country_roles": {},
        "story_public_channel": None,
        "story_log_channel": None
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            for key, value in default_config.items():
                if key not in loaded:
                    loaded[key] = value
            return loaded
    return default_config

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(warns, f, indent=4, ensure_ascii=False)

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tickets(data):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_logs(data):
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_stories():
    if os.path.exists(ANONYMOUS_STORIES_FILE):
        with open(ANONYMOUS_STORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_stories(data):
    with open(ANONYMOUS_STORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_action(action, user_id, guild_id, details=""):
    logs = load_logs()
    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "user_id": user_id,
        "guild_id": guild_id,
        "details": details
    })
    save_logs(logs)

# Configuración inicial del bot
bot.config = load_config()
bot.save_config = save_config
bot.log_action = log_action
warns_data = load_warns()
tickets_data = load_tickets()
stories_data = load_stories()

# ══════════════════════════════════════════════════════════════════════════════
# 🔐 SISTEMA DE PERMISOS
# ══════════════════════════════════════════════════════════════════════════════

def is_admin_or_mod():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator:
            return True
        admin_roles = bot.config.get("admin_roles", [])
        mod_roles = bot.config.get("mod_roles", [])
        return any(role.id in admin_roles or role.id in mod_roles for role in ctx.author.roles)
    return commands.check(predicate)

def is_admin_only():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator:
            return True
        admin_roles = bot.config.get("admin_roles", [])
        return any(role.id in admin_roles for role in ctx.author.roles)
    return commands.check(predicate)

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 SISTEMA DE REFRIGERACIÓN DE MÓDULOS MEJORADO
# ══════════════════════════════════════════════════════════════════════════════

class ModuloRefrigeracionView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Refrigerar Todos los Módulos", emoji="❄️", style=discord.ButtonStyle.primary, custom_id="refrigerar_modulos_btn")
    async def refrigerar(self, interaction: discord.Interaction, button: ui.Button):
        # Verificar permisos
        if not await self.bot.is_owner(interaction.user):
            admin_roles = self.bot.config.get("admin_roles", [])
            if not any(role.id in admin_roles for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
                error_embed = discord.Embed(
                    title=f"{Icons.ERROR} Acceso Denegado",
                    description="No tienes permisos para usar esta función.",
                    color=Colors.SOFT_RED
                )
                return await interaction.response.send_message(embed=error_embed, ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        folder = 'módulos' if os.path.exists('módulos') else 'modulos'
        if not os.path.exists(folder):
            error_embed = discord.Embed(
                title=f"{Icons.ERROR} Error de Sistema",
                description="No se encontró la carpeta de módulos.",
                color=Colors.SOFT_RED
            )
            return await interaction.followup.send(embed=error_embed, ephemeral=True)

        # Proceso de refrigeración
        success_modules = []
        failed_modules = []
        loaded_modules = []
        
        for filename in os.listdir(folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                ext = f'{folder}.{filename[:-3]}'
                try:
                    await self.bot.reload_extension(ext)
                    success_modules.append(filename[:-3])
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(ext)
                        loaded_modules.append(filename[:-3])
                    except Exception as e:
                        failed_modules.append((filename[:-3], str(e)))
                except Exception as e:
                    failed_modules.append((filename[:-3], str(e)))

        # Crear embed de resultado
        embed = discord.Embed(
            title=f"❄️ Sistema de Refrigeración Completado",
            description="**Resumen de la operación:**",
            color=Colors.CYAN,
            timestamp=datetime.now()
        )
        
        if success_modules:
            embed.add_field(
                name=f"{Icons.SUCCESS} Módulos Recargados ({len(success_modules)})",
                value="```\n" + "\n".join([f"✓ {m}" for m in success_modules]) + "```",
                inline=False
            )
        
        if loaded_modules:
            embed.add_field(
                name=f"{Icons.SPARKLES} Módulos Cargados ({len(loaded_modules)})",
                value="```\n" + "\n".join([f"+ {m}" for m in loaded_modules]) + "```",
                inline=False
            )
        
        if failed_modules:
            embed.add_field(
                name=f"{Icons.ERROR} Módulos con Error ({len(failed_modules)})",
                value="```\n" + "\n".join([f"✗ {m}: {e[:50]}..." for m, e in failed_modules]) + "```",
                inline=False
            )
        
        total = len(success_modules) + len(loaded_modules) + len(failed_modules)
        success_rate = ((len(success_modules) + len(loaded_modules)) / total * 100) if total > 0 else 0
        
        embed.add_field(
            name=f"{Icons.CHART} Estadísticas",
            value=f"```\nTotal: {total}\nÉxito: {success_rate:.1f}%\nTiempo: {datetime.now().strftime('%H:%M:%S')}```",
            inline=False
        )
        
        embed.set_footer(
            text=f"{BotConfig.BOT_EMOJI} Sistema de Refrigeración • {BotConfig.BOT_NAME}",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.command(name="panel-modulos", aliases=["panel-m", "modulos"])
@is_admin_only()
async def panel_modulos(ctx):
    """Panel de control de módulos mejorado"""
    
    # Contar módulos
    folder = 'módulos' if os.path.exists('módulos') else 'modulos'
    total_modules = 0
    if os.path.exists(folder):
        total_modules = len([f for f in os.listdir(folder) if f.endswith('.py') and not f.startswith('__')])
    
    embed = discord.Embed(
        title=f"🎛️ Panel de Control de Módulos",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**{Icons.TOOLS} Sistema de Gestión Avanzada**\n\n"
            f"Este panel te permite gestionar y refrescar todos los módulos del bot "
            f"para asegurar un funcionamiento óptimo y aplicar cambios recientes.\n\n"
            f"{Icons.INFO} **Módulos Detectados:** `{total_modules}`\n"
            f"{Icons.ROCKET} **Estado:** `Operativo`\n"
            f"{Icons.SPARKLES} **Versión:** `{BotConfig.BOT_VERSION}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Instrucciones:**\n"
            f"{Icons.DOT} Presiona el botón para refrigerar todos los módulos\n"
            f"{Icons.DOT} Usa `-modulo rest <nombre>` para recargar uno específico\n"
            f"{Icons.DOT} Revisa el estado de cada módulo después de la refrigeración"
        ),
        color=Colors.PURPLE,
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(
        text=f"{BotConfig.BOT_EMOJI} Sistema de Mantenimiento • {BotConfig.BOT_NAME}",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    
    await ctx.send(embed=embed, view=ModuloRefrigeracionView(bot))

@bot.command(name="modulo", aliases=["mod"])
@is_admin_only()
async def modulo_cmd(ctx, action: str = None, module_name: str = None):
    """Gestiona módulos individuales"""
    
    if not action or not module_name:
        embed = discord.Embed(
            title=f"{Icons.INFO} Gestión de Módulos Individual",
            description=(
                f"**Uso correcto:**\n"
                f"```\n{BotConfig.PREFIX}modulo rest <nombre>\n```\n"
                f"**Ejemplos:**\n"
                f"{Icons.DOT} `-modulo rest confesiones`\n"
                f"{Icons.DOT} `-modulo rest tickets`\n"
                f"{Icons.DOT} `-modulo rest paises`\n\n"
                f"**O usa:**\n"
                f"`{BotConfig.PREFIX}panel-modulos` para el panel completo"
            ),
            color=Colors.PINK
        )
        return await ctx.send(embed=embed)

    folder = 'módulos' if os.path.exists('módulos') else 'modulos'
    full_module_path = f"{folder}.{module_name}"
    
    if action.lower() in ["rest", "reload", "recargar", "r"]:
        loading_embed = discord.Embed(
            description=f"{Icons.REFRESH} Procesando módulo `{module_name}`...",
            color=Colors.CYAN
        )
        msg = await ctx.send(embed=loading_embed)
        
        try:
            await bot.reload_extension(full_module_path)
            final_embed = discord.Embed(
                title=f"{Icons.SUCCESS} Módulo Recargado",
                description=f"El módulo **{module_name}** ha sido recargado exitosamente.",
                color=Colors.SOFT_GREEN,
                timestamp=datetime.now()
            )
        except commands.ExtensionNotLoaded:
            try:
                await bot.load_extension(full_module_path)
                final_embed = discord.Embed(
                    title=f"{Icons.SPARKLES} Módulo Cargado",
                    description=f"El módulo **{module_name}** ha sido cargado por primera vez.",
                    color=Colors.SOFT_GREEN,
                    timestamp=datetime.now()
                )
            except Exception as e:
                final_embed = discord.Embed(
                    title=f"{Icons.ERROR} Error al Cargar",
                    description=f"**Módulo:** `{module_name}`\n**Error:**\n```py\n{str(e)[:500]}\n```",
                    color=Colors.SOFT_RED,
                    timestamp=datetime.now()
                )
        except Exception as e:
            final_embed = discord.Embed(
                title=f"{Icons.ERROR} Error al Recargar",
                description=f"**Módulo:** `{module_name}`\n**Error:**\n```py\n{str(e)[:500]}\n```",
                color=Colors.SOFT_RED,
                timestamp=datetime.now()
            )
        
        final_embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await msg.edit(embed=final_embed)

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 SISTEMA DE CARGA ULTRA-PREMIUM CON BANNER
# ══════════════════════════════════════════════════════════════════════════════

def clear_console():
    """Limpia la consola"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    """Imprime el banner principal del bot"""
    clear_console()
    
    T = Colors.Terminal
    
    # Banner artístico mejorado
    banner_lines = [
        f"{T.PINK}{T.BOLD}╔═══════════════════════════════════════════════════════════╗{T.RESET}",
        f"{T.PINK}║                                                           ║{T.RESET}",
        f"{T.PINK}║     {T.WHITE}{T.BOLD}✨ {BotConfig.BANNER_TITLE} ✨{T.RESET}{T.PINK}      ║{T.RESET}",
        f"{T.PINK}║                                                           ║{T.RESET}",
        f"{T.PINK}║     {T.VIOLET}{BotConfig.BANNER_SUBTITLE.center(47)}{T.RESET}{T.PINK}     ║{T.RESET}",
        f"{T.PINK}║                                                           ║{T.RESET}",
        f"{T.PINK}╚═══════════════════════════════════════════════════════════╝{T.RESET}",
        f"",
        f"{T.CYAN}  {Icons.ROCKET} Versión: {T.WHITE}{BotConfig.BOT_VERSION}{T.RESET}",
        f"{T.CYAN}  {Icons.CROWN} Desarrollado con {T.PINK}❤{T.RESET}{T.CYAN}  por el equipo de {T.WHITE}{BotConfig.BOT_NAME}{T.RESET}",
        f""
    ]
    
    for line in banner_lines:
        print(line)
        time.sleep(0.05)

def loading_animation():
    """Animación de carga premium"""
    T = Colors.Terminal
    
    print(f"{T.PINK}{T.BOLD}  ┌─────────────────────────────────────────────────────┐{T.RESET}")
    print(f"{T.PINK}  │ {T.WHITE}          🌸 INICIANDO SISTEMA PREMIUM 🌸{T.RESET}{T.PINK}          │{T.RESET}")
    print(f"{T.PINK}  └─────────────────────────────────────────────────────┘{T.RESET}\n")
    
    # Tareas de carga
    color_map = {
        "pink": T.PINK,
        "violet": T.VIOLET,
        "cyan": T.CYAN,
        "yellow": T.YELLOW,
        "green": T.GREEN
    }
    
    for task_text, color_name in BotConfig.LOADING_MESSAGES:
        color = color_map.get(color_name, T.WHITE)
        sys.stdout.write(f"  {color}➤ {T.WHITE}{task_text}{T.RESET}")
        sys.stdout.flush()
        
        # Animación de puntos
        for _ in range(3):
            time.sleep(0.15)
            sys.stdout.write(f"{color}.{T.RESET}")
            sys.stdout.flush()
        
        print(f" {T.GREEN}✔{T.RESET}")
        time.sleep(0.1)
    
    # Barra de progreso premium
    print(f"\n{T.CYAN}{T.BOLD}  ⚡ CARGANDO NÚCLEO DEL SISTEMA{T.RESET}\n")
    
    bar_length = 45
    emojis = ["☁️", "⭐", "🌙", "🌸", "✨", "💖"]
    
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        
        # Colores del gradiente
        if i < bar_length // 3:
            bar_color = T.PINK
        elif i < (bar_length * 2) // 3:
            bar_color = T.VIOLET
        else:
            bar_color = T.GREEN
        
        filled = "█" * i
        empty = "░" * (bar_length - i)
        
        # Emoji rotativo
        current_emoji = emojis[min(i // (bar_length // 5), len(emojis) - 1)]
        
        # Barra de progreso
        sys.stdout.write(
            f"\r  {T.PINK}▐{bar_color}{filled}{T.WHITE}{empty}{T.PINK}▌ "
            f"{T.CYAN if percent % 2 == 0 else T.WHITE}{percent:3d}% {current_emoji}{T.RESET}"
        )
        sys.stdout.flush()
        
        # Velocidad variable
        if percent > 80:
            time.sleep(0.12)
        elif percent > 40:
            time.sleep(0.03)
        else:
            time.sleep(0.05)
    
    print(f"\n\n{T.GREEN}{T.BOLD}  ✔ ¡SISTEMA INICIADO CORRECTAMENTE! {BotConfig.BOT_EMOJI}{T.RESET}")
    time.sleep(1)
    clear_console()

def aesthetic_loading():
    """Proceso completo de carga estética"""
    print_banner()
    time.sleep(0.5)
    loading_animation()

# ══════════════════════════════════════════════════════════════════════════════
# 🎮 EVENTOS DEL BOT
# ══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    """Evento cuando el bot está listo"""
    T = Colors.Terminal
    
    # Banner de confirmación
    print(f"\n{T.PINK}╔═══════════════════════════════════════════════════════════╗{T.RESET}")
    print(f"{T.PINK}║  {T.GREEN}{T.BOLD}✔ BOT ONLINE Y OPERATIVO{T.RESET}{T.PINK}                                ║{T.RESET}")
    print(f"{T.PINK}╠═══════════════════════════════════════════════════════════╣{T.RESET}")
    print(f"{T.PINK}║  {T.WHITE}Usuario:{T.RESET}  {T.CYAN}{str(bot.user).ljust(45)}{T.RESET}{T.PINK}║{T.RESET}")
    print(f"{T.PINK}║  {T.WHITE}ID:{T.RESET}       {T.VIOLET}{str(bot.user.id).ljust(45)}{T.RESET}{T.PINK}║{T.RESET}")
    print(f"{T.PINK}║  {T.WHITE}Servers:{T.RESET}  {T.YELLOW}{str(len(bot.guilds)).ljust(45)}{T.RESET}{T.PINK}║{T.RESET}")
    print(f"{T.PINK}║  {T.WHITE}Latencia:{T.RESET} {T.GREEN}{f'{round(bot.latency * 1000)}ms'.ljust(45)}{T.RESET}{T.PINK}║{T.RESET}")
    print(f"{T.PINK}╚═══════════════════════════════════════════════════════════╝{T.RESET}\n")
    
    # Configurar presencia y iniciar rotación de status
    await bot.change_presence(
        activity=discord.Activity(
            type=BotConfig.STATUS_TYPE,
            name=BotConfig.STATUS_TEXT
        ),
        status=discord.Status.online
    )
    
    # Iniciar rotación de status si está habilitada
    if hasattr(BotConfig, 'STATUS_ROTATION') and BotConfig.STATUS_ROTATION:
        bot.status_rotator.start()
    
    # Registrar vistas persistentes
    print(f"{T.VIOLET}  {Icons.REFRESH} Registrando vistas persistentes...{T.RESET}")
    
    # Vista de módulos
    bot.add_view(ModuloRefrigeracionView(bot))
    print(f"{T.GREEN}    ✓ ModuloRefrigeracionView{T.RESET}")
    
    # Vistas de módulos externos
    try:
        from módulos.tickets import TicketView, TicketControlView
        bot.add_view(TicketView(bot))
        bot.add_view(TicketControlView(bot))
        print(f"{T.GREEN}    ✓ TicketView & TicketControlView{T.RESET}")
    except Exception as e:
        print(f"{T.YELLOW}    ⚠ Tickets: {str(e)[:30]}...{T.RESET}")
    
    try:
        from módulos.confesiones import ConfesionPanelView, ConfesionModerateView
        bot.add_view(ConfesionPanelView(bot))
        bot.add_view(ConfesionModerateView(bot=bot))
        print(f"{T.GREEN}    ✓ ConfesionPanelView & ConfesionModerateView{T.RESET}")
    except Exception as e:
        print(f"{T.YELLOW}    ⚠ Confesiones: {str(e)[:30]}...{T.RESET}")
    
    try:
        folder = 'módulos' if os.path.exists('módulos') else 'modulos'
        if os.path.exists(f'{folder}/paises.py'):
            paises_module = __import__(f'{folder}.paises', fromlist=['PaisView'])
            bot.add_view(paises_module.PaisView(bot))
            print(f"{T.GREEN}    ✓ PaisView{T.RESET}")
    except Exception as e:
        print(f"{T.YELLOW}    ⚠ Paises: {str(e)[:30]}...{T.RESET}")
    
    print(f"\n{T.GREEN}{T.BOLD}  {Icons.SPARKLES} ¡Todo listo! El bot está funcionando perfectamente. {Icons.SPARKLES}{T.RESET}\n")

@bot.event
async def on_command_error(ctx, error):
    """Manejo de errores de comandos"""
    
    if isinstance(error, commands.CommandNotFound):
        return  # Ignorar comandos no encontrados
    
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{Icons.ERROR} Permisos Insuficientes",
            description="No tienes los permisos necesarios para ejecutar este comando.",
            color=Colors.SOFT_RED
        )
        return await ctx.send(embed=embed, delete_after=10)
    
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=f"{Icons.WARN} Argumento Faltante",
            description=f"Te falta el argumento: `{error.param.name}`\nUsa: `{BotConfig.PREFIX}help {ctx.command.name}` para más información.",
            color=Colors.CORAL
        )
        return await ctx.send(embed=embed, delete_after=15)
    
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title=f"{Icons.LOCK} Acceso Denegado",
            description="No tienes permiso para usar este comando.",
            color=Colors.SOFT_RED
        )
        return await ctx.send(embed=embed, delete_after=10)
    
    # Error genérico
    embed = discord.Embed(
        title=f"{Icons.ERROR} Error al Ejecutar Comando",
        description=f"```py\n{str(error)[:500]}\n```",
        color=Colors.SOFT_RED
    )
    await ctx.send(embed=embed, delete_after=30)

# ══════════════════════════════════════════════════════════════════════════════
# 🔧 COMANDOS DE ADMINISTRACIÓN DE MÓDULOS
# ══════════════════════════════════════════════════════════════════════════════

@bot.command(name="reloadmodule", aliases=["reload-m", "rm", "recarga"])
@commands.is_owner()
async def reload_module_cmd(ctx, module_name: str = None):
    """Recargar un módulo en caliente (solo Owner)"""
    if not module_name:
        # Mostrar modules disponibles
        folder = BotConfig.MODULES_FOLDER
        available = sorted([f[:-3] for f in os.listdir(folder) if f.endswith('.py') and not f.startswith('_')])
        
        modules_text = "\n".join([f"  🟢 {m}" for m in available])
        
        embed = discord.Embed(
            title="🔄 Recargador de Módulos",
            description=f"Uso: `-reloadmodule <nombre>`\n\n**Módulos disponibles:**\n```\n{modules_text}\n```",
            color=Colors.LAVENDER
        )
        return await ctx.send(embed=embed)
    
    async with ctx.typing():
        success, msg = await ctx.bot.module_manager.reload(module_name)
    
    embed = discord.Embed(
        title="🔄 Recarga de Módulo",
        description=msg,
        color=Colors.GREEN if success else Colors.SOFT_RED
    )
    embed.set_footer(text=f"Tiempo: {datetime.now().strftime('%H:%M:%S')}")
    await ctx.send(embed=embed)

@bot.command(name="modules", aliases=["mods", "listmodules"])
@commands.is_owner()
async def modules_info(ctx):
    """Ver información detallada de módulos cargados (solo Owner)"""
    info = ctx.bot.module_manager.get_info()
    
    embed = discord.Embed(
        title="📦 Estado del Sistema de Módulos",
        color=Colors.LAVENDER,
        description=f"Bot: **{BotConfig.BOT_NAME}** v{BotConfig.BOT_VERSION}"
    )
    
    # Estadísticas
    embed.add_field(
        name="📊 Estadísticas",
        value=(
            f"✅ Cargados: `{info['total_loaded']}`\n"
            f"❌ Errores: `{info['total_failed']}`\n"
            f"📈 Total: `{info['total_loaded'] + info['total_failed']}`"
        ),
        inline=False
    )
    
    # Módulos activos
    if info['modules']:
        modules_list = sorted(info['modules'].keys())
        modules_text = "\n".join([f"  🟢 `{name}`" for name in modules_list])
        
        embed.add_field(
            name=f"✅ Módulos Activos ({len(modules_list)})",
            value=modules_text,
            inline=False
        )
    
    # Errores
    if info['errors']:
        errors_text = "\n".join([
            f"  🔴 `{err['module']}` - {err['error'][:50]}" 
            for err in info['errors']
        ])
        embed.add_field(
            name=f"❌ Módulos con Error ({len(info['errors'])})",
            value=errors_text,
            inline=False
        )
    
    # Tip
    embed.add_field(
        name="💡 Tips",
        value=(
            "`-reloadmodule <nombre>` - Recargar un módulo\n"
            "`-reloadmodule` - Ver lista de módulos\n"
            "`-mods` - Ver este estado"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    await ctx.send(embed=embed)

# ══════════════════════════════════════════════════════════════════════════════
# 📚 COMANDO DE AYUDA PERSONALIZADO
# ══════════════════════════════════════════════════════════════════════════════

@bot.command(name="help", aliases=["ayuda", "h"])
async def help_command(ctx, *, comando: str = None):
    """Comando de ayuda mejorado"""
    
    if comando:
        # Ayuda de comando específico
        cmd = bot.get_command(comando)
        if not cmd:
            embed = discord.Embed(
                title=f"{Icons.ERROR} Comando No Encontrado",
                description=f"No existe el comando `{comando}`",
                color=Colors.SOFT_RED
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"{Icons.INFO} Ayuda: {cmd.name}",
            description=cmd.help or "Sin descripción disponible.",
            color=Colors.LAVENDER
        )
        
        if cmd.aliases:
            embed.add_field(
                name="Alias",
                value=", ".join([f"`{alias}`" for alias in cmd.aliases]),
                inline=False
            )
        
        embed.add_field(
            name="Uso",
            value=f"`{BotConfig.PREFIX}{cmd.name} {cmd.signature}`",
            inline=False
        )
        
        return await ctx.send(embed=embed)
    
    # Ayuda general
    embed = discord.Embed(
        title=f"{BotConfig.BOT_EMOJI} Centro de Ayuda - {BotConfig.BOT_NAME}",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Bienvenido al sistema de ayuda**\n\n"
            f"Usa `{BotConfig.PREFIX}help <comando>` para información detallada.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=Colors.PINK,
        timestamp=datetime.now()
    )
    
    # Comandos de administración
    admin_cmds = [
        f"`{BotConfig.PREFIX}panel-modulos` - Panel de gestión de módulos",
        f"`{BotConfig.PREFIX}modulo rest <nombre>` - Recargar módulo específico",
    ]
    
    embed.add_field(
        name=f"{Icons.CROWN} Administración",
        value="\n".join(admin_cmds),
        inline=False
    )
    
    # Comandos generales
    general_cmds = [
        f"`{BotConfig.PREFIX}help` - Muestra este mensaje",
        f"`{BotConfig.PREFIX}info` - Información del bot",
        f"`{BotConfig.PREFIX}ping` - Latencia del bot",
    ]
    
    embed.add_field(
        name=f"{Icons.STAR} General",
        value="\n".join(general_cmds),
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(
        text=f"{BotConfig.BOT_EMOJI} {BotConfig.BOT_NAME} {BotConfig.BOT_VERSION}",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="info", aliases=["botinfo", "información"])
async def info_command(ctx):
    """Información del bot"""
    
    # Calcular uptime
    uptime = datetime.now() - bot.start_time if hasattr(bot, 'start_time') else timedelta(0)
    
    embed = discord.Embed(
        title=f"{BotConfig.BOT_EMOJI} Información del Bot",
        description=f"━━━━━━━━━━━━━━━━━━━━━━",
        color=Colors.PURPLE,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=f"{Icons.ROBOT} Bot",
        value=f"```\n{bot.user.name}\n```",
        inline=True
    )
    
    embed.add_field(
        name=f"{Icons.CHART} Versión",
        value=f"```\n{BotConfig.BOT_VERSION}\n```",
        inline=True
    )
    
    embed.add_field(
        name=f"{Icons.TIME} Latencia",
        value=f"```\n{round(bot.latency * 1000)}ms\n```",
        inline=True
    )
    
    embed.add_field(
        name=f"{Icons.SHIELD} Servidores",
        value=f"```\n{len(bot.guilds)}\n```",
        inline=True
    )
    
    embed.add_field(
        name=f"{Icons.USER} Usuarios",
        value=f"```\n{sum(g.member_count for g in bot.guilds)}\n```",
        inline=True
    )
    
    embed.add_field(
        name=f"{Icons.FIRE} Uptime",
        value=f"```\n{str(uptime).split('.')[0]}\n```",
        inline=True
    )
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(
        text=f"Solicitado por {ctx.author.name}",
        icon_url=ctx.author.display_avatar.url
    )
    
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping_command(ctx):
    """Muestra la latencia del bot"""
    
    latency = round(bot.latency * 1000)
    
    if latency < 100:
        color = Colors.SOFT_GREEN
        status = "Excelente"
        emoji = Icons.SUCCESS
    elif latency < 200:
        color = Colors.GOLD
        status = "Buena"
        emoji = Icons.STAR
    else:
        color = Colors.CORAL
        status = "Alta"
        emoji = Icons.WARN
    
    embed = discord.Embed(
        title=f"{emoji} Pong!",
        description=f"**Latencia:** `{latency}ms`\n**Estado:** {status}",
        color=color
    )
    
    await ctx.send(embed=embed)

@bot.command(name="reloadmod")
async def reload_module(ctx, module_name: str = None):
    """Recargar módulo en caliente (solo dueño del bot)"""
    
    # Permitir si es owner del servidor o admin
    if not (ctx.guild.owner_id == ctx.author.id or ctx.author.guild_permissions.administrator):
        await ctx.send("❌ Solo el dueño del servidor o admin puede recargar módulos")
        return
    
    if not module_name:
        await ctx.send("❌ Uso: `-reloadmod <módulo>`")
        return
    
    async with ctx.typing():
        success, message = await bot.module_manager.reload(module_name)
        
        if success:
            embed = discord.Embed(
                title="✅ Recarga Exitosa",
                description=message,
                color=Colors.SOFT_GREEN
            )
        else:
            embed = discord.Embed(
                title="❌ Error en Recarga",
                description=message,
                color=Colors.SOFT_RED
            )
        
        embed.set_footer(text="Sistema de recarga de módulos")
        await ctx.send(embed=embed)

@bot.command(name="reloadall")
async def reload_all(ctx):
    """🔄 Recargar todos los módulos + utils"""
    
    # Permitir si es owner del servidor o admin
    if not (ctx.guild.owner_id == ctx.author.id or ctx.author.guild_permissions.administrator):
        await ctx.send("❌ Solo el dueño del servidor o admin puede recargar módulos")
        return
    
    async with ctx.typing():
        T = Colors.Terminal
        print(f"\n{T.PINK}🔄 RECARGANDO TODO (MÓDULOS + UTILS){T.RESET}\n")
        
        modules = sorted([f[:-3] for f in os.listdir(BotConfig.MODULES_FOLDER) 
                         if f.endswith('.py') and not f.startswith('_')])
        
        results = {"success": [], "failed": []}
        
        for module in modules:
            success, msg = await bot.module_manager.reload(module)
            if success:
                results["success"].append(module)
                print(f"  {T.GREEN}✓{T.RESET} {module}")
            else:
                results["failed"].append((module, msg))
                print(f"  {T.PINK}✗{T.RESET} {module}: {msg[:40]}")
        
        embed = discord.Embed(
            title="🔄 Recarga Masiva Completada",
            color=Colors.LAVENDER
        )
        
        embed.add_field(
            name="✅ Exitosos",
            value=f"`{len(results['success'])}/{len(modules)}`",
            inline=True
        )
        
        embed.add_field(
            name="❌ Errores",
            value=f"`{len(results['failed'])}`",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Utils Recargados",
            value="`glass_image_builder`\n`roblox_image_builder`\n`image_builder`",
            inline=False
        )
        
        if results["failed"]:
            failed_text = "\n".join([f"• **{m}**: {msg[:50]}..." for m, msg in results["failed"][:5]])
            embed.add_field(
                name="Módulos con Error",
                value=failed_text,
                inline=False
            )
        
        print(f"\n{T.PINK}✅ Recarga completada{T.RESET}\n")
        
        await ctx.send(embed=embed)

@bot.command(name="rest", aliases=["restart", "reiniciar"])
async def restart_command(ctx, mode: str = None):
    """Reinicia el bot automáticamente"""
    
    # Verificar permisos de administrador
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title=f"{Icons.ERROR} Acceso Denegado",
            description="Solo administradores pueden usar este comando.",
            color=Colors.SOFT_RED
        )
        return await ctx.send(embed=embed)
    
    # Modo full
    if mode and mode.lower() == "full":
        embed = discord.Embed(
            title=f"{Icons.REFRESH} Reinicio Completo",
            description="🔄 Reiniciando bot en modo completo...\nSe limpiarán todos los datos en caché.",
            color=Colors.GOLD
        )
        await ctx.send(embed=embed)
        
        # Limpiar logs
        save_logs([])
        
        await asyncio.sleep(1)
        await bot.close()
    else:
        # Reinicio normal
        embed = discord.Embed(
            title=f"{Icons.REFRESH} Reinicio",
            description="🔄 Reiniciando bot...",
            color=Colors.GOLD
        )
        await ctx.send(embed=embed)
        
        await asyncio.sleep(1)
        await bot.close()

# ══════════════════════════════════════════════════════════════════════════════
# 🔄 SISTEMA AVANZADO DE CARGA DE MÓDULOS
# ══════════════════════════════════════════════════════════════════════════════

class ModuleManager:
    """Gestor inteligente de módulos con carga automática y recargas en caliente + UTILS"""
    
    def __init__(self, bot):
        self.bot = bot
        self.loaded_modules = {}
        self.failed_modules = []
        self.module_info = {}
        self.utils_cache = {}  # Caché para limpiar utils
        
    async def load_all(self):
        """Cargar todos los módulos disponibles"""
        T = Colors.Terminal
        folder = BotConfig.MODULES_FOLDER
        
        if not os.path.exists(folder):
            print(f"{T.YELLOW}  ⚠ No se encontró carpeta: {folder}{T.RESET}")
            return 0, 0
        
        print(f"\n{T.PINK}╔═══════════════════════════════════════════════════════════╗{T.RESET}")
        print(f"{T.PINK}║  {T.WHITE}{T.BOLD}🌸 CARGANDO MÓDULOS DEL SISTEMA 🌸{T.RESET}{T.PINK}                    ║{T.RESET}")
        print(f"{T.PINK}╚═══════════════════════════════════════════════════════════╝{T.RESET}\n")
        
        modules = sorted([f[:-3] for f in os.listdir(folder) if f.endswith('.py') and not f.startswith('_')])
        success, failed = await self._load_modules(modules, folder)
        
        self._print_summary(success, failed, len(modules))
        return success, failed
    
    async def _load_modules(self, modules, folder):
        """Cargar módulos con validación"""
        T = Colors.Terminal
        success = 0
        
        for module_name in modules:
            ext = f'{folder}.{module_name}'
            try:
                # Validar que el archivo tenga una clase Cog
                module_path = os.path.join(folder, f'{module_name}.py')
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'async def setup' not in content:
                        raise ValueError("Falta función 'async def setup(bot)' en el módulo")
                
                await self.bot.load_extension(ext)
                
                self.loaded_modules[module_name] = {
                    'status': 'active',
                    'loaded_at': datetime.now(),
                    'path': module_path
                }
                
                emoji = random.choice(['🎀', '✨', '🔮', '⭐', '🌙', '🌸', '💖', '🎨'])
                print(f"  {T.VIOLET}{emoji} {T.WHITE}{module_name.ljust(25)} {T.PINK}│ {T.GREEN}✓ CARGADO{T.RESET}")
                success += 1
                await asyncio.sleep(0.03)
                
            except Exception as e:
                self.failed_modules.append({
                    'module': module_name,
                    'error': str(e),
                    'trace': traceback.format_exc()
                })
                print(f"  {T.PINK}❌ {T.WHITE}{module_name.ljust(25)} {T.PINK}│ {T.RED}ERROR{T.RESET}")
                if BotConfig.DEBUG_MODE:
                    print(f"     └─ {str(e)[:50]}")
        
        return success, len(self.failed_modules)
    
    def _print_summary(self, success, failed, total):
        """Mostrar resumen de carga"""
        T = Colors.Terminal
        print(f"{T.PINK}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{T.RESET}")
        print(f"{T.GREEN}  ✔ Cargados: {success}/{total}{T.RESET}  {T.PINK}│{T.RESET}  {T.PINK}✗ Errores: {failed}{T.RESET}")
        print(f"{T.PINK}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{T.RESET}\n")
        
        if self.failed_modules and BotConfig.DEBUG_MODE:
            print(f"{T.PINK}📋 Detalles de errores:{T.RESET}\n")
            for item in self.failed_modules:
                print(f"  {T.RED}✗{T.RESET} {item['module']}: {item['error']}\n")
    
    def _reload_utils(self, module_name):
        """Recargar utils asociados al módulo (GlassImageBuilder, RobloxImageBuilder, etc)"""
        try:
            # Limpiar imports de utils
            utils_to_reload = [
                'utils.glass_image_builder',
                'utils.roblox_image_builder',
                'utils.image_builder',
            ]
            
            for util_module in utils_to_reload:
                if util_module in sys.modules:
                    # Recargar el módulo
                    import importlib
                    importlib.reload(sys.modules[util_module])
            
            return True
        except Exception as e:
            logging.error(f"Error recargando utils: {e}")
            return False
    
    async def reload(self, module_name):
        """Recargar un módulo en caliente con limpieza completa + UTILS"""
        folder = BotConfig.MODULES_FOLDER
        ext = f'{folder}.{module_name}'
        
        try:
            # 1. Validar que el módulo existe
            module_path = os.path.join(folder, f'{module_name}.py')
            if not os.path.exists(module_path):
                return False, f"Módulo '{module_name}' no encontrado en {folder}/"
            
            # 2. Validar que tiene setup
            with open(module_path, 'r', encoding='utf-8') as f:
                if 'async def setup' not in f.read():
                    return False, f"Módulo '{module_name}' sin función 'async def setup(bot)'"
            
            # 3. RECARGAR UTILS PRIMERO
            self._reload_utils(module_name)
            
            # 4. Descargar si está cargado
            if ext in self.bot.extensions:
                try:
                    await self.bot.unload_extension(ext)
                except Exception as e:
                    print(f"  ⚠️ Aviso al descargar {module_name}: {e}")
            
            # 5. Limpiar del diccionario de módulos Python
            if ext in sys.modules:
                del sys.modules[ext]
            
            # 6. Limpiar submódulos cargados por este módulo
            modules_to_remove = [mod for mod in list(sys.modules.keys()) if mod.startswith(ext)]
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]
            
            # 7. Cargar nuevamente
            try:
                await self.bot.load_extension(ext)
                
                self.loaded_modules[module_name] = {
                    'status': 'active',
                    'loaded_at': datetime.now(),
                    'path': module_path,
                    'reloads': self.loaded_modules.get(module_name, {}).get('reloads', 0) + 1
                }
                
                # Remover de lista de errores si estaba
                self.failed_modules = [e for e in self.failed_modules if e['module'] != module_name]
                
                return True, f"✅ **{module_name}** recargado (con utils) exitosamente"
            
            except Exception as e:
                self.loaded_modules[module_name] = {
                    'status': 'error',
                    'error': str(e),
                    'loaded_at': datetime.now(),
                    'path': module_path
                }
                
                # Agregar a errores
                error_found = False
                for err in self.failed_modules:
                    if err['module'] == module_name:
                        err['error'] = str(e)
                        err['trace'] = traceback.format_exc()
                        error_found = True
                        break
                
                if not error_found:
                    self.failed_modules.append({
                        'module': module_name,
                        'error': str(e),
                        'trace': traceback.format_exc()
                    })
                
                return False, f"❌ Error al recargar: {str(e)[:100]}"
        
        except Exception as e:
            return False, f"❌ Error en validación: {str(e)[:100]}"
    
    def get_info(self):
        """Obtener información de módulos cargados"""
        return {
            'total_loaded': len(self.loaded_modules),
            'total_failed': len(self.failed_modules),
            'modules': self.loaded_modules,
            'errors': self.failed_modules
        }

async def load_extensions():
    """Cargar extensiones usando ModuleManager avanzado"""
    module_manager = ModuleManager(bot)
    await module_manager.load_all()
    bot.module_manager = module_manager

# ══════════════════════════════════════════════════════════════════════════════
# 🚀 PUNTO DE ENTRADA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def main():
        """Función principal de inicio"""
        try:
            # Guardar tiempo de inicio
            bot.start_time = datetime.now()
            
            # Mostrar animación de carga
            aesthetic_loading()
            
            # Iniciar bot
            async with bot:
                await load_extensions()
                await bot.start(BotConfig.TOKEN)
                
        except KeyboardInterrupt:
            T = Colors.Terminal
            print(f"\n\n{T.PINK}{T.BOLD}  {Icons.HEART} Apagando bot... ¡Hasta pronto! {Icons.SPARKLES}{T.RESET}\n")
        except Exception as e:
            T = Colors.Terminal
            print(f"\n{T.PINK}  {Icons.ERROR} Error crítico: {T.WHITE}{e}{T.RESET}\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass