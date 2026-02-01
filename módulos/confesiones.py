import discord
from discord.ext import commands, tasks
from discord import ui
from datetime import datetime, timedelta
import json
import os
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# ⚙️ CONFIGURACIÓN PERSONALIZABLE - EDITA AQUÍ TUS PREFERENCIAS
# =============================================================================
class Config:
    # 🎨 COLORES (Formato hexadecimal)
    COLOR_PRIMARY = 0xFF85A1        # Rosa principal
    COLOR_SECONDARY = 0xD4ADFC      # Lavanda
    COLOR_ACCENT = 0xFFD700         # Dorado
    COLOR_SUCCESS = 0x2ECC71        # Verde éxito
    COLOR_DANGER = 0xE74C3C         # Rojo peligro
    COLOR_INFO = 0x3498DB           # Azul información
    COLOR_PENDING = 0xFFA500        # Naranja pendiente
    
    # 📝 TEXTOS DEL PANEL PRINCIPAL
    PANEL_TITLE = "CONFESIONES ANÓNIMAS"
    PANEL_SUBTITLE = "Sistema de Confesiones NODEX"
    PANEL_DESCRIPTION = (
        "Comparte tus pensamientos de forma **100% anónima**.\n\n"
        "🔹 Haz clic en el botón de abajo\n"
        "🔹 Escribe tu confesión\n"
        "🔹 ¡Envía y espera la aprobación!\n\n"
        "Tu identidad está completamente protegida. 🔒"
    )
    PANEL_FOOTER = "Sistema Protegido y Encriptado"
    PANEL_BUTTON_LABEL = "📨 Enviar Confesión"
    PANEL_BUTTON_EMOJI = "💌"
    
    # 📝 TEXTOS DEL MODAL
    MODAL_TITLE = "🌸 Rincón de Secretos"
    MODAL_CONFESSION_LABEL = "¿Qué quieres confesar?"
    MODAL_CONFESSION_PLACEHOLDER = "Tu identidad será 100% anónima... ✨"
    MODAL_IMAGE_LABEL = "🖼️ Imagen (Opcional)"
    MODAL_IMAGE_PLACEHOLDER = "Pega el link de la imagen aquí..."
    
    # 📝 TEXTOS DE PUBLICACIÓN
    PUBLIC_TITLE = "🌸 Confesión Anónima"
    PUBLIC_FOOTER = "Enviado de forma anónima • ✨"
    
    # 🎨 DECORACIÓN
    DECORATION_EMOJI = "🌸"
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━"
    
    # 🖼️ CONFIGURACIÓN DE IMAGEN DEL PANEL
    PANEL_IMAGE_WIDTH = 900
    PANEL_IMAGE_HEIGHT = 500
    PANEL_IMAGE_BG_COLOR = (255, 133, 161)  # RGB del color rosa
    PANEL_IMAGE_TEXT_COLOR = (255, 255, 255)  # Blanco
    PANEL_IMAGE_ACCENT_COLOR = (212, 173, 252)  # Lavanda RGB
    
    # 🖼️ ICONO/LOGO CENTRAL (Opcional - Deja vacío "" si no quieres icono)
    PANEL_ICON_URL = ""  # Ejemplo: "https://i.imgur.com/tu-icono.png"
    PANEL_ICON_SIZE = 120  # Tamaño del icono en píxeles
    
    # ⏱️ TIEMPO DE AUTO-APROBACIÓN (en minutos)
    AUTO_APPROVE_MINUTES = 2
    
    # 🔄 INTERVALO DE VERIFICACIÓN (en segundos)
    CHECK_INTERVAL = 30

# =============================================================================
# 📁 CONFIGURACIÓN DE RUTAS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "stories_data.json")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
FONT_PATH = os.path.join(FONTS_DIR, "classic.ttf")

def load_stories():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_stories(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# =============================================================================
# 🎨 GENERADOR DE IMAGEN DEL PANEL
# =============================================================================
def create_panel_image(guild_icon_url=None):
    """Crea una imagen personalizada estilo glassmorphism para el panel de confesiones"""
    # Fondo degradado oscuro (dark purple/pink)
    img = Image.new('RGB', (Config.PANEL_IMAGE_WIDTH, Config.PANEL_IMAGE_HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Crear degradado de fondo dark
    for y in range(Config.PANEL_IMAGE_HEIGHT):
        # Degradado de morado oscuro a rosa oscuro
        r = int(40 + (y / Config.PANEL_IMAGE_HEIGHT) * 60)   # 40 -> 100
        g = int(20 + (y / Config.PANEL_IMAGE_HEIGHT) * 30)   # 20 -> 50
        b = int(60 + (y / Config.PANEL_IMAGE_HEIGHT) * 60)   # 60 -> 120
        draw.rectangle([(0, y), (Config.PANEL_IMAGE_WIDTH, y + 1)], fill=(r, g, b))
    
    # Intentar cargar la fuente personalizada
    try:
        font_title = ImageFont.truetype(FONT_PATH, 65)
        font_subtitle = ImageFont.truetype(FONT_PATH, 28)
        font_small = ImageFont.truetype(FONT_PATH, 22)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Efecto glass - Rectángulo semitransparente (simulado con alpha blend)
    glass_overlay = Image.new('RGBA', (Config.PANEL_IMAGE_WIDTH, Config.PANEL_IMAGE_HEIGHT), (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass_overlay)
    
    # Panel glass central - Ajustado para que el contenido quepa
    glass_margin = 50
    glass_y_start = 70
    glass_y_end = Config.PANEL_IMAGE_HEIGHT - 70
    
    # Fondo del glass con bordes redondeados
    glass_draw.rounded_rectangle(
        [(glass_margin, glass_y_start), (Config.PANEL_IMAGE_WIDTH - glass_margin, glass_y_end)],
        radius=30,
        fill=(255, 255, 255, 15)  # Blanco muy transparente
    )
    
    # Borde del glass
    glass_draw.rounded_rectangle(
        [(glass_margin, glass_y_start), (Config.PANEL_IMAGE_WIDTH - glass_margin, glass_y_end)],
        radius=30,
        outline=(255, 255, 255, 60),
        width=2
    )
    
    # Brillo superior del glass
    glass_draw.rounded_rectangle(
        [(glass_margin + 15, glass_y_start + 15), (Config.PANEL_IMAGE_WIDTH - glass_margin - 15, glass_y_start + 90)],
        radius=25,
        fill=(255, 255, 255, 10)
    )
    
    # Combinar el glass con la imagen principal
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glass_overlay)
    img = img.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Decoración superior - Línea de acento con glow
    accent_y = 40
    for i in range(3):
        alpha = 100 - (i * 30)
        draw.line(
            [(180 - i, accent_y), (Config.PANEL_IMAGE_WIDTH - 180 + i, accent_y)],
            fill=(255, 150, 200),
            width=3 - i
        )
    
    # Título principal con sombra - AJUSTADO
    title_text = Config.PANEL_TITLE
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (Config.PANEL_IMAGE_WIDTH - title_width) // 2
    title_y = 110  # Ajustado para estar dentro del glass
    
    # Sombra del título
    draw.text((title_x + 3, title_y + 3), title_text, fill=(0, 0, 0), font=font_title)
    # Título principal
    draw.text((title_x, title_y), title_text, fill=(255, 200, 220), font=font_title)
    
    # ICONO CENTRAL (si está configurado)
    icon_y_position = title_y + 90
    
    if Config.PANEL_ICON_URL or guild_icon_url:
        try:
            import requests
            from io import BytesIO as IOBytes
            
            icon_url = Config.PANEL_ICON_URL if Config.PANEL_ICON_URL else guild_icon_url
            response = requests.get(icon_url, timeout=5)
            icon_img = Image.open(IOBytes(response.content))
            
            # Redimensionar el icono
            icon_size = Config.PANEL_ICON_SIZE
            icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            
            # Crear máscara circular
            mask = Image.new('L', (icon_size, icon_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([(0, 0), (icon_size, icon_size)], fill=255)
            
            # Convertir a RGBA si es necesario
            if icon_img.mode != 'RGBA':
                icon_img = icon_img.convert('RGBA')
            
            # Aplicar máscara circular
            output = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            output.paste(icon_img, (0, 0))
            output.putalpha(mask)
            
            # Crear borde brillante alrededor del icono
            border_size = icon_size + 8
            border = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border)
            border_draw.ellipse([(0, 0), (border_size, border_size)], 
                              outline=(255, 200, 220, 200), width=4)
            
            # Posicionar en el centro
            icon_x = (Config.PANEL_IMAGE_WIDTH - border_size) // 2
            icon_y = icon_y_position
            
            # Pegar borde y luego icono
            img_rgba = img.convert('RGBA')
            img_rgba.paste(border, (icon_x, icon_y), border)
            img_rgba.paste(output, (icon_x + 4, icon_y + 4), output)
            img = img_rgba.convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Ajustar posición del emoji decorativo
            icon_y_position += icon_size + 20
        except:
            pass  # Si falla, continuar sin icono
    
    # Emoji decorativo - AJUSTADO
    emoji_text = "✨ 💌 ✨"
    emoji_bbox = draw.textbbox((0, 0), emoji_text, font=font_subtitle)
    emoji_width = emoji_bbox[2] - emoji_bbox[0]
    emoji_x = (Config.PANEL_IMAGE_WIDTH - emoji_width) // 2
    emoji_y = icon_y_position
    draw.text((emoji_x, emoji_y), emoji_text, fill=(255, 180, 210), font=font_subtitle)
    
    # Línea decorativa inferior - AJUSTADA
    line_y = Config.PANEL_IMAGE_HEIGHT - 115  # Subida para quedar dentro del glass
    for i in range(3):
        draw.line(
            [(220 - i, line_y), (Config.PANEL_IMAGE_WIDTH - 220 + i, line_y)],
            fill=(200, 150, 255),
            width=2 - (i // 2)
        )
    
    # Subtítulo/Footer - AJUSTADO para estar dentro del glass
    footer_text = Config.PANEL_SUBTITLE
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_small)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (Config.PANEL_IMAGE_WIDTH - footer_width) // 2
    footer_y = Config.PANEL_IMAGE_HEIGHT - 85  # Subido para estar dentro del glass
    
    # Sombra del footer
    draw.text((footer_x + 2, footer_y + 2), footer_text, fill=(0, 0, 0), font=font_small)
    # Footer
    draw.text((footer_x, footer_y), footer_text, fill=(180, 160, 220), font=font_small)
    
    # Puntos decorativos (estrellas pequeñas) - AJUSTADOS
    star_positions = [
        (120, 140), (Config.PANEL_IMAGE_WIDTH - 120, 140),
        (100, Config.PANEL_IMAGE_HEIGHT - 120), (Config.PANEL_IMAGE_WIDTH - 100, Config.PANEL_IMAGE_HEIGHT - 120)
    ]
    
    for x, y in star_positions:
        # Estrella pequeña
        draw.ellipse([(x - 3, y - 3), (x + 3, y + 3)], fill=(255, 200, 230))
        draw.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=(255, 255, 255))
    
    # Guardar en BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

# =============================================================================
# 🎭 MODALES
# =============================================================================
class ConfesionModal(ui.Modal, title=Config.MODAL_TITLE):
    confesion_text = ui.TextInput(
        label=Config.MODAL_CONFESSION_LABEL,
        style=discord.TextStyle.paragraph,
        placeholder=Config.MODAL_CONFESSION_PLACEHOLDER,
        required=True,
        min_length=5,
        max_length=2000
    )
    multimedia_url = ui.TextInput(
        label=Config.MODAL_IMAGE_LABEL,
        placeholder=Config.MODAL_IMAGE_PLACEHOLDER,
        required=False
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        preview = discord.Embed(
            title="🔍 Vista Previa de tu Confesión",
            description=f"{Config.DIVIDER}\n\n{self.confesion_text.value}\n\n{Config.DIVIDER}",
            color=Config.COLOR_SECONDARY,
            timestamp=datetime.now()
        )
        
        media_url = self.multimedia_url.value.strip() if self.multimedia_url.value else None
        if media_url and (media_url.startswith(('http://', 'https://'))):
            preview.set_image(url=media_url)
        
        preview.set_footer(
            text="¿Confirmas el envío? Será enviado a moderación",
            icon_url=interaction.user.display_avatar.url
        )
        
        view = ConfesionConfirmView(
            self.confesion_text.value,
            media_url,
            interaction.user,
            self.bot
        )
        await interaction.followup.send(embed=preview, view=view, ephemeral=True)

# =============================================================================
# 🎮 VISTAS
# =============================================================================
class ConfesionConfirmView(ui.View):
    def __init__(self, content, media, author, bot):
        super().__init__(timeout=180)
        self.content = content
        self.media = media
        self.author = author
        self.bot = bot

    @ui.button(label="✅ Confirmar y Enviar", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        stories = load_stories()
        sid = len(stories) + 1
        
        story = {
            "id": sid,
            "author_id": str(self.author.id),
            "content": self.content,
            "attachment": self.media if self.media else None,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "guild_id": str(interaction.guild.id)
        }
        
        stories.append(story)
        save_stories(stories)
        
        # Enviar a moderación
        lchan_id = self.bot.config.get("story_log_channel")
        if lchan_id:
            lchan = self.bot.get_channel(int(lchan_id))
            if lchan:
                log_embed = discord.Embed(
                    title=f"🛡️ Moderación de Confesión #{sid}",
                    description=f"{Config.DIVIDER}\n**Estado:** ⏳ Pendiente de Revisión\n{Config.DIVIDER}",
                    color=Config.COLOR_PENDING,
                    timestamp=datetime.now()
                )
                
                log_embed.set_author(
                    name=f"📨 Nueva Confesión",
                    icon_url=self.author.display_avatar.url
                )
                
                log_embed.add_field(
                    name="👤 Remitente",
                    value=f"{self.author.mention}\n`ID: {self.author.id}`",
                    inline=True
                )
                
                log_embed.add_field(
                    name="📅 Fecha",
                    value=f"<t:{int(datetime.now().timestamp())}:R>",
                    inline=True
                )
                
                log_embed.add_field(
                    name="📝 Contenido",
                    value=f"```\n{self.content[:500]}{'...' if len(self.content) > 500 else ''}\n```",
                    inline=False
                )
                
                if self.media and self.media.startswith(('http://', 'https://')):
                    log_embed.set_image(url=self.media)
                
                log_embed.set_footer(
                    text=f"ID de Confesión: #{sid} • Auto-aprobación en {Config.AUTO_APPROVE_MINUTES} min",
                    icon_url=interaction.guild.icon.url if interaction.guild.icon else None
                )
                
                msg = await lchan.send(
                    embed=log_embed,
                    view=ConfesionModerateView(sid, self.bot)
                )
                
                story["mod_msg_id"] = msg.id
                save_stories(stories)
        
        # Confirmar al usuario
        success_embed = discord.Embed(
            title="✅ Confesión Enviada",
            description=(
                f"{Config.DIVIDER}\n\n"
                "Tu confesión ha sido enviada correctamente.\n\n"
                "**Estado:** ⏳ En revisión\n"
                f"**ID:** #{sid}\n\n"
                "Recibirás una notificación cuando sea aprobada.\n\n"
                f"{Config.DIVIDER}"
            ),
            color=Config.COLOR_SUCCESS
        )
        success_embed.set_footer(text="Gracias por usar el sistema de confesiones")
        
        await interaction.edit_original_response(embed=success_embed, view=None)

    @ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        cancel_embed = discord.Embed(
            title="❌ Confesión Cancelada",
            description="Tu confesión no fue enviada.",
            color=Config.COLOR_INFO
        )
        await interaction.response.edit_message(embed=cancel_embed, view=None)

class ConfesionModerateView(ui.View):
    def __init__(self, story_id=None, bot=None):
        super().__init__(timeout=None)
        self.story_id = story_id
        self.bot = bot

    @ui.button(label="Aprobar", emoji="✅", style=discord.ButtonStyle.success, custom_id="mod_approve")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if await process_confession(self.bot, self.story_id, "approved", interaction.user):
            approved_embed = discord.Embed(
                title="✅ Confesión Aprobada",
                description=f"La confesión #{self.story_id} ha sido aprobada y publicada.",
                color=Config.COLOR_SUCCESS
            )
            await interaction.followup.send(embed=approved_embed, ephemeral=True)
            await interaction.message.edit(view=None)

    @ui.button(label="Rechazar", emoji="❌", style=discord.ButtonStyle.danger, custom_id="mod_reject")
    async def reject(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if await process_confession(self.bot, self.story_id, "rejected", interaction.user):
            rejected_embed = discord.Embed(
                title="❌ Confesión Rechazada",
                description=f"La confesión #{self.story_id} ha sido rechazada.",
                color=Config.COLOR_DANGER
            )
            await interaction.followup.send(embed=rejected_embed, ephemeral=True)
            await interaction.message.edit(view=None)

# =============================================================================
# ⚙️ PROCESAMIENTO DE CONFESIONES
# =============================================================================
async def process_confession(bot, story_id, status, moderator=None):
    """Procesa la aprobación o rechazo de una confesión"""
    stories = load_stories()
    story = next((s for s in stories if s["id"] == story_id), None)
    
    if not story or story["status"] != "pending":
        return False
    
    story["status"] = status
    story["moderated_by"] = str(moderator.id) if moderator else "auto"
    story["moderated_at"] = datetime.now().isoformat()
    save_stories(stories)
    
    # Registrar en logs
    lchan_id = bot.config.get("story_log_channel")
    if lchan_id:
        lchan = bot.get_channel(int(lchan_id))
        if lchan:
            color = Config.COLOR_SUCCESS if status == "approved" else Config.COLOR_DANGER
            action = "✅ APROBADA" if status == "approved" else "❌ RECHAZADA"
            mod_mention = moderator.mention if moderator else "🤖 Sistema (Auto-aprobación)"
            
            final_embed = discord.Embed(
                title=f"📋 Resolución de Confesión #{story_id}",
                description=f"{Config.DIVIDER}\n**Acción:** {action}\n**Moderador:** {mod_mention}\n{Config.DIVIDER}",
                color=color,
                timestamp=datetime.now()
            )
            
            author = bot.get_user(int(story["author_id"]))
            if author:
                final_embed.set_author(
                    name=f"Remitente: {author.name}",
                    icon_url=author.display_avatar.url
                )
            
            final_embed.add_field(
                name="👤 Usuario",
                value=f"<@{story['author_id']}>",
                inline=True
            )
            
            final_embed.add_field(
                name="📅 Procesado",
                value=f"<t:{int(datetime.now().timestamp())}:R>",
                inline=True
            )
            
            final_embed.add_field(
                name="📝 Contenido",
                value=f"```\n{story['content'][:500]}{'...' if len(story['content']) > 500 else ''}\n```",
                inline=False
            )
            
            if story.get("attachment") and story["attachment"].startswith(('http://', 'https://')):
                final_embed.set_image(url=story["attachment"])
            
            final_embed.set_footer(text=f"ID: #{story_id}")
            
            await lchan.send(embed=final_embed)
    
    # Publicar si fue aprobada
    if status == "approved":
        pchan_id = bot.config.get("story_public_channel")
        if pchan_id:
            pchan = bot.get_channel(int(pchan_id))
            if pchan:
                public_embed = discord.Embed(
                    title=f"{Config.PUBLIC_TITLE} #{story_id}",
                    description=f"{Config.DIVIDER}\n\n{story['content']}\n\n{Config.DIVIDER}",
                    color=Config.COLOR_PRIMARY,
                    timestamp=datetime.now()
                )
                
                if story.get("attachment") and story["attachment"].startswith(('http://', 'https://')):
                    public_embed.set_image(url=story["attachment"])
                
                public_embed.set_footer(text=Config.PUBLIC_FOOTER)
                
                await pchan.send(embed=public_embed)
    
    return True

# =============================================================================
# 🎯 COG PRINCIPAL
# =============================================================================
class Confesiones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_accept_loop.start()
        self.bot.add_view(ConfesionPanelView(self.bot))
        self.bot.add_view(ConfesionModerateView(bot=self.bot))

    @tasks.loop(seconds=Config.CHECK_INTERVAL)
    async def auto_accept_loop(self):
        """Auto-aprueba confesiones después del tiempo configurado"""
        stories = load_stories()
        now = datetime.now()
        
        for s in stories:
            if s["status"] == "pending":
                created_time = datetime.fromisoformat(s["timestamp"])
                if now - created_time > timedelta(minutes=Config.AUTO_APPROVE_MINUTES):
                    if await process_confession(self.bot, s["id"], "approved"):
                        # Remover botones del mensaje de moderación
                        lchan = self.bot.get_channel(int(self.bot.config.get("story_log_channel")))
                        if lchan and "mod_msg_id" in s:
                            try:
                                msg = await lchan.fetch_message(s["mod_msg_id"])
                                await msg.edit(view=None)
                            except:
                                pass

    @commands.command(name="set-canal-moderacion")
    @commands.has_permissions(administrator=True)
    async def set_canal_moderacion(self, ctx, channel: discord.TextChannel = None):
        """Establece el canal donde se moderan las confesiones"""
        if channel is None:
            channel = ctx.channel
        
        self.bot.config["story_log_channel"] = str(channel.id)
        
        # Guardar configuración (asumiendo que el bot tiene un método para esto)
        if hasattr(self.bot, 'save_config'):
            self.bot.save_config(self.bot.config)
        
        config_embed = discord.Embed(
            title="✅ Canal de Moderación Configurado",
            description=(
                f"{Config.DIVIDER}\n\n"
                f"**Canal establecido:** {channel.mention}\n\n"
                f"Todas las confesiones pendientes aparecerán aquí para su revisión.\n\n"
                f"{Config.DIVIDER}"
            ),
            color=Config.COLOR_SUCCESS,
            timestamp=datetime.now()
        )
        
        config_embed.set_footer(
            text="Sistema de Confesiones NODEX",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.send(embed=config_embed)
    
    @commands.command(name="set-canal-publico")
    @commands.has_permissions(administrator=True)
    async def set_canal_publico(self, ctx, channel: discord.TextChannel = None):
        """Establece el canal donde se publican las confesiones aprobadas"""
        if channel is None:
            channel = ctx.channel
        
        self.bot.config["story_public_channel"] = str(channel.id)
        
        # Guardar configuración
        if hasattr(self.bot, 'save_config'):
            self.bot.save_config(self.bot.config)
        
        config_embed = discord.Embed(
            title="✅ Canal Público Configurado",
            description=(
                f"{Config.DIVIDER}\n\n"
                f"**Canal establecido:** {channel.mention}\n\n"
                f"Las confesiones aprobadas se publicarán automáticamente aquí.\n\n"
                f"{Config.DIVIDER}"
            ),
            color=Config.COLOR_SUCCESS,
            timestamp=datetime.now()
        )
        
        config_embed.set_footer(
            text="Sistema de Confesiones NODEX",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.send(embed=config_embed)
    
    @commands.command(name="ver-config-confesiones")
    @commands.has_permissions(administrator=True)
    async def ver_config(self, ctx):
        """Muestra la configuración actual del sistema de confesiones"""
        log_channel_id = self.bot.config.get("story_log_channel")
        public_channel_id = self.bot.config.get("story_public_channel")
        
        log_channel = self.bot.get_channel(int(log_channel_id)) if log_channel_id else None
        public_channel = self.bot.get_channel(int(public_channel_id)) if public_channel_id else None
        
        config_embed = discord.Embed(
            title="⚙️ Configuración del Sistema",
            description=f"{Config.DIVIDER}",
            color=Config.COLOR_INFO,
            timestamp=datetime.now()
        )
        
        config_embed.add_field(
            name="📋 Canal de Moderación",
            value=log_channel.mention if log_channel else "❌ No configurado",
            inline=False
        )
        
        config_embed.add_field(
            name="📢 Canal Público",
            value=public_channel.mention if public_channel else "❌ No configurado",
            inline=False
        )
        
        config_embed.add_field(
            name="⏱️ Auto-aprobación",
            value=f"```{Config.AUTO_APPROVE_MINUTES} minutos```",
            inline=True
        )
        
        config_embed.add_field(
            name="🔄 Intervalo de Revisión",
            value=f"```{Config.CHECK_INTERVAL} segundos```",
            inline=True
        )
        
        config_embed.set_footer(
            text="Sistema de Confesiones NODEX",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.send(embed=config_embed)
    
    @commands.command(name="panel-cf")
    @commands.has_permissions(administrator=True)
    async def panel_confesiones(self, ctx):
        """Crea el panel de confesiones con imagen personalizada"""
        # Crear imagen del panel
        panel_img = create_panel_image()
        file = discord.File(fp=panel_img, filename="panel_confesiones.png")
        
        # Crear embed
        embed = discord.Embed(
            title=f"{Config.DECORATION_EMOJI} {Config.PANEL_TITLE}",
            description=f"{Config.DIVIDER}\n\n{Config.PANEL_DESCRIPTION}\n{Config.DIVIDER}",
            color=Config.COLOR_PRIMARY
        )
        
        embed.set_image(url="attachment://panel_confesiones.png")
        
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.set_footer(
            text=Config.PANEL_FOOTER,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.send(file=file, embed=embed, view=ConfesionPanelView(self.bot))
    
    @commands.command(name="confesiones-stats")
    @commands.has_permissions(administrator=True)
    async def confesiones_stats(self, ctx):
        """Muestra estadísticas del sistema de confesiones"""
        stories = load_stories()
        
        total = len(stories)
        approved = len([s for s in stories if s["status"] == "approved"])
        rejected = len([s for s in stories if s["status"] == "rejected"])
        pending = len([s for s in stories if s["status"] == "pending"])
        
        stats_embed = discord.Embed(
            title="📊 Estadísticas de Confesiones",
            description=f"{Config.DIVIDER}",
            color=Config.COLOR_INFO,
            timestamp=datetime.now()
        )
        
        stats_embed.add_field(
            name="📝 Total de Confesiones",
            value=f"```{total}```",
            inline=True
        )
        
        stats_embed.add_field(
            name="✅ Aprobadas",
            value=f"```{approved}```",
            inline=True
        )
        
        stats_embed.add_field(
            name="❌ Rechazadas",
            value=f"```{rejected}```",
            inline=True
        )
        
        stats_embed.add_field(
            name="⏳ Pendientes",
            value=f"```{pending}```",
            inline=True
        )
        
        if total > 0:
            approval_rate = (approved / total) * 100
            stats_embed.add_field(
                name="📈 Tasa de Aprobación",
                value=f"```{approval_rate:.1f}%```",
                inline=True
            )
        
        stats_embed.set_footer(
            text="Sistema de Confesiones NODEX",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await ctx.send(embed=stats_embed)
    
    @commands.command(name="confesiones-clear")
    @commands.has_permissions(administrator=True)
    async def confesiones_clear(self, ctx, confession_id: int = None):
        """Elimina una confesión específica o todas las confesiones"""
        stories = load_stories()
        
        if confession_id:
            # Eliminar una confesión específica
            story = next((s for s in stories if s["id"] == confession_id), None)
            if story:
                stories.remove(story)
                save_stories(stories)
                
                delete_embed = discord.Embed(
                    title="🗑️ Confesión Eliminada",
                    description=f"La confesión #{confession_id} ha sido eliminada del sistema.",
                    color=Config.COLOR_SUCCESS
                )
                await ctx.send(embed=delete_embed)
            else:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description=f"No se encontró ninguna confesión con ID #{confession_id}",
                    color=Config.COLOR_DANGER
                )
                await ctx.send(embed=error_embed)
        else:
            # Confirmar antes de eliminar todo
            confirm_embed = discord.Embed(
                title="⚠️ Confirmación Requerida",
                description=(
                    "¿Estás seguro de que quieres **eliminar TODAS las confesiones**?\n\n"
                    "Esta acción **NO se puede deshacer**.\n\n"
                    "Escribe `confirmar` para proceder o `cancelar` para abortar."
                ),
                color=Config.COLOR_DANGER
            )
            await ctx.send(embed=confirm_embed)
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                if msg.content.lower() == 'confirmar':
                    save_stories([])
                    success_embed = discord.Embed(
                        title="✅ Sistema Limpiado",
                        description="Todas las confesiones han sido eliminadas.",
                        color=Config.COLOR_SUCCESS
                    )
                    await ctx.send(embed=success_embed)
                else:
                    cancel_embed = discord.Embed(
                        title="❌ Cancelado",
                        description="La operación ha sido cancelada.",
                        color=Config.COLOR_INFO
                    )
                    await ctx.send(embed=cancel_embed)
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏱️ Tiempo Agotado",
                    description="La operación ha sido cancelada por inactividad.",
                    color=Config.COLOR_DANGER
                )
                await ctx.send(embed=timeout_embed)

class ConfesionPanelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @ui.button(
        label=Config.PANEL_BUTTON_LABEL,
        emoji=Config.PANEL_BUTTON_EMOJI,
        style=discord.ButtonStyle.primary,
        custom_id="btn_confess"
    )
    async def send(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ConfesionModal(self.bot))

async def setup(bot):
    await bot.add_cog(Confesiones(bot))