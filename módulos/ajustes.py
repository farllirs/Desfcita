import discord
from discord.ext import commands, tasks
from discord import ui
import json
import os
import random
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import aiohttp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 TEMAS Y COLORES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THEMES = {
    'PINK': {'hex': 0xFFB6C1, 'rgb': (255, 182, 193), 'gradient': ((255, 182, 193), (147, 112, 219))},
    'GOLD': {'hex': 0xFFD700, 'rgb': (255, 215, 0), 'gradient': ((255, 215, 0), (255, 140, 0))},
    'PURPLE': {'hex': 0x9370DB, 'rgb': (147, 112, 219), 'gradient': ((147, 112, 219), (138, 43, 226))},
    'SKY': {'hex': 0x00BFFF, 'rgb': (0, 191, 255), 'gradient': ((0, 191, 255), (30, 144, 255))},
    'MINT': {'hex': 0x00FA9A, 'rgb': (0, 250, 154), 'gradient': ((0, 250, 154), (0, 206, 209))},
    'CORAL': {'hex': 0xFF7F50, 'rgb': (255, 127, 80), 'gradient': ((255, 127, 80), (255, 99, 71))},
    'VIOLET': {'hex': 0x8A2BE2, 'rgb': (138, 43, 226), 'gradient': ((138, 43, 226), (75, 0, 130))},
    'ROSE': {'hex': 0xFF007F, 'rgb': (255, 0, 127), 'gradient': ((255, 0, 127), (255, 105, 180))},
    'OCEAN': {'hex': 0x4ECDC4, 'rgb': (78, 205, 196), 'gradient': ((78, 205, 196), (44, 62, 80))},
    'SUNSET': {'hex': 0xFF6B6B, 'rgb': (255, 107, 107), 'gradient': ((255, 107, 107), (254, 202, 87))}
}

def get_theme(name: str) -> dict:
    return THEMES.get(name, THEMES['PINK'])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 GLASSMORPHISM GENERATOR (ESTILO iOS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class GlassCard:
    """Generador de tarjetas con efecto glassmorphism estilo iPhone"""
    
    FONTS_PATH = "fonts"
    
    @staticmethod
    def get_font(font_type: str, size: int):
        """Obtiene la fuente desde la carpeta fonts"""
        font_map = {
            "classic": "classic.ttf",
            "emoji": "emojis.ttf"
        }
        try:
            path = os.path.join(GlassCard.FONTS_PATH, font_map.get(font_type, "classic.ttf"))
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()
    
    @staticmethod
    def create_gradient(width: int, height: int, colors: tuple) -> Image.Image:
        """Crea un gradiente suave entre dos colores"""
        base = Image.new('RGB', (width, height), colors[0])
        top = Image.new('RGB', (width, height), colors[1])
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (y / height)))
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    @staticmethod
    def add_glass_effect(img: Image.Image, blur: int = 15, opacity: int = 180) -> Image.Image:
        """Aplica efecto de vidrio esmerilado"""
        blurred = img.filter(ImageFilter.GaussianBlur(blur))
        glass = Image.new('RGBA', img.size, (255, 255, 255, opacity))
        blurred = blurred.convert('RGBA')
        return Image.alpha_composite(blurred, glass)
    
    @staticmethod
    def add_particles(draw: ImageDraw, width: int, height: int, color: tuple, count: int = 20):
        """Añade partículas decorativas"""
        for _ in range(count):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(2, 8)
            alpha = random.randint(30, 80)
            draw.ellipse((x, y, x+size, y+size), fill=(*color, alpha))
    
    @staticmethod
    def circular_avatar(avatar: Image.Image, size: int) -> Image.Image:
        """Crea avatar circular con máscara"""
        avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(avatar, (0, 0), mask)
        return output
    
    @staticmethod
    async def fetch_avatar(url: str) -> Image.Image:
        """Descarga avatar de usuario"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return Image.open(BytesIO(await resp.read())).convert('RGBA')
    
    @staticmethod
    async def create_profile_card(member: discord.Member, data: dict, theme_name: str = 'PINK') -> BytesIO:
        """Genera tarjeta de perfil con glassmorphism mejorada"""
        width, height = 880, 450
        theme = get_theme(theme_name)
        
        bg = GlassCard.create_gradient(width, height, theme['gradient'])
        bg = GlassCard.add_glass_effect(bg)
        draw = ImageDraw.Draw(bg)
        
        GlassCard.add_particles(draw, width, height, theme['rgb'], 30)
        
        draw.rounded_rectangle([(20, 20), (width-20, height-20)], radius=30, fill=(255, 255, 255, 30))
        draw.rounded_rectangle([(15, 15), (width-15, height-15)], radius=35, outline=(*theme['rgb'], 180), width=3)
        
        font_title = GlassCard.get_font("classic", 40)
        font_main = GlassCard.get_font("classic", 28)
        font_small = GlassCard.get_font("classic", 20)
        font_mini = GlassCard.get_font("classic", 16)
        
        try:
            avatar = await GlassCard.fetch_avatar(str(member.display_avatar.url))
            avatar = GlassCard.circular_avatar(avatar, 150)
            
            glow = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse((0, 0, 180, 180), fill=(*theme['rgb'], 100))
            glow = glow.filter(ImageFilter.GaussianBlur(12))
            bg.paste(glow, (35, 45), glow)
            bg.paste(avatar, (50, 60), avatar)
            
            ring = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
            ring_draw = ImageDraw.Draw(ring)
            ring_draw.ellipse((0, 0, 160, 160), outline=(255, 255, 255, 220), width=4)
            ring_draw.ellipse((5, 5, 155, 155), outline=(*theme['rgb'], 150), width=2)
            bg.paste(ring, (45, 55), ring)
        except:
            draw.ellipse((50, 60, 200, 210), fill=(*theme['rgb'], 150))
        
        level = data.get("level", 1)
        xp = data.get("xp", 0)
        messages = data.get("messages", 0)
        streak = data.get("daily_streak", 0)
        needed = int(100 * (level ** 1.5) + 150 * level)
        progress = min(xp / needed, 1.0) if needed > 0 else 0
        
        draw.text((230, 50), member.display_name[:16], fill=(255, 255, 255), 
                 font=font_title, stroke_width=2, stroke_fill=(0, 0, 0))
        
        level_badge = Image.new('RGBA', (120, 35), (0, 0, 0, 0))
        badge_draw = ImageDraw.Draw(level_badge)
        badge_draw.rounded_rectangle([(0, 0), (120, 35)], radius=17, fill=(*theme['rgb'], 200))
        bg.paste(level_badge, (230, 95), level_badge)
        draw.text((290, 112), f"Nivel {level}", fill=(255, 255, 255), font=font_small, anchor='mm')
        
        if streak > 0:
            draw.text((360, 112), f"🔥 {streak}", fill=(255, 200, 100), font=font_small, anchor='lm')
        
        bar_x, bar_y, bar_w, bar_h = 230, 145, 600, 26
        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)],
            radius=13, fill=(255, 255, 255, 50), outline=(255, 255, 255, 120))
        if progress > 0:
            prog_w = max(26, int(bar_w * progress))
            draw.rounded_rectangle([(bar_x, bar_y), (bar_x + prog_w, bar_y + bar_h)],
                radius=13, fill=(*theme['rgb'], 230))
        draw.text((bar_x + bar_w//2, bar_y + bar_h//2), f"{xp:,} / {needed:,} XP", 
                 fill=(255, 255, 255), font=font_mini, anchor='mm')
        
        total_xp = xp + sum(int(100 * (l ** 1.5) + 150 * l) for l in range(1, level))
        stats = [
            ('💬', 'Mensajes', f'{messages:,}'),
            ('⭐', 'XP Total', f'{total_xp:,}'),
            ('🎯', 'Progreso', f'{int(progress * 100)}%'),
            ('📊', 'Nivel', f'{level}')
        ]
        box_w = 145
        for i, (emoji, label, value) in enumerate(stats):
            x = 230 + i * (box_w + 12)
            y = 190
            draw.rounded_rectangle([(x, y), (x + box_w, y + 85)], radius=15, fill=(255, 255, 255, 40))
            draw.text((x + 12, y + 10), emoji, font=font_small, fill=(255, 255, 255))
            draw.text((x + 38, y + 10), label, font=font_mini, fill=(255, 255, 255, 180))
            draw.text((x + 12, y + 45), value, font=font_main, fill=(255, 255, 255))
        
        partner = data.get("partner")
        if partner:
            partner_box = Image.new('RGBA', (250, 35), (0, 0, 0, 0))
            ImageDraw.Draw(partner_box).rounded_rectangle([(0, 0), (250, 35)], radius=17, fill=(255, 255, 255, 50))
            bg.paste(partner_box, (230, 290), partner_box)
            draw.text((245, 307), f"💖 Vinculado", fill=(255, 255, 255), font=font_mini, anchor='lm')
        
        for lvl, info in sorted(Style.LEVEL_ROLES.items(), reverse=True):
            if level >= lvl:
                role_name = info["name"]
                draw.rounded_rectangle([(230, 340), (500, 375)], radius=17, fill=(255, 255, 255, 35))
                draw.text((245, 357), f"🏅 {role_name}", fill=(255, 255, 255, 220), font=font_small, anchor='lm')
                break
        
        draw.text((width - 40, height - 30), theme_name, fill=(255, 255, 255, 100), font=font_mini, anchor='rm')
        
        buffer = BytesIO()
        bg.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    async def create_leaderboard_card(users_data: list, bot, theme_name: str = 'GOLD') -> BytesIO:
        """Genera tarjeta de ranking top 10 mejorada"""
        width, height = 900, 680
        theme = get_theme(theme_name)
        
        bg = GlassCard.create_gradient(width, height, theme['gradient'])
        bg = GlassCard.add_glass_effect(bg, blur=20)
        draw = ImageDraw.Draw(bg)
        
        GlassCard.add_particles(draw, width, height, theme['rgb'], 30)
        
        draw.rounded_rectangle([(20, 20), (width-20, height-20)], radius=30, fill=(255, 255, 255, 25))
        draw.rounded_rectangle([(15, 15), (width-15, height-15)], radius=35, outline=(*theme['rgb'], 180), width=3)
        
        font_title = GlassCard.get_font("classic", 48)
        font_entry = GlassCard.get_font("classic", 26)
        font_small = GlassCard.get_font("classic", 20)
        
        draw.text((width // 2, 45), "🏆 TOP RANKING", fill=(255, 255, 255), 
                 font=font_title, anchor="mt", stroke_width=3, stroke_fill=(0, 0, 0))
        
        medals = ["🥇", "🥈", "🥉"]
        y = 110
        
        for i, (uid, data) in enumerate(users_data[:10], 1):
            u = bot.get_user(int(uid))
            name = u.name[:14] if u else f"Usuario"
            level = data.get("level", 1)
            xp = data.get("xp", 0)
            medal = medals[i-1] if i <= 3 else f"#{i}"
            
            entry_color = (*theme['rgb'], 80) if i <= 3 else (255, 255, 255, 50)
            draw.rounded_rectangle([(50, y), (width - 50, y + 50)], radius=15, fill=entry_color)
            
            draw.text((80, y + 25), medal, font=font_entry, fill=(255, 255, 255), anchor='lm')
            draw.text((130, y + 25), name, font=font_entry, fill=(255, 255, 255), anchor='lm')
            draw.text((width - 100, y + 25), f"Lv.{level}", font=font_entry, fill=(*theme['rgb'], 255), anchor='rm')
            draw.text((width - 180, y + 25), f"{xp} XP", font=font_small, fill=(255, 255, 255, 180), anchor='rm')
            
            y += 55
        
        buffer = BytesIO()
        bg.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    async def create_config_panel(guild_name: str, settings: dict, theme_name: str = 'PURPLE') -> BytesIO:
        """Genera banner para el panel de configuración"""
        width, height = 800, 520
        theme = get_theme(theme_name)
        
        bg = GlassCard.create_gradient(width, height, theme['gradient'])
        bg = GlassCard.add_glass_effect(bg, blur=18)
        draw = ImageDraw.Draw(bg)
        
        GlassCard.add_particles(draw, width, height, theme['rgb'], 20)
        
        draw.rounded_rectangle([(20, 20), (width-20, height-20)], radius=30, fill=(255, 255, 255, 25))
        draw.rounded_rectangle([(15, 15), (width-15, height-15)], radius=35, outline=(*theme['rgb'], 180), width=3)
        
        font_title = GlassCard.get_font("classic", 36)
        font_label = GlassCard.get_font("classic", 22)
        font_value = GlassCard.get_font("classic", 20)
        
        draw.text((width//2, 45), "⚙️ PANEL DE CONFIGURACIÓN", fill=(255, 255, 255), 
                 font=font_title, anchor='mt', stroke_width=2, stroke_fill=(0, 0, 0))
        draw.text((width//2, 85), guild_name[:25], fill=(255, 255, 255, 180), font=font_value, anchor='mt')
        
        roles_status = '✅ Activo' if settings.get('role_rewards', True) else '❌ Inactivo'
        options = [
            ('💫', 'Sistema XP', '✅ Activo' if settings['levels_enabled'] else '❌ Inactivo'),
            ('🔥', 'Multiplicador', f'x{settings.get("xp_multiplier", 1.0)}'),
            ('⏱️', 'Cooldown', f'{settings.get("xp_cooldown", 45)}s'),
            ('🔔', 'Notificaciones', settings.get('levelup_notifs', 'channel').upper()),
            ('🎭', 'Auto-Roles', roles_status),
            ('🎨', 'Tema', settings.get('theme', 'PINK')),
            ('📊', 'XP Mínimo', str(settings.get('xp_min', 15))),
            ('📈', 'XP Máximo', str(settings.get('xp_max', 25)))
        ]
        
        box_w, box_h = 230, 75
        start_x, start_y = 50, 120
        
        for i, (emoji, label, value) in enumerate(options):
            col, row = i % 3, i // 3
            x = start_x + col * (box_w + 20)
            y = start_y + row * (box_h + 15)
            
            draw.rounded_rectangle([(x, y), (x + box_w, y + box_h)], radius=15, fill=(255, 255, 255, 45))
            draw.text((x + 15, y + 12), f'{emoji} {label}', font=font_value, fill=(255, 255, 255, 200))
            draw.text((x + 15, y + 42), value, font=font_label, fill=(255, 255, 255))
        
        draw.text((width//2, height - 45), 'Usa los botones para configurar', 
                 font=font_value, fill=(255, 255, 255, 150), anchor='mt')
        
        buffer = BytesIO()
        bg.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    async def create_oracle_card(message: str) -> BytesIO:
        """Tarjeta del oráculo místico"""
        width, height = 700, 400
        
        # Gradiente púrpura-azul
        bg = GlassCard.create_gradient(width, height, 
            ((138, 43, 226), (75, 0, 130)))
        bg = GlassCard.add_glass_effect(bg, blur=18)
        draw = ImageDraw.Draw(bg)
        
        font_title = GlassCard.get_font("classic", 52)
        font_text = GlassCard.get_font("classic", 32)
        
        # Título
        draw.text((width // 2, 60), "🔮 ORÁCULO ESTELAR", 
                 fill=(255, 215, 0), font=font_title, 
                 anchor="mt", stroke_width=2, stroke_fill=(138, 43, 226))
        
        # Panel central glass
        draw.rounded_rectangle(
            [(50, 140), (width - 50, height - 80)],
            radius=25, fill=(255, 255, 255, 140), 
            outline=(255, 255, 255, 200), width=3
        )
        
        # Mensaje (multi-línea si es necesario)
        lines = []
        words = message.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if len(test_line) > 30:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line.strip())
        
        y_text = 180
        for line in lines[:3]:
            draw.text((width // 2, y_text), line, fill=(50, 50, 50), 
                     font=font_text, anchor="mt")
            y_text += 45
        
        # Borde exterior
        draw.rounded_rectangle(
            [(10, 10), (width - 10, height - 10)],
            radius=30, outline=(255, 215, 0, 220), width=4
        )
        
        buffer = BytesIO()
        bg.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 GESTIÓN DE DATOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DataManager:
    PATH = 'data/nivel.json'
    
    @staticmethod
    def load() -> Dict[str, Any]:
        if not os.path.exists('data'): 
            os.makedirs('data')
        if os.path.exists(DataManager.PATH):
            try:
                with open(DataManager.PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: 
                pass
        return {
            "users": {}, 
            "settings": {
                "levels_enabled": True, 
                "xp_cooldown": 45, 
                "xp_multiplier": 1.0, 
                "xp_min": 15, 
                "xp_max": 25,
                "levelup_notifs": "channel", 
                "role_rewards": True,
                "theme": "PINK"
            }
        }

    @staticmethod
    def save(data: Dict[str, Any]):
        if not os.path.exists('data'): 
            os.makedirs('data')
        with open(DataManager.PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 CONFIGURACIÓN VISUAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Style:
    C_PINK = 0xFFB6C1
    C_GOLD = 0xFFD700
    C_PURPLE = 0x9370DB
    C_DARK = 0x2B2D31
    
    LEVEL_ROLES = {
        1:   {"name": "✧ Polvo Estelar", "color": 0xFFFFFF},
        10:  {"name": "🌸 Brote Mágico", "color": 0xFFB6C1},
        25:  {"name": "🌙 Luz de Luna", "color": 0x9370DB},
        50:  {"name": "🌌 Nebulosa", "color": 0x8A2BE2},
        75:  {"name": "💎 Elite Stellar", "color": 0x00BFFF},
        100: {"name": "👑 Soberana Cósmica", "color": 0xFFD700}
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️ PANEL DE CONFIGURACIÓN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ConfigPanel(ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog

    async def update_panel(self, interaction: discord.Interaction):
        """Actualiza el panel con nuevo banner"""
        theme = self.cog.data["settings"].get("theme", "PINK")
        banner = await GlassCard.create_config_panel(
            interaction.guild.name, self.cog.data["settings"], theme
        )
        file = discord.File(banner, filename='panel.png')
        embed = discord.Embed(color=get_theme(theme)['hex'])
        embed.set_image(url='attachment://panel.png')
        await interaction.response.edit_message(attachments=[file], embed=embed, view=self)

    @ui.button(label="XP", style=discord.ButtonStyle.primary, emoji="💫", row=0)
    async def toggle_xp(self, interaction: discord.Interaction, button: ui.Button):
        self.cog.data["settings"]["levels_enabled"] = not self.cog.data["settings"]["levels_enabled"]
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="Multi", style=discord.ButtonStyle.primary, emoji="🔥", row=0)
    async def toggle_mult(self, interaction: discord.Interaction, button: ui.Button):
        current = self.cog.data["settings"].get("xp_multiplier", 1.0)
        options = [1.0, 1.5, 2.0, 2.5, 3.0]
        idx = (options.index(current) + 1) % len(options) if current in options else 0
        self.cog.data["settings"]["xp_multiplier"] = options[idx]
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="Cooldown", style=discord.ButtonStyle.primary, emoji="⏱️", row=0)
    async def toggle_cooldown(self, interaction: discord.Interaction, button: ui.Button):
        current = self.cog.data["settings"]["xp_cooldown"]
        options = [15, 30, 45, 60, 90]
        idx = (options.index(current) + 1) % len(options) if current in options else 0
        self.cog.data["settings"]["xp_cooldown"] = options[idx]
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="Notifs", style=discord.ButtonStyle.secondary, emoji="🔔", row=0)
    async def toggle_notifs(self, interaction: discord.Interaction, button: ui.Button):
        options = ["channel", "dm", "off"]
        current = self.cog.data["settings"]["levelup_notifs"]
        idx = (options.index(current) + 1) % len(options) if current in options else 0
        self.cog.data["settings"]["levelup_notifs"] = options[idx]
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="Roles", style=discord.ButtonStyle.secondary, emoji="🎭", row=1)
    async def toggle_roles(self, interaction: discord.Interaction, button: ui.Button):
        self.cog.data["settings"]["role_rewards"] = not self.cog.data["settings"].get("role_rewards", True)
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="Tema", style=discord.ButtonStyle.secondary, emoji="🎨", row=1)
    async def change_theme(self, interaction: discord.Interaction, button: ui.Button):
        themes = list(THEMES.keys())
        current = self.cog.data["settings"].get("theme", "PINK")
        idx = (themes.index(current) + 1) % len(themes) if current in themes else 0
        self.cog.data["settings"]["theme"] = themes[idx]
        DataManager.save(self.cog.data)
        await self.update_panel(interaction)

    @ui.button(label="XP Range", style=discord.ButtonStyle.secondary, emoji="📊", row=1)
    async def xp_range(self, interaction: discord.Interaction, button: ui.Button):
        modal = ui.Modal(title='Configurar Rango de XP')
        modal.add_item(ui.TextInput(label='XP Mínimo por mensaje', placeholder='15', 
                                    default=str(self.cog.data["settings"].get("xp_min", 15)), max_length=3))
        modal.add_item(ui.TextInput(label='XP Máximo por mensaje', placeholder='25', 
                                    default=str(self.cog.data["settings"].get("xp_max", 25)), max_length=3))
        
        async def on_submit(it: discord.Interaction):
            try:
                xp_min = int(modal.children[0].value)
                xp_max = int(modal.children[1].value)
                if xp_min > 0 and xp_max >= xp_min:
                    self.cog.data["settings"]["xp_min"] = xp_min
                    self.cog.data["settings"]["xp_max"] = xp_max
                    DataManager.save(self.cog.data)
                    await self.update_panel(it)
                else:
                    await it.response.send_message('`❌` Valores inválidos', ephemeral=True)
            except:
                await it.response.send_message('`❌` Ingresa números válidos', ephemeral=True)
        
        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)

    @ui.button(label="Ver Roles", style=discord.ButtonStyle.success, emoji="⭐", row=1)
    async def view_roles(self, interaction: discord.Interaction, button: ui.Button):
        roles_text = '\n'.join([f'`Lv.{lvl:3}` → {info["name"]}' for lvl, info in sorted(Style.LEVEL_ROLES.items())])
        theme = self.cog.data["settings"].get("theme", "PINK")
        embed = discord.Embed(
            title='🎭 Roles por Nivel',
            description=f"Roles que se asignan automáticamente:\n\n{roles_text}",
            color=get_theme(theme)['hex']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Reset All", style=discord.ButtonStyle.danger, emoji="🗑️", row=2)
    async def reset_all(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message('`❌` Solo administradores', ephemeral=True)
        
        confirm_view = ui.View(timeout=30)
        
        async def confirm_callback(it: discord.Interaction):
            self.cog.data["users"] = {}
            DataManager.save(self.cog.data)
            await it.response.send_message('`✅` Todos los datos de usuarios han sido eliminados', ephemeral=True)
        
        async def cancel_callback(it: discord.Interaction):
            await it.response.send_message('`❌` Cancelado', ephemeral=True)
        
        confirm_btn = ui.Button(label='Confirmar', style=discord.ButtonStyle.danger, emoji='⚠️')
        cancel_btn = ui.Button(label='Cancelar', style=discord.ButtonStyle.secondary)
        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        await interaction.response.send_message(
            '⚠️ **¿Estás seguro?** Esto eliminará TODOS los datos de niveles.',
            view=confirm_view, ephemeral=True
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COG PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AjustesPro(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = DataManager.load()
        self.xp_cooldowns = {}
        self.auto_save.start()

    def cog_unload(self):
        DataManager.save(self.data)
        self.auto_save.cancel()

    @tasks.loop(minutes=5.0)
    async def auto_save(self):
        DataManager.save(self.data)

    def get_user(self, user_id: int) -> Dict[str, Any]:
        uid = str(user_id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "xp": 0, 
                "level": 1, 
                "messages": 0, 
                "partner": None
            }
            DataManager.save(self.data)
        return self.data["users"][uid]

    async def sync_roles(self, member: discord.Member, level: int):
        """Asigna roles automáticamente según nivel"""
        if not self.data["settings"].get("role_rewards", True): 
            return
        if not member.guild.me.guild_permissions.manage_roles: 
            return
        
        highest = None
        for lvl, info in sorted(Style.LEVEL_ROLES.items(), reverse=True):
            if level >= lvl:
                highest = info
                break
        
        if not highest: 
            return
        
        role = discord.utils.get(member.guild.roles, name=highest["name"])
        if not role:
            try: 
                role = await member.guild.create_role(
                    name=highest["name"], 
                    color=discord.Color(highest["color"])
                )
            except: 
                return
        
        if role not in member.roles:
            try: 
                await member.add_roles(role)
            except: 
                pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Sistema de XP automático"""
        if message.author.bot or not message.guild or message.content.startswith('-'): 
            return
        
        settings = self.data["settings"]
        if not settings["levels_enabled"]: 
            return
        
        uid = message.author.id
        now = datetime.now()
        
        # Cooldown
        if uid in self.xp_cooldowns:
            delta = (now - self.xp_cooldowns[uid]).total_seconds()
            if delta < settings["xp_cooldown"]: 
                return
        
        self.xp_cooldowns[uid] = now
        user = self.get_user(uid)
        
        # Ganar XP
        xp_gain = random.randint(settings.get("xp_min", 15), settings.get("xp_max", 25))
        user["xp"] += int(xp_gain * settings.get("xp_multiplier", 1.0))
        user["messages"] += 1
        
        # Verificar subida de nivel
        needed = int(100 * (user["level"] ** 1.5) + 150 * user["level"])
        if user["xp"] >= needed:
            user["level"] += 1
            user["xp"] -= needed
            
            # Notificación
            if settings["levelup_notifs"] == "channel":
                embed = discord.Embed(
                    title="✨ ¡NIVEL AUMENTADO!",
                    description=f"¡Felicidades {message.author.mention}!\nAhora eres **Nivel {user['level']}** 🌟",
                    color=Style.C_GOLD
                )
                await message.channel.send(embed=embed, delete_after=15)
            elif settings["levelup_notifs"] == "dm":
                try: 
                    await message.author.send(
                        f"✨ ¡Subiste al nivel {user['level']} en **{message.guild.name}**!"
                    )
                except: 
                    pass
            
            await self.sync_roles(message.author, user["level"])
        
        DataManager.save(self.data)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 COMANDOS DE NIVELES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="perfil", aliases=["p", "me"])
    async def profile(self, ctx, member: Optional[discord.Member] = None):
        """Ver perfil de nivel (Alias: p, me)"""
        member = member or ctx.author
        user = self.get_user(member.id)
        theme = self.data["settings"].get("theme", "PINK")
        
        async with ctx.typing():
            img_buffer = await GlassCard.create_profile_card(member, user, theme)
            file = discord.File(img_buffer, filename="perfil.png")
            await ctx.send(file=file)

    @commands.command(name="ranking", aliases=["top", "lb"])
    async def leaderboard(self, ctx):
        """Ver ranking del servidor (Alias: top, lb)"""
        sorted_users = sorted(
            self.data["users"].items(), 
            key=lambda x: (x[1]["level"], x[1]["xp"]), 
            reverse=True
        )[:10]
        theme = self.data["settings"].get("theme", "GOLD")
        
        async with ctx.typing():
            img_buffer = await GlassCard.create_leaderboard_card(sorted_users, self.bot, theme)
            file = discord.File(img_buffer, filename="ranking.png")
            await ctx.send(file=file)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔮 COMANDOS MÍSTICOS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="oraculo", aliases=["suerte", "fortuna"])
    async def oracle(self, ctx):
        """Consulta el oráculo (Alias: suerte, fortuna)"""
        fortunes = [
            "Las estrellas brillan a tu favor hoy ✨",
            "Un encuentro inesperado traerá alegría 🌸",
            "Confía en tu intuición, te guiará bien 🔮",
            "El universo te envía un abrazo cálido 💖",
            "Grandes cambios se aproximan 🌟"
        ]
        
        message = random.choice(fortunes)
        img_buffer = await GlassCard.create_oracle_card(message)
        file = discord.File(img_buffer, filename="oraculo.png")
        
        await ctx.send(file=file)

    @commands.command(name="afinidad", aliases=["af", "love"])
    async def affinity(self, ctx, member: discord.Member):
        """Calcula compatibilidad (Alias: af, love)"""
        percent = random.randint(0, 100)
        bar = "💖" * (percent // 10) + "🖤" * (10 - (percent // 10))
        
        embed = discord.Embed(
            title="💖 AFINIDAD",
            description=(
                f"**{ctx.author.mention} x {member.mention}**\n\n"
                f"**Compatibilidad:** `{percent}%`\n"
                f"{bar}\n\n"
                f"{'¡Destinados por las estrellas! ✨' if percent > 80 else 'Hay una chispa aquí 🌸'}"
            ),
            color=Style.C_PINK
        )
        await ctx.send(embed=embed)

    @commands.command(name="vincular", aliases=["link", "pareja"])
    async def link_partner(self, ctx, member: discord.Member):
        """Crear vínculo especial (Alias: link, pareja)"""
        user = self.get_user(ctx.author.id)
        theme = self.data["settings"].get("theme", "PINK")
        
        if user["partner"]:
            return await ctx.send(f"❌ Ya tienes un vínculo con <@{user['partner']}>")
        
        if member.id == ctx.author.id:
            return await ctx.send("❌ No puedes vincularte contigo mismo")
        
        user["partner"] = member.id
        DataManager.save(self.data)
        
        embed = discord.Embed(
            title="✨ VÍNCULO CREADO",
            description=(
                f"{ctx.author.mention} ↔️ {member.mention}\n\n"
                f"¡Que su luz nunca se apague! 💖"
            ),
            color=get_theme(theme)['hex']
        )
        await ctx.send(embed=embed)

    @commands.command(name="desvincular", aliases=["unlink", "romper"])
    async def unlink_partner(self, ctx):
        """Eliminar vínculo especial (Alias: unlink, romper)"""
        user = self.get_user(ctx.author.id)
        
        if not user["partner"]:
            return await ctx.send("❌ No tienes ningún vínculo activo")
        
        partner_id = user["partner"]
        user["partner"] = None
        DataManager.save(self.data)
        
        await ctx.send(f"💔 Vínculo con <@{partner_id}> eliminado")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ⚙️ COMANDOS DE ADMINISTRACIÓN
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="panel-aj", aliases=["cfg", "ajustes", "config"])
    @commands.has_permissions(administrator=True)
    async def config_panel(self, ctx):
        """Panel de configuración (Alias: cfg, ajustes)"""
        theme = self.data["settings"].get("theme", "PURPLE")
        
        async with ctx.typing():
            banner = await GlassCard.create_config_panel(ctx.guild.name, self.data["settings"], theme)
            file = discord.File(banner, filename='panel.png')
            embed = discord.Embed(color=get_theme(theme)['hex'])
            embed.set_image(url='attachment://panel.png')
            await ctx.send(file=file, embed=embed, view=ConfigPanel(self))

    @commands.command(name="dar-xp", aliases=["addxp", "givexp"])
    @commands.has_permissions(administrator=True)
    async def give_xp(self, ctx, member: discord.Member, amount: int):
        """Dar XP a un usuario (Alias: addxp, givexp)"""
        user = self.get_user(member.id)
        user["xp"] += amount
        DataManager.save(self.data)
        
        embed = discord.Embed(
            title="✨ XP OTORGADO",
            description=f"Se han dado **{amount} XP** a {member.mention}",
            color=Style.C_GOLD
        )
        await ctx.send(embed=embed)

    @commands.command(name="dar-nivel", aliases=["addlvl", "setlvl"])
    @commands.has_permissions(administrator=True)
    async def set_level(self, ctx, member: discord.Member, level: int):
        """Establecer nivel de usuario (Alias: addlvl, setlvl)"""
        user = self.get_user(member.id)
        user["level"] = max(1, level)
        user["xp"] = 0
        DataManager.save(self.data)
        
        await self.sync_roles(member, user["level"])
        
        embed = discord.Embed(
            title="⭐ NIVEL MODIFICADO",
            description=f"{member.mention} ahora es **Nivel {user['level']}**",
            color=Style.C_PURPLE
        )
        await ctx.send(embed=embed)

    @commands.command(name="reset", aliases=["exterminar", "Limpiar"])
    @commands.has_permissions(administrator=True)
    async def reset_user(self, ctx, member: discord.Member):
        """Resetear progreso de usuario (Alias: borrar, limpiar)"""
        uid = str(member.id)
        if uid in self.data["users"]:
            del self.data["users"][uid]
            DataManager.save(self.data)
            await ctx.send(f"✅ Progreso de {member.mention} reseteado")
        else:
            await ctx.send(f"❌ {member.mention} no tiene datos guardados")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📋 COMANDOS DE INFORMACIÓN
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="Ayuda", aliases=["Help", "H"])
    async def help_panel(self, ctx):
        """Panel de ayuda (Alias: help, h)"""
        embed = discord.Embed(
            title="🌸 PANEL DE AYUDA",
            description="Sistema de niveles con glassmorphism",
            color=Style.C_PINK
        )
        
        embed.add_field(
            name="📊 Niveles",
            value=(
                "`perfil` / `p` / `me` - Ver tu perfil\n"
                "`ranking` / `top` / `lb` - Ver ranking\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔮 Místicos",
            value=(
                "`oraculo` / `suerte` - Consultar oráculo\n"
                "`afinidad` / `af` - Calcular compatibilidad\n"
                "`vincular` / `link` - Crear vínculo especial\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Admin",
            value=(
                "`config` / `cfg` - Panel de configuración\n"
                "`dar-xp` / `addxp` - Dar XP a usuario\n"
                "`dar-nivel` / `setlvl` - Cambiar nivel\n"
                "`reset` / `borrar` - Resetear usuario\n"
            ),
            inline=False
        )
        
        embed.set_footer(text="Sistema Glassmorphism v3.0")
        await ctx.send(embed=embed)

    @commands.command(name="informacion", aliases=["estadisticas"])
    async def server_stats(self, ctx):
        """Ver estadísticas del servidor (Alias: estadisticas, info)"""
        total_users = len(self.data["users"])
        total_messages = sum(u.get("messages", 0) for u in self.data["users"].values())
        avg_level = sum(u.get("level", 1) for u in self.data["users"].values()) / max(total_users, 1)
        
        # Usuario con más nivel
        top_user = max(
            self.data["users"].items(), 
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            default=(None, {"level": 0})
        )
        
        embed = discord.Embed(
            title="📊 ESTADÍSTICAS DEL SERVIDOR",
            description="Datos del sistema de niveles",
            color=Style.C_PURPLE
        )
        
        embed.add_field(
            name="General",
            value=(
                f"**Usuarios Activos:** `{total_users}`\n"
                f"**Mensajes Totales:** `{total_messages:,}`\n"
                f"**Nivel Promedio:** `{avg_level:.1f}`"
            ),
            inline=False
        )
        
        if top_user[0]:
            top_member = self.bot.get_user(int(top_user[0]))
            top_name = top_member.name if top_member else "Desconocido"
            embed.add_field(
                name="🏆 Usuario Top",
                value=f"**{top_name}** - Nivel {top_user[1]['level']}",
                inline=False
            )
        
        settings = self.data["settings"]
        embed.add_field(
            name="⚙️ Configuración Actual",
            value=(
                f"**Sistema:** {'✅ Activo' if settings['levels_enabled'] else '❌ Inactivo'}\n"
                f"**Multiplicador:** `x{settings['xp_multiplier']}`\n"
                f"**Cooldown:** `{settings['xp_cooldown']}s`"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎁 COMANDOS EXTRA/DIVERTIDOS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="daily", aliases=["diario", "regalo"])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily_reward(self, ctx):
        """Recompensa diaria de XP con sistema de racha (Alias: diario, regalo)"""
        user = self.get_user(ctx.author.id)
        theme = self.data["settings"].get("theme", "GOLD")
        
        streak = user.get("daily_streak", 0) + 1
        user["daily_streak"] = streak
        
        base_bonus = random.randint(50, 100)
        streak_bonus = min(streak * 5, 50)
        total_bonus = base_bonus + streak_bonus
        
        user["xp"] += total_bonus
        user["last_daily"] = datetime.now().isoformat()
        DataManager.save(self.data)
        
        embed = discord.Embed(
            title="🎁 RECOMPENSA DIARIA",
            description=(
                f"¡{ctx.author.mention} ha recibido su regalo!\n\n"
                f"**+{base_bonus} XP** base\n"
                f"**+{streak_bonus} XP** racha\n"
                f"━━━━━━━━━━━━\n"
                f"**Total: +{total_bonus} XP** ✨\n\n"
                f"🔥 **Racha:** {streak} días consecutivos"
            ),
            color=get_theme(theme)['hex']
        )
        await ctx.send(embed=embed)

    @daily_reward.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            hours = int(error.retry_after // 3600)
            minutes = int((error.retry_after % 3600) // 60)
            await ctx.send(f"⏰ Ya reclamaste tu recompensa. Vuelve en **{hours}h {minutes}m**")

    @commands.command(name="transfer", aliases=["transferir", "enviar"])
    async def transfer_xp(self, ctx, member: discord.Member, amount: int):
        """Transferir XP a otro usuario (Alias: transferir, enviar)"""
        if amount <= 0:
            return await ctx.send("❌ La cantidad debe ser positiva")
        
        sender = self.get_user(ctx.author.id)
        if sender["xp"] < amount:
            return await ctx.send(f"❌ No tienes suficiente XP. Tienes: {sender['xp']}")
        
        receiver = self.get_user(member.id)
        sender["xp"] -= amount
        receiver["xp"] += amount
        DataManager.save(self.data)
        
        embed = discord.Embed(
            title="💸 TRANSFERENCIA EXITOSA",
            description=(
                f"{ctx.author.mention} ➔ {member.mention}\n\n"
                f"**Cantidad:** `{amount} XP` ✨"
            ),
            color=Style.C_PINK
        )
        await ctx.send(embed=embed)

    @commands.command(name="regalar-nivel", aliases=["gift", "regalar"])
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def gift_level(self, ctx, member: discord.Member):
        """Regalar 1 nivel a alguien (1 vez por semana) (Alias: gift, regalar)"""
        receiver = self.get_user(member.id)
        receiver["level"] += 1
        DataManager.save(self.data)
        
        await self.sync_roles(member, receiver["level"])
        
        embed = discord.Embed(
            title="🎁 NIVEL REGALADO",
            description=(
                f"{ctx.author.mention} ha regalado un nivel a {member.mention}!\n\n"
                f"✨ Ahora es **Nivel {receiver['level']}**\n\n"
                f"¡Qué generoso gesto! 💖"
            ),
            color=Style.C_GOLD
        )
        await ctx.send(embed=embed)

    @gift_level.error
    async def gift_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            days = int(error.retry_after // 86400)
            hours = int((error.retry_after % 86400) // 3600)
            await ctx.send(
                f"⏰ Solo puedes regalar un nivel por semana.\n"
                f"Vuelve en **{days}d {hours}h**"
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎲 COMANDOS DE JUEGOS/MINIJUEGOS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @commands.command(name="ruleta", aliases=["spin", "apostar"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def roulette(self, ctx):
        """Ruleta de XP (Alias: spin, apostar)"""
        user = self.get_user(ctx.author.id)
        
        outcomes = [
            {"xp": 100, "msg": "¡JACKPOT! 🎰", "chance": 5},
            {"xp": 50, "msg": "¡Genial! 🌟", "chance": 15},
            {"xp": 25, "msg": "¡Bien! ✨", "chance": 30},
            {"xp": 0, "msg": "Casi... 😅", "chance": 30},
            {"xp": -20, "msg": "Mala suerte 💔", "chance": 20}
        ]
        
        # Elegir resultado basado en probabilidades
        roll = random.randint(1, 100)
        cumulative = 0
        result = outcomes[-1]
        
        for outcome in outcomes:
            cumulative += outcome["chance"]
            if roll <= cumulative:
                result = outcome
                break
        
        user["xp"] = max(0, user["xp"] + result["xp"])
        DataManager.save(self.data)
        
        embed = discord.Embed(
            title="🎰 RULETA DE XP",
            description=(
                f"**{result['msg']}**\n\n"
                f"{'Ganaste' if result['xp'] > 0 else 'Perdiste' if result['xp'] < 0 else 'Empataste'}: "
                f"`{abs(result['xp'])} XP`\n\n"
                f"Tu XP actual: `{user['xp']}`"
            ),
            color=Style.C_GOLD if result['xp'] > 0 else Style.C_DARK
        )
        await ctx.send(embed=embed)

    @roulette.error
    async def roulette_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            await ctx.send(f"⏰ Ruleta en cooldown. Vuelve en **{minutes} minutos**")

    @commands.command(name="adivina", aliases=["guess", "numero"])
    async def guess_game(self, ctx):
        """Juego de adivinar número (Alias: guess, numero)"""
        number = random.randint(1, 10)
        
        embed = discord.Embed(
            title="🎲 ADIVINA EL NÚMERO",
            description="Adivina un número del **1 al 10**\nTienes 3 intentos. ¡Gana 30 XP!",
            color=Style.C_PURPLE
        )
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
        
        for attempt in range(3):
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                guess = int(msg.content)
                
                if guess == number:
                    user = self.get_user(ctx.author.id)
                    user["xp"] += 30
                    DataManager.save(self.data)
                    
                    await ctx.send(
                        f"🎉 ¡CORRECTO! Era **{number}**\n"
                        f"Ganaste **30 XP** ✨"
                    )
                    return
                elif guess < number:
                    await ctx.send(f"📈 Más alto... ({3 - attempt - 1} intentos)")
                else:
                    await ctx.send(f"📉 Más bajo... ({3 - attempt - 1} intentos)")
                    
            except asyncio.TimeoutError:
                await ctx.send("⏰ Se acabó el tiempo")
                return
        
        await ctx.send(f"😔 Perdiste. El número era **{number}**")
async def setup(bot: commands.Bot):
    await bot.add_cog(AjustesPro(bot))
