import discord
from discord.ext import commands
from discord import ui
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import asyncio

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.glass_image_builder import GlassImageBuilder

# ════════════════════════════════════════════════════════════════
# 🎨 CONFIGURACIÓN GLOBAL
# ════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "titulo": "PANEL DE SUGERENCIAS",
    "subtitulo": "Comparte tu feedback con la comunidad",
    "mensaje_central": "Tu opinión nos importa\nAyudanos a mejorar",
    "pie_pagina": "Sistema automático de sugerencias • Tu voz cuenta",
    "emoji_like": "👍",
    "emoji_dislike": "👎",
    "color_principal": 0xE6E6FA,
    "color_exito": 0x5CFF9D,
    "color_error": 0xFF5C5C,
    "color_warning": 0xFFD700,
}

TEMAS_PREDEFINIDOS = {
    "pastel": {
        "color_principal": 0xFFB6C1,
        "color_exito": 0xFFDAB9,
        "color_error": 0xFF6B9D,
        "color_warning": 0xFFE5B4
    },
    "dark": {
        "color_principal": 0x1a1a2e,
        "color_exito": 0x00d4ff,
        "color_error": 0xff006e,
        "color_warning": 0xffc300
    },
    "neon": {
        "color_principal": 0x00d9ff,
        "color_exito": 0x39ff14,
        "color_error": 0xff006e,
        "color_warning": 0xffff00
    },
    "vintage": {
        "color_principal": 0xAA7939,
        "color_exito": 0xC4B5A0,
        "color_error": 0x8B4513,
        "color_warning": 0xDEB887
    },
    "oceano": {
        "color_principal": 0x0A4D68,
        "color_exito": 0x088395,
        "color_error": 0xE63946,
        "color_warning": 0xF4D58D
    },
    "bosque": {
        "color_principal": 0x1B4332,
        "color_exito": 0x52B788,
        "color_error": 0xD62828,
        "color_warning": 0xF77F00
    }
}

async def setup(bot):
    await bot.add_cog(Sugerencias(bot))

# ════════════════════════════════════════════════════════════════
# 🎮 MODALES Y VISTAS
# ════════════════════════════════════════════════════════════════

class SugerenciaModal(ui.Modal, title="📝 Nueva Sugerencia"):
    """Modal avanzado para enviar sugerencias"""
    
    categoria = ui.TextInput(
        label="📂 Categoría",
        placeholder="Bot / Servidor / Feature / Evento / Otro",
        required=True,
        max_length=30
    )
    
    sugerencia = ui.TextInput(
        label="💡 Tu Sugerencia",
        placeholder="Describe tu idea detalladamente...",
        required=True,
        max_length=500
    )
    
    detalles = ui.TextInput(
        label="📋 Detalles Adicionales",
        placeholder="Información extra, ejemplos, beneficios...",
        required=False,
        max_length=500
    )
    
    prioridad = ui.TextInput(
        label="⚡ Prioridad (Baja/Media/Alta)",
        placeholder="Media",
        required=False,
        max_length=10
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await self.cog.process_suggestion(
                interaction, 
                self.categoria.value, 
                self.sugerencia.value, 
                self.detalles.value or "Sin detalles adicionales",
                self.prioridad.value or "Media"
            )
        except:
            try:
                colors = self.cog.get_colors(interaction.guild.id)
                embed = discord.Embed(
                    title="❌ Error",
                    description="Hubo un problema al procesar tu sugerencia",
                    color=colors.get("color_error", 0xFF5C5C)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass

class PersonalizacionTextoModal(ui.Modal, title="📝 Personalizar Textos"):
    """Modal para personalizar textos del panel"""
    
    titulo = ui.TextInput(
        label="Título Principal",
        placeholder="PANEL DE SUGERENCIAS",
        required=False,
        max_length=50
    )
    
    subtitulo = ui.TextInput(
        label="Subtítulo",
        placeholder="Comparte tu feedback con la comunidad",
        required=False,
        max_length=100
    )
    
    mensaje_central = ui.TextInput(
        label="Mensaje Central",
        placeholder="Tu opinión nos importa",
        required=False,
        max_length=150
    )
    
    pie_pagina = ui.TextInput(
        label="Pie de Página",
        placeholder="Sistema automático de sugerencias",
        required=False,
        max_length=100
    )
    
    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            new_config = {
                "titulo": self.titulo.value or DEFAULT_CONFIG["titulo"],
                "subtitulo": self.subtitulo.value or DEFAULT_CONFIG["subtitulo"],
                "mensaje_central": self.mensaje_central.value or DEFAULT_CONFIG["mensaje_central"],
                "pie_pagina": self.pie_pagina.value or DEFAULT_CONFIG["pie_pagina"],
            }
            
            await self.cog.save_personalization(self.guild_id, new_config)
            
            colors = self.cog.get_colors(self.guild_id)
            embed = discord.Embed(
                title="✅ Textos Actualizados",
                description="Los cambios se aplicarán inmediatamente",
                color=colors.get("color_exito", 0x5CFF9D)
            )
            
            for key, value in new_config.items():
                embed.add_field(name=key.replace("_", " ").title(), value=f"`{value}`", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            try:
                colors = self.cog.get_colors(self.guild_id)
                embed = discord.Embed(
                    title="❌ Error",
                    description="No se pudieron guardar los cambios",
                    color=colors.get("color_error", 0xFF5C5C)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass

class PersonalizacionColorModal(ui.Modal, title="🎨 Personalizar Colores"):
    """Modal para personalizar colores"""
    
    color_principal = ui.TextInput(
        label="Color Principal (Hex sin #)",
        placeholder="E6E6FA",
        required=False,
        max_length=6
    )
    
    color_exito = ui.TextInput(
        label="Color Éxito (Hex)",
        placeholder="5CFF9D",
        required=False,
        max_length=6
    )
    
    color_error = ui.TextInput(
        label="Color Error (Hex)",
        placeholder="FF5C5C",
        required=False,
        max_length=6
    )
    
    color_warning = ui.TextInput(
        label="Color Advertencia (Hex)",
        placeholder="FFD700",
        required=False,
        max_length=6
    )
    
    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            colors = {}
            for field in [self.color_principal, self.color_exito, self.color_error, self.color_warning]:
                if field.value:
                    try:
                        key = field.label.split('(')[0].strip().lower().replace(' ', '_')
                        colors[key] = int(field.value, 16)
                    except:
                        pass
            
            if colors:
                await self.cog.save_colors(self.guild_id, colors)
            
            current_colors = self.cog.get_colors(self.guild_id)
            embed = discord.Embed(
                title="🎨 Colores Actualizados",
                description="Los colores se aplicarán inmediatamente",
                color=current_colors.get("color_exito", 0x5CFF9D)
            )
            
            for key, value in colors.items():
                embed.add_field(name=f"#{key}", value=f"`#{hex(value)[2:].upper()}`", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            try:
                colors = self.cog.get_colors(self.guild_id)
                embed = discord.Embed(
                    title="❌ Error",
                    description="Colores inválidos",
                    color=colors.get("color_error", 0xFF5C5C)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass

class PersonalizacionView(ui.View):
    """Vista de personalización"""
    
    def __init__(self, cog, guild_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
    
    @ui.button(label="Textos", style=discord.ButtonStyle.primary, emoji="📝")
    async def textos(self, interaction: discord.Interaction, button: ui.Button):
        modal = PersonalizacionTextoModal(self.cog, self.guild_id)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Colores", style=discord.ButtonStyle.success, emoji="🎨")
    async def colores(self, interaction: discord.Interaction, button: ui.Button):
        modal = PersonalizacionColorModal(self.cog, self.guild_id)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Pastel", style=discord.ButtonStyle.secondary, emoji="🎀")
    async def pastel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.save_colors(self.guild_id, TEMAS_PREDEFINIDOS["pastel"])
        embed = discord.Embed(title="✅ Tema Pastel Aplicado", color=TEMAS_PREDEFINIDOS["pastel"]["color_principal"])
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @ui.button(label="Dark", style=discord.ButtonStyle.danger, emoji="🌙")
    async def dark(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.save_colors(self.guild_id, TEMAS_PREDEFINIDOS["dark"])
        embed = discord.Embed(title="✅ Tema Dark Aplicado", color=TEMAS_PREDEFINIDOS["dark"]["color_principal"])
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @ui.button(label="Neon", style=discord.ButtonStyle.primary, emoji="⚡")
    async def neon(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.save_colors(self.guild_id, TEMAS_PREDEFINIDOS["neon"])
        embed = discord.Embed(title="✅ Tema Neon Aplicado", color=TEMAS_PREDEFINIDOS["neon"]["color_principal"])
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @ui.button(label="Océano", style=discord.ButtonStyle.primary, emoji="🌊")
    async def oceano(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.save_colors(self.guild_id, TEMAS_PREDEFINIDOS["oceano"])
        embed = discord.Embed(title="✅ Tema Océano Aplicado", color=TEMAS_PREDEFINIDOS["oceano"]["color_principal"])
        await interaction.followup.send(embed=embed, ephemeral=True)

class SugerenciasView(ui.View):
    """Vista del panel de sugerencias"""
    
    def __init__(self, cog, guild_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
    
    @ui.button(label="💡 Enviar Sugerencia", style=discord.ButtonStyle.primary, emoji="✨")
    async def suggest(self, interaction: discord.Interaction, button: ui.Button):
        try:
            modal = SugerenciaModal(self.cog)
            await interaction.response.send_modal(modal)
        except:
            colors = self.cog.get_colors(self.guild_id)
            embed = discord.Embed(
                title="❌ Error",
                description="No se pudo abrir el formulario",
                color=colors.get("color_error", 0xFF5C5C)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# ════════════════════════════════════════════════════════════════
# 💡 CLASE PRINCIPAL
# ════════════════════════════════════════════════════════════════

class Sugerencias(commands.Cog):
    """💡 Sistema Premium de Sugerencias con Personalización Total"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.glass_builder = GlassImageBuilder()
    
    def get_config(self, guild_id: int) -> dict:
        """Obtener configuración del servidor"""
        if "sugerencias" not in self.config:
            self.config["sugerencias"] = {}
        return self.config["sugerencias"].get(str(guild_id), {})
    
    def save_guild_config(self, guild_id: int, config: dict):
        """Guardar configuración del servidor"""
        if "sugerencias" not in self.config:
            self.config["sugerencias"] = {}
        self.config["sugerencias"][str(guild_id)] = config
        self.bot.save_config(self.config)
    
    async def save_personalization(self, guild_id: int, custom_config: dict):
        """Guardar personalización"""
        config = self.get_config(guild_id)
        if "personalization" not in config:
            config["personalization"] = {}
        config["personalization"].update(custom_config)
        self.save_guild_config(guild_id, config)
    
    async def save_colors(self, guild_id: int, colors: dict):
        """Guardar colores"""
        config = self.get_config(guild_id)
        if "colors" not in config:
            config["colors"] = {}
        config["colors"].update(colors)
        self.save_guild_config(guild_id, config)
    
    def get_personalization(self, guild_id: int) -> dict:
        """Obtener personalización con fallback"""
        config = self.get_config(guild_id)
        custom = config.get("personalization", {})
        
        return {
            "titulo": custom.get("titulo", DEFAULT_CONFIG["titulo"]),
            "subtitulo": custom.get("subtitulo", DEFAULT_CONFIG["subtitulo"]),
            "mensaje_central": custom.get("mensaje_central", DEFAULT_CONFIG["mensaje_central"]),
            "pie_pagina": custom.get("pie_pagina", DEFAULT_CONFIG["pie_pagina"]),
            "emoji_like": custom.get("emoji_like", DEFAULT_CONFIG["emoji_like"]),
            "emoji_dislike": custom.get("emoji_dislike", DEFAULT_CONFIG["emoji_dislike"]),
        }
    
    def get_colors(self, guild_id: int) -> dict:
        """Obtener colores con fallback"""
        config = self.get_config(guild_id)
        custom = config.get("colors", {})
        
        return {
            "color_principal": custom.get("color_principal", DEFAULT_CONFIG["color_principal"]),
            "color_exito": custom.get("color_exito", DEFAULT_CONFIG["color_exito"]),
            "color_error": custom.get("color_error", DEFAULT_CONFIG["color_error"]),
            "color_warning": custom.get("color_warning", DEFAULT_CONFIG["color_warning"]),
        }
    
    async def process_suggestion(
        self, 
        interaction: discord.Interaction, 
        categoria: str, 
        sugerencia: str, 
        detalles: str,
        prioridad: str = "Media"
    ):
        """Procesar sugerencia"""
        try:
            config = self.get_config(interaction.guild.id)
            
            if not config.get("channel_id"):
                colors = self.get_colors(interaction.guild.id)
                embed = discord.Embed(
                    title="⚠️ No Configurado",
                    description="El admin debe usar `-sugerencias-canal <#canal>` primero",
                    color=colors["color_warning"]
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            channel = self.bot.get_channel(config.get("channel_id"))
            if not channel:
                colors = self.get_colors(interaction.guild.id)
                embed = discord.Embed(
                    title="❌ Canal Eliminado",
                    description="El canal de sugerencias fue eliminado",
                    color=colors["color_error"]
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            prioridad = prioridad.capitalize()
            if prioridad not in ["Baja", "Media", "Alta"]:
                prioridad = "Media"
            
            emoji_prioridad = {"Baja": "🟢", "Media": "🟡", "Alta": "🔴"}.get(prioridad, "🟡")
            
            custom = self.get_personalization(interaction.guild.id)
            colors = self.get_colors(interaction.guild.id)
            
            sugg_id = len(self.config.get("suggestions", {})) + 1
            
            embed = discord.Embed(
                title=f"💡 {categoria.upper()}",
                description=sugerencia,
                color=colors["color_principal"],
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📋 Detalles", value=detalles, inline=False)
            embed.add_field(name="👤 Autor", value=interaction.user.mention, inline=True)
            embed.add_field(name=f"{emoji_prioridad} Prioridad", value=f"`{prioridad}`", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{sugg_id}`", inline=True)
            embed.add_field(name="👍", value=f"`0`", inline=True)
            embed.add_field(name="👎", value=f"`0`", inline=True)
            embed.add_field(name="⏮️ Estado", value="`En Revisión`", inline=True)
            
            embed.set_footer(text=custom["pie_pagina"])
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            msg = await channel.send(embed=embed)
            
            if "suggestions" not in self.config:
                self.config["suggestions"] = {}
            
            self.config["suggestions"][str(sugg_id)] = {
                "id": sugg_id,
                "guild_id": interaction.guild.id,
                "author_id": interaction.user.id,
                "categoria": categoria,
                "texto": sugerencia,
                "detalles": detalles,
                "prioridad": prioridad,
                "votos": {"positivos": 0, "negativos": 0},
                "fecha": datetime.now().isoformat(),
                "mensaje_id": msg.id,
                "canal_id": channel.id
            }
            
            self.bot.save_config(self.config)
            
            embed_respuesta = discord.Embed(
                title="✅ Sugerencia Enviada",
                description=f"Tu sugerencia ha sido registrada (ID: `{sugg_id}`)",
                color=colors["color_exito"]
            )
            
            await interaction.followup.send(embed=embed_respuesta, ephemeral=True)
        
        except:
            try:
                colors = self.get_colors(interaction.guild.id)
                embed = discord.Embed(
                    title="❌ Error",
                    description="Hubo un problema al procesar la sugerencia",
                    color=colors["color_error"]
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass
    
    # ════════════════════════════════════════════════════════════════
    # 📋 COMANDOS
    # ════════════════════════════════════════════════════════════════
    
    @commands.command(name="sugerencias-canal")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Establecer canal de sugerencias"""
        
        config = self.get_config(ctx.guild.id)
        config["channel_id"] = channel.id
        self.save_guild_config(ctx.guild.id, config)
        
        colors = self.get_colors(ctx.guild.id)
        embed = discord.Embed(
            title="✅ Canal Configurado",
            description=f"Las sugerencias irán a {channel.mention}",
            color=colors["color_exito"]
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="sugerencias-panel")
    @commands.has_permissions(administrator=True)
    async def show_panel(self, ctx):
        """Mostrar panel de sugerencias"""
        
        config = self.get_config(ctx.guild.id)
        if not config.get("channel_id"):
            colors = self.get_colors(ctx.guild.id)
            embed = discord.Embed(
                title="⚠️ No Configurado",
                description="Usa `-sugerencias-canal <#canal>` primero",
                color=colors["color_warning"]
            )
            return await ctx.send(embed=embed)
        
        custom = self.get_personalization(ctx.guild.id)
        colors = self.get_colors(ctx.guild.id)
        
        async with ctx.typing():
            panel_file = None
            try:
                panel_data = {
                    "titulo": custom['titulo'],
                    "subtitulo": custom['subtitulo'],
                    "mensaje_central": custom['mensaje_central'],
                    "pie_pagina": custom['pie_pagina'],
                    "color_principal": colors["color_principal"],
                    "color_exito": colors["color_exito"],
                    "emoji_like": custom['emoji_like'],
                    "emoji_dislike": custom['emoji_dislike'],
                }
                panel_img = self.glass_builder.create_suggestion_panel(panel_data)
                panel_file = discord.File(panel_img, filename="panel.png")
            except:
                pass
            
            embed = discord.Embed(
                title=f"💡 {custom['titulo']}",
                description=custom['subtitulo'],
                color=colors["color_principal"]
            )
            
            if panel_file:
                embed.set_image(url="attachment://panel.png")
            else:
                embed.add_field(
                    name="📝 Cómo Participar",
                    value="1️⃣ Haz clic en el botón\n2️⃣ Completa el formulario\n3️⃣ ¡La comunidad vota!",
                    inline=False
                )
            
            embed.add_field(
                name="📋 Pasos",
                value=f"1️⃣ Envía tu sugerencia\n2️⃣ La comunidad opina\n3️⃣ Se implementa",
                inline=False
            )
            
            embed.set_footer(text=custom['pie_pagina'])
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            
            view = SugerenciasView(self, ctx.guild.id)
            if panel_file:
                await ctx.send(embed=embed, file=panel_file, view=view)
            else:
                await ctx.send(embed=embed, view=view)
    
    @commands.command(name="sugerencias-personalizar")
    @commands.has_permissions(administrator=True)
    async def personalize(self, ctx):
        """Panel de personalización"""
        
        colors = self.get_colors(ctx.guild.id)
        
        embed = discord.Embed(
            title="🎨 Panel de Personalización",
            description="Personaliza tu sistema de sugerencias",
            color=colors["color_principal"]
        )
        
        embed.add_field(name="📝 Textos", value="Títulos y subtítulos", inline=True)
        embed.add_field(name="🎨 Colores", value="Personaliza colores", inline=True)
        embed.add_field(name="🎭 Temas", value="Pastel • Dark • Neon • Océano", inline=False)
        
        await ctx.send(embed=embed, view=PersonalizacionView(self, ctx.guild.id), ephemeral=True)
    
    @commands.command(name="sugerencias-stats")
    async def stats(self, ctx):
        """Estadísticas de sugerencias"""
        
        suggestions = self.config.get("suggestions", {})
        guild_sugg = [v for v in suggestions.values() if v.get('guild_id') == ctx.guild.id]
        
        colors = self.get_colors(ctx.guild.id)
        
        embed = discord.Embed(
            title="📊 Estadísticas",
            color=colors["color_principal"],
            timestamp=datetime.now()
        )
        
        if not guild_sugg:
            embed.description = "No hay sugerencias registradas"
            return await ctx.send(embed=embed)
        
        total_pos = sum(s['votos']['positivos'] for s in guild_sugg)
        total_neg = sum(s['votos']['negativos'] for s in guild_sugg)
        
        embed.add_field(name="💡 Total", value=f"`{len(guild_sugg)}`", inline=True)
        embed.add_field(name="👍 Positivos", value=f"`{total_pos}`", inline=True)
        embed.add_field(name="👎 Negativos", value=f"`{total_neg}`", inline=True)
        
        cats = {}
        for s in guild_sugg:
            cat = s.get('categoria', 'Sin')
            cats[cat] = cats.get(cat, 0) + 1
        
        if cats:
            text = "\n".join([f"• **{k}**: `{v}`" for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True)[:5]])
            embed.add_field(name="📂 Categorías", value=text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="sugerencias-config")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Ver configuración"""
        
        config = self.get_config(ctx.guild.id)
        custom = self.get_personalization(ctx.guild.id)
        colors = self.get_colors(ctx.guild.id)
        
        if not config.get("channel_id"):
            embed = discord.Embed(title="⚠️ No Configurado", color=colors["color_warning"])
            return await ctx.send(embed=embed, ephemeral=True)
        
        channel = self.bot.get_channel(config.get("channel_id"))
        
        embed = discord.Embed(title="⚙️ Configuración", color=colors["color_principal"])
        embed.add_field(name="📢 Canal", value=channel.mention if channel else "❌ Eliminado", inline=False)
        embed.add_field(name="📝 Título", value=f"`{custom['titulo']}`", inline=False)
        
        suggestions = self.config.get("suggestions", {})
        total = len([v for v in suggestions.values() if v.get('guild_id') == ctx.guild.id])
        embed.add_field(name="💡 Total Sugerencias", value=f"`{total}`", inline=False)
        
        await ctx.send(embed=embed, ephemeral=True)

# ════════════════════════════════════════════════════════════════
# 📝 SECCIÓN EDITABLE - PERSONALIZA AQUÍ
# ════════════════════════════════════════════════════════════════

# 🎨 AGREGAR MÁS TEMAS:
# TEMAS_PREDEFINIDOS["tu_tema"] = {
#     "color_principal": 0x...,
#     "color_exito": 0x...,
#     "color_error": 0x...,
#     "color_warning": 0x...,
# }

# 📝 PERSONALIZAR TEXTOS PREDETERMINADOS:
# DEFAULT_CONFIG["titulo"] = "Tu título aquí"
# DEFAULT_CONFIG["subtitulo"] = "Tu subtítulo aquí"

# 💡 AGREGAR NUEVOS COMANDOS O FUNCIONALIDADES:
# - Extender la clase Sugerencias con más @commands.command()
# - Modificar process_suggestion() para cambiar lógica
# - Agregar reacciones con votos automáticos
# - Integrar con bases de datos externas
