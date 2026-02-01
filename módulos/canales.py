
import discord
from discord.ext import commands
from discord import ui
import json
import os
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rich.console import Console
from rich.panel import Panel
import aiohttp

# ──────────────────────────────
# CONSTANTES
# ──────────────────────────────

DATA_PATH = "data/config.json"
EMBED_COLOR = 0xff79c6  # ROSA PROTAGONISTA
EMBED_DARK = 0x1a0a1f   # MORADO OSCURO
RICH_STYLE = "bold #ff79c6"

console = Console()

# ──────────────────────────────
# CONFIG
# ──────────────────────────────

def load_config():
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w") as f:
            json.dump({}, f, indent=4)
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_config(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

# ──────────────────────────────
# BANNER GENERATOR (ULTRA MEJORADO CON FUENTES GRANDES)
# ──────────────────────────────

async def generate_banner(member: discord.Member, mode: str, custom_bg=None):
    W, H = 900, 400
    
    # Fondo con gradiente
    base = Image.new("RGBA", (W, H), "#0a0a0f")
    draw = ImageDraw.Draw(base)
    
    # Gradiente oscuro elegante
    for y in range(H):
        alpha = int(30 * (y / H))
        draw.rectangle([(0, y), (W, y+1)], fill=f"#{alpha:02x}0a{alpha+10:02x}")
    
    # Efectos de partículas (estrellas)
    import random
    random.seed(member.id)
    for _ in range(50):
        x = random.randint(0, W)
        y = random.randint(0, H)
        size = random.randint(1, 3)
        alpha = random.randint(100, 255)
        draw.ellipse((x, y, x+size, y+size), fill=(255, 121, 198, alpha))
    
    # Marco rosa elegante con brillo
    for i in range(3):
        draw.rounded_rectangle(
            (12-i, 12-i, W-12+i, H-12+i),
            radius=24,
            outline=(255, 121, 198, 100-i*20),
            width=2
        )
    draw.rounded_rectangle(
        (12, 12, W-12, H-12),
        radius=24,
        outline="#ff79c6",
        width=4
    )
    
    # Avatar con efecto glow
    avatar_size = 140
    try:
        avatar_bytes = await member.display_avatar.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((avatar_size, avatar_size))
        
        # Crear máscara circular
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
        
        # Efecto glow alrededor del avatar
        glow = Image.new("RGBA", (avatar_size+20, avatar_size+20), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        for i in range(10, 0, -1):
            alpha = int(50 - i*4)
            glow_draw.ellipse(
                (10-i, 10-i, avatar_size+10+i, avatar_size+10+i),
                fill=(255, 121, 198, alpha)
            )
        
        base.paste(glow, (60-10, H//2 - avatar_size//2-10), glow)
        avatar.putalpha(mask)
        
        # Borde del avatar
        avatar_border = Image.new("RGBA", (avatar_size+8, avatar_size+8), (0, 0, 0, 0))
        ImageDraw.Draw(avatar_border).ellipse((0, 0, avatar_size+8, avatar_size+8), outline="#ff79c6", width=4)
        base.paste(avatar_border, (60-4, H//2 - avatar_size//2-4), avatar_border)
        base.paste(avatar, (60, H//2 - avatar_size//2), avatar)
    except:
        pass
    
    # ──────────────────────────────
    # CARGAR FUENTES PERSONALIZADAS (DESDE CARPETA fonts/)
    # ──────────────────────────────
    try:
        # Busca la fuente en la carpeta fonts/ en el directorio raíz
        font_title = ImageFont.truetype("fonts/classic.ttf", 40)  # Título grande
        font_subtitle = ImageFont.truetype("fonts/classic.ttf", 20)  # Subtítulo
        font_username = ImageFont.truetype("fonts/classic.ttf", 30)  # Usuario
        font_info = ImageFont.truetype("fonts/classic.ttf", 20)  # Info extra
    except:
        # Fuentes por defecto más grandes
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_subtitle = ImageFont.truetype("arial.ttf", 28)
            font_username = ImageFont.truetype("arial.ttf", 38)
            font_info = ImageFont.truetype("arial.ttf", 24)
        except:
            font_title = None
            font_subtitle = None
            font_username = None
            font_info = None
    
    if mode == "welcome":
        title = "WELCOME TO NODEX"
        subtitle = "a new soul has arrived"
        icon = "@"
    else:
        title = "GOODBYE, SWEET SOUL"
        subtitle = "your echo will remain"
        icon = ":C"
    
    username = member.display_name[:20]
    count = f"Soul #{member.guild.member_count}"
    joined = f"{datetime.utcnow().strftime('%d/%m/%Y - %H:%M UTC')}"
    
    # ──────────────────────────────
    # TEXTOS CON FUENTES GRANDES Y LEGIBLES
    # ──────────────────────────────
    text_x = 240
    
    # Título (GRANDE Y VISIBLE)
    draw.text((text_x, 60), title, fill="#ff79c6", font=font_title)
    
    # Subtítulo
    draw.text((text_x, 120), subtitle, fill="#d1d1d1", font=font_subtitle)
    
    # Usuario con icono
    draw.text((text_x, 180), f"{icon} {username}", fill="#ffffff", font=font_username)
    
    # Contador de miembros
    draw.text((text_x, 240), count, fill="#ff79c6", font=font_info)
    
    # Fecha/hora
    draw.text((text_x, 280), joined, fill="#a0a0a0", font=font_info)
    
    # Decoraciones finales
    draw.text((W-120, H-50), "<3", fill="#ff79c6", font=font_info)
    
    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ──────────────────────────────
# MODAL MEJORADO
# ──────────────────────────────

class IDModal(ui.Modal):
    def __init__(self, title, key):
        super().__init__(title=title)
        self.key = key
        self.input = ui.TextInput(
            label="ID numérica",
            placeholder="Pega aquí la ID del canal/rol",
            required=True,
            max_length=20
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = load_config()
            gid = str(interaction.guild.id)
            data.setdefault(gid, {})
            data[gid][self.key] = int(self.input.value)
            save_config(data)

            embed = discord.Embed(
                title="✧ Configuración Exitosa",
                description=f"🌸 **{self.key}** ha sido configurado correctamente\n\n⊱ ────── ✧ ────── ⊰",
                color=EMBED_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                "❌ **Error:** La ID debe ser numérica",
                ephemeral=True
            )

class MessageModal(ui.Modal):
    def __init__(self, title, key):
        super().__init__(title=title)
        self.key = key
        self.input = ui.TextInput(
            label="Mensaje personalizado",
            placeholder="Usa {user} para mencionar y {server} para el nombre del servidor",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_config()
        gid = str(interaction.guild.id)
        data.setdefault(gid, {})
        data[gid][self.key] = self.input.value
        save_config(data)

        embed = discord.Embed(
            title="✧ Mensaje Personalizado",
            description=f"🌸 El mensaje de **{self.key}** ha sido guardado\n\n⊱ ────── ✧ ────── ⊰",
            color=EMBED_COLOR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ──────────────────────────────
# PANEL VIEW MEJORADO
# ──────────────────────────────

class PanelView(ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @ui.button(label="🌸 Canal Bienvenida", style=discord.ButtonStyle.secondary, row=0)
    async def welcome(self, interaction, _):
        await interaction.response.send_modal(
            IDModal("Configurar Canal Bienvenida", "welcome_channel")
        )

    @ui.button(label="🥀 Canal Despedida", style=discord.ButtonStyle.secondary, row=0)
    async def leave(self, interaction, _):
        await interaction.response.send_modal(
            IDModal("Configurar Canal Despedida", "leave_channel")
        )

    @ui.button(label="🎀 Auto-Rol", style=discord.ButtonStyle.secondary, row=0)
    async def autorole(self, interaction, _):
        await interaction.response.send_modal(
            IDModal("Configurar Auto-Rol", "auto_role")
        )

    @ui.button(label="📝 Mensaje Bienvenida", style=discord.ButtonStyle.secondary, row=1)
    async def custom_welcome(self, interaction, _):
        await interaction.response.send_modal(
            MessageModal("Personalizar Mensaje de Bienvenida", "custom_welcome_msg")
        )

    @ui.button(label="💭 Mensaje Despedida", style=discord.ButtonStyle.secondary, row=1)
    async def custom_leave(self, interaction, _):
        await interaction.response.send_modal(
            MessageModal("Personalizar Mensaje de Despedida", "custom_leave_msg")
        )

    @ui.button(label="📢 Canal Logs", style=discord.ButtonStyle.secondary, row=1)
    async def logs(self, interaction, _):
        await interaction.response.send_modal(
            IDModal("Configurar Canal de Logs", "log_channel")
        )

    @ui.button(label="🧪 Test", style=discord.ButtonStyle.success, row=2)
    async def test(self, interaction, _):
        await self.cog.send_welcome(interaction.user)
        await self.cog.send_leave(interaction.user)
        embed = discord.Embed(
            title="✧ Test Completado",
            description="🧪 Los sistemas de bienvenida y despedida han sido probados\n\n⊱ ────── ✧ ────── ⊰",
            color=EMBED_COLOR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="📊 Ver Config", style=discord.ButtonStyle.primary, row=2)
    async def view_config(self, interaction, _):
        data = load_config().get(str(interaction.guild.id), {})
        
        welcome_ch = f"<#{data['welcome_channel']}>" if data.get('welcome_channel') else "No configurado"
        leave_ch = f"<#{data['leave_channel']}>" if data.get('leave_channel') else "No configurado"
        auto_role = f"<@&{data['auto_role']}>" if data.get('auto_role') else "No configurado"
        log_ch = f"<#{data['log_channel']}>" if data.get('log_channel') else "No configurado"
        
        embed = discord.Embed(
            title="🌸 Configuración Actual",
            description="⊱ ────── {.⋅ estado del sistema ⋅.} ────── ⊰",
            color=EMBED_COLOR
        )
        embed.add_field(name="🌸 Canal Bienvenida", value=welcome_ch, inline=False)
        embed.add_field(name="🥀 Canal Despedida", value=leave_ch, inline=False)
        embed.add_field(name="🎀 Auto-Rol", value=auto_role, inline=False)
        embed.add_field(name="📢 Canal Logs", value=log_ch, inline=False)
        embed.set_footer(text=f"Servidor: {interaction.guild.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="❌ Reset", style=discord.ButtonStyle.danger, row=2)
    async def reset(self, interaction, _):
        data = load_config()
        data.pop(str(interaction.guild.id), None)
        save_config(data)
        
        embed = discord.Embed(
            title="✧ Reset Completo",
            description="❌ Toda la configuración ha sido eliminada\n\n⊱ ────── ✧ ────── ⊰",
            color=EMBED_DARK
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ──────────────────────────────
# COG MEJORADO
# ──────────────────────────────

class Canales(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    async def log_event(self, guild, event_type, member):
        """Registra eventos en el canal de logs"""
        config = load_config().get(str(guild.id), {})
        log_channel_id = config.get("log_channel")
        
        if not log_channel_id:
            return
        
        channel = guild.get_channel(log_channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title=f"📋 Log: {event_type}",
            color=EMBED_COLOR if event_type == "Ingreso" else EMBED_DARK
        )
        embed.add_field(name="Usuario", value=f"{member.mention} ({member.id})", inline=False)
        embed.add_field(name="Hora", value=datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC'), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Total miembros: {guild.member_count}")
        
        await channel.send(embed=embed)

    async def send_welcome(self, member: discord.Member):
        config = load_config().get(str(member.guild.id), {})
        channel_id = config.get("welcome_channel")
        role_id = config.get("auto_role")
        custom_msg = config.get("custom_welcome_msg")

        # Auto-rol
        if role_id:
            role = member.guild.get_role(role_id)
            if role and member.guild.me.guild_permissions.manage_roles:
                try:
                    await member.add_roles(role, reason="🌸 Auto-Rol Bienvenida")
                except:
                    pass

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        banner = await generate_banner(member, "welcome")
        file = discord.File(banner, filename="welcome.png")

        # Mensaje personalizado o por defecto
        if custom_msg:
            description = custom_msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
        else:
            description = (
                f"✧ **{member.mention}** ha llegado a la oscuridad\n\n"
                "╰┈➤ **Lee las normas** para no perderte\n"
                "╰┈➤ **Preséntate** con la comunidad\n"
                "╰┈➤ **Disfruta la noche** eterna 🌙\n\n"
                "⊱ ────── {.⋅ Que florezcas aquí ⋅.} ────── ⊰"
            )

        embed = discord.Embed(
            title="╭┈──────── ⊱ 🌸 ⊰ ────────┈╮",
            description=description,
            color=EMBED_COLOR
        )
        embed.set_image(url="attachment://welcome.png")
        embed.set_footer(
            text=f"{member.guild.name} • {datetime.utcnow().strftime('%d/%m/%Y')}",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        await channel.send(embed=embed, file=file)
        await self.log_event(member.guild, "Ingreso", member)

    async def send_leave(self, member: discord.Member):
        config = load_config().get(str(member.guild.id), {})
        channel_id = config.get("leave_channel")
        custom_msg = config.get("custom_leave_msg")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        banner = await generate_banner(member, "leave")
        file = discord.File(banner, filename="leave.png")

        # Mensaje personalizado o por defecto
        if custom_msg:
            description = custom_msg.replace("{user}", member.name).replace("{server}", member.guild.name)
        else:
            description = (
                "╭┈──────── ⊱ 🥀 ⊰ ────────┈╮\n"
                f"𝑮𝒐𝒐𝒅𝒃𝒚𝒆, **{member.name}**…\n"
                "╰┈──────── ⊱ 🌑 ⊰ ────────┈╯\n\n"
                "✧.* Que la noche te acompañe siempre\n"
                f"Un alma menos en {member.guild.name}"
            )

        embed = discord.Embed(
            description=description,
            color=EMBED_DARK
        )
        embed.set_image(url="attachment://leave.png")
        embed.set_footer(text=f"Miembros restantes: {member.guild.member_count}")

        await channel.send(embed=embed, file=file)
        await self.log_event(member.guild, "Salida", member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_welcome(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_leave(member)

    @commands.command(name="panel-c")
    @commands.has_permissions(administrator=True)
    async def panelw(self, ctx):
        """Panel de control para bienvenidas y despedidas"""
        embed = discord.Embed(
            title="🌸 Panel de Bienvenidas & Despedidas",
            description=(
                "⊱ ────── {.⋅ configuración estética ⋅.} ────── ⊰\n\n"
                "**Características:**\n"
                "🌸 Mensajes de bienvenida personalizados\n"
                "🥀 Despedidas elegantes con banners\n"
                "🎀 Sistema de auto-roles\n"
                "📢 Logs de eventos\n"
                "✧ Banners dinámicos y únicos\n\n"
                "⊱ ────── ✧ ────── ⊰"
            ),
            color=EMBED_COLOR
        )
        embed.set_footer(text="Dark Coquette System • by your server")
        
        await ctx.send(embed=embed, view=PanelView(self))

    @commands.command(name="stats")
    @commands.has_permissions(manage_guild=True)
    async def stats(self, ctx):
        """Estadísticas del servidor"""
        guild = ctx.guild
        
        # Contadores
        total = guild.member_count
        bots = len([m for m in guild.members if m.bot])
        humans = total - bots
        online = len([m for m in guild.members if m.status != discord.Status.offline])
        
        embed = discord.Embed(
            title=f"📊 Estadísticas de {guild.name}",
            description="⊱ ────── {.⋅ datos del servidor ⋅.} ────── ⊰",
            color=EMBED_COLOR
        )
        embed.add_field(name="👥 Total Miembros", value=f"```{total}```", inline=True)
        embed.add_field(name="✨ Humanos", value=f"```{humans}```", inline=True)
        embed.add_field(name="🤖 Bots", value=f"```{bots}```", inline=True)
        embed.add_field(name="🟢 En Línea", value=f"```{online}```", inline=True)
        embed.add_field(name="📅 Creado", value=f"```{guild.created_at.strftime('%d/%m/%Y')}```", inline=True)
        embed.add_field(name="👑 Owner", value=f"```{guild.owner}```", inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text="🌸 Dark Coquette Stats")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Canales(bot))