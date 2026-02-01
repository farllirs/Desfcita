import discord
from discord.ext import commands
from discord import ui
import time
import datetime
import os
import inspect

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 CONFIGURACIÓN PERSONALIZABLE - EDITA AQUÍ
# ══════════════════════════════════════════════════════════════════════════════

class HelpConfig:
    # 🖼️ Banner del Panel
    BANNER_URL = "https://cdn.discordapp.com/attachments/1461871586037731338/1463891484053868692/ecd5ddbfb1b63a821eb67c9bf9c15793.gif"
    
    # 🎨 Colores por Categoría
    COLORS = {
        "inicio": 0xFFB6C1,      # Rosa pastel
        "confesiones": 0xFFB6C1, # Rosa pastel
        "soporte": 0x87CEEB,     # Azul cielo
        "tickets": 0x87CEEB,     # Azul cielo
        "países": 0x98FB98,      # Verde menta
        "paises": 0x98FB98,      # Verde menta
        "moderación": 0xF08080,  # Rojo suave
        "moderacion": 0xF08080,  # Rojo suave
        "administración": 0xFFD700, # Dorado
        "administracion": 0xFFD700, # Dorado
        "gestión": 0x9B59B6,     # Púrpura
        "gestion": 0x9B59B6,     # Púrpura
        "ajustes": 0x3498DB,     # Azul
        "anuncios": 0xE67E22,    # Naranja
        "canales": 0x1ABC9C,     # Turquesa
        "niveles": 0xF1C40F,     # Amarillo
        "tiktokers": 0xE91E63,   # Rosa fuerte
        "default": 0xFFB6C1      # Rosa por defecto
    }
    
    # 🎭 Emojis por Categoría
    EMOJIS = {
        "inicio": "🏠",
        "confesiones": "🌸",
        "soporte": "🎫",
        "tickets": "🎫",
        "países": "🌍",
        "paises": "🌍",
        "moderación": "🛡️",
        "moderacion": "🛡️",
        "administración": "⚙️",
        "administracion": "⚙️",
        "gestión": "👑",
        "gestion": "👑",
        "ajustes": "🔧",
        "anuncios": "📢",
        "eventos": "📅",
        "canales": "📺",
        "niveles": "⭐",
        "tiktokers": "🎬",
        "default": "📖"
    }
    
    # 📝 Textos del Panel
    TITULO_PRINCIPAL = "🌸 ✨ CENTRO DE AYUDA PREMIUM ✨ 🌸"
    DESCRIPCION_INICIO = (
        "╭─────────────────────────────╮\n"
        "│ Bienvenido al Centro de Ayuda   │\n"
        "│ Usa el menú para explorar        │\n"
        "│ todas las funcionalidades        │\n"
        "╰─────────────────────────────╯"
    )

# ══════════════════════════════════════════════════════════════════════════════
# 🔍 SISTEMA DE AUTO-DETECCIÓN DE COMANDOS
# ══════════════════════════════════════════════════════════════════════════════

class CommandDetector:
    """Detecta automáticamente todos los comandos de los módulos"""
    
    def __init__(self, bot):
        self.bot = bot
        self.commands_by_module = {}
    
    def scan_modules(self):
        """Escanea todos los módulos y organiza sus comandos"""
        self.commands_by_module.clear()
        
        # Obtener todos los cogs del bot
        for cog_name, cog in self.bot.cogs.items():
            # Ignorar el cog de ayuda
            if cog_name.lower() in ['helpcog', 'ayuda', 'help']:
                continue
            
            # Obtener comandos del cog
            cog_commands = cog.get_commands()
            
            if cog_commands:
                module_name = self._get_module_name(cog_name)
                
                if module_name not in self.commands_by_module:
                    self.commands_by_module[module_name] = []
                
                for cmd in cog_commands:
                    cmd_info = {
                        'name': cmd.name,
                        'description': cmd.help or cmd.short_doc or "Sin descripción",
                        'signature': cmd.signature,
                        'cog': cog_name
                    }
                    self.commands_by_module[module_name].append(cmd_info)
        
        return self.commands_by_module
    
    def _get_module_name(self, cog_name):
        """Usa el nombre exacto del módulo para independencia total"""
        # Sin mapping: cada cog es un módulo independiente
        return cog_name

# ══════════════════════════════════════════════════════════════════════════════
# 📋 GENERADOR DE PÁGINAS DINÁMICAS
# ══════════════════════════════════════════════════════════════════════════════

class PageGenerator:
    """Genera páginas de ayuda dinámicamente"""
    
    def __init__(self, bot, commands_by_module):
        self.bot = bot
        self.commands_by_module = commands_by_module
        self.pages = {}
    
    def generate_pages(self):
        """Genera todas las páginas de ayuda"""
        self.pages = {}
        
        # Página de inicio
        self.pages["inicio"] = self._create_home_page()
        
        # Páginas por módulo
        for module_name, commands in self.commands_by_module.items():
            self.pages[module_name.lower()] = self._create_module_page(module_name, commands)
        
        return self.pages
    
    def _create_home_page(self):
        """Crea la página de inicio"""
        total_commands = sum(len(cmds) for cmds in self.commands_by_module.values())
        total_modules = len(self.commands_by_module)
        
        description = (
            f"{HelpConfig.DESCRIPCION_INICIO}\n\n"
            f"**📊 Estadísticas del Sistema**\n"
            f"```\n"
            f"Módulos: {total_modules}\n"
            f"Comandos: {total_commands}\n"
            f"Prefix: {self.bot.command_prefix}\n"
            f"```\n"
            f"**💡 Tip:** Selecciona una categoría del menú para ver sus comandos."
        )
        
        return {
            "title": HelpConfig.TITULO_PRINCIPAL,
            "description": description,
            "color": HelpConfig.COLORS["inicio"],
            "show_stats": True,
            "fields": []
        }
    
    def _create_module_page(self, module_name, commands):
        """Crea una página para un módulo específico con comandos en fila"""
        emoji = HelpConfig.EMOJIS.get(module_name.lower(), HelpConfig.EMOJIS["default"])
        
        # Lista de comandos en fila (horizontal)
        commands_list = []
        for cmd in commands:
            cmd_text = f"`{self.bot.command_prefix}{cmd['name']}"
            if cmd['signature']:
                cmd_text += f" {cmd['signature']}"
            cmd_text += "`"
            commands_list.append(cmd_text)
        
        # Unir en una fila separada por " | "
        commands_in_row = " | ".join(commands_list)
        
        description = (
            f"**{emoji} Módulo: {module_name.upper()}**\n\n"
            f"**Comandos disponibles:**\n{commands_in_row}\n\n"
            f"**Descripciones:**\n"
        )
        
        # Agregar descripciones en fields para claridad
        fields = []
        for cmd in commands:
            desc = cmd['description']
            if len(desc) > 100:
                desc = desc[:97] + "..."
            fields.append({
                "name": f"🔸 `{self.bot.command_prefix}{cmd['name']}`",
                "value": f"```{desc}```",
                "inline": False
            })
        
        return {
            "title": f"{emoji} {module_name.upper()} - Catálogo",
            "description": description,
            "color": HelpConfig.COLORS.get(module_name.lower(), HelpConfig.COLORS["default"]),
            "show_stats": False,
            "fields": fields
        }

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 COMPONENTES UI
# ══════════════════════════════════════════════════════════════════════════════

class HelpSelect(ui.Select):
    """Selector de categorías del panel de ayuda"""
    
    def __init__(self, pages, bot):
        self.bot = bot
        self.pages = pages
        
        # Crear opciones dinámicamente
        options = [
            discord.SelectOption(
                label="Inicio",
                emoji=HelpConfig.EMOJIS["inicio"],
                description="Página principal",
                value="inicio"
            )
        ]
        
        # Agregar opciones por cada módulo
        for module_name in sorted(pages.keys()):
            if module_name == "inicio":
                continue
            
            emoji = HelpConfig.EMOJIS.get(module_name.lower(), HelpConfig.EMOJIS["default"])
            options.append(
                discord.SelectOption(
                    label=module_name.title(),
                    emoji=emoji,
                    description=f"Comandos de {module_name}",
                    value=module_name.lower()
                )
            )
        
        super().__init__(
            placeholder="✨ Selecciona una categoría...",
            options=options[:25],  # Discord limita a 25 opciones
            custom_id="help_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Maneja la selección de categoría"""
        selected = self.values[0].lower()
        page = self.pages.get(selected, self.pages["inicio"])
        
        embed = discord.Embed(
            title=page["title"],
            description=page["description"],
            color=page["color"],
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_thumbnail(url=HelpConfig.BANNER_URL)
        
        # Agregar fields si existen
        for field in page.get("fields", []):
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False)
            )
        
        # Agregar estadísticas si es la página de inicio
        if page.get("show_stats", False):
            start_time = getattr(self.bot, 'start_time', time.time())
            if isinstance(start_time, datetime.datetime):
                now = discord.utils.utcnow()
                if start_time.tzinfo is None:
                    now = now.replace(tzinfo=None)
                uptime_val = int((now - start_time).total_seconds())
            else:
                uptime_val = int(time.time() - start_time)
            hours = uptime_val // 3600
            minutes = (uptime_val % 3600) // 60
            
            embed.add_field(
                name="📊 Estado del Bot",
                value=(
                    f"```\n"
                    f"Ping:    {round(self.bot.latency * 1000)}ms\n"
                    f"Uptime:  {hours}h {minutes}m\n"
                    f"Servers: {len(self.bot.guilds)}\n"
                    f"```"
                ),
                inline=False
            )
        
        embed.set_footer(
            text=f"Solicitado por {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(ui.View):
    """Vista principal del panel de ayuda"""
    
    def __init__(self, bot, pages):
        super().__init__(timeout=180)
        self.bot = bot
        self.pages = pages
        self.add_item(HelpSelect(pages, bot))
    
    @ui.button(label="Actualizar", emoji="🔄", style=discord.ButtonStyle.secondary, custom_id="help_refresh")
    async def refresh_button(self, interaction: discord.Interaction, button: ui.Button):
        """Actualiza la detección de comandos"""
        await interaction.response.defer(ephemeral=True)
        
        # Re-escanear módulos
        detector = CommandDetector(self.bot)
        commands_by_module = detector.scan_modules()
        
        # Regenerar páginas
        generator = PageGenerator(self.bot, commands_by_module)
        new_pages = generator.generate_pages()
        
        # Actualizar vista
        self.pages = new_pages
        self.clear_items()
        self.add_item(HelpSelect(new_pages, self.bot))
        self.add_item(button)
        
        # Mensaje de confirmación
        refresh_embed = discord.Embed(
            title="✅ Sistema Actualizado",
            description=(
                f"Se han detectado:\n"
                f"```\n"
                f"Módulos:  {len(commands_by_module)}\n"
                f"Comandos: {sum(len(cmds) for cmds in commands_by_module.values())}\n"
                f"```"
            ),
            color=0x2ECC71
        )
        
        await interaction.followup.send(embed=refresh_embed, ephemeral=True)
    
    async def on_timeout(self):
        """Desactiva los botones al expirar"""
        for item in self.children:
            item.disabled = True

# ══════════════════════════════════════════════════════════════════════════════
# 🧠 COG PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class HelpCog(commands.Cog, name="Ayuda"):
    """Sistema de ayuda ultra-premium con auto-detección"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Guardar tiempo de inicio si no existe
        if not hasattr(self.bot, 'start_time'):
            self.bot.start_time = time.time()
        
        # Inicializar detector y generador
        self.detector = CommandDetector(bot)
        self.commands_cache = {}
        self.pages_cache = {}
        
        # Escanear comandos al inicio
        self.refresh_commands()
    
    def refresh_commands(self):
        """Refresca la cache de comandos"""
        self.commands_cache = self.detector.scan_modules()
        generator = PageGenerator(self.bot, self.commands_cache)
        self.pages_cache = generator.generate_pages()
    
    @commands.command(name="panel-ay")
    async def help_command(self, ctx):
        """Muestra el panel de ayuda interactivo"""
        
        # Refrescar comandos antes de mostrar
        self.refresh_commands()
        
        # Crear vista
        view = HelpView(self.bot, self.pages_cache)
        page = self.pages_cache["inicio"]
        
        # Crear embed inicial
        embed = discord.Embed(
            title=page["title"],
            description=page["description"],
            color=page["color"],
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_thumbnail(url=HelpConfig.BANNER_URL)
        
        # Agregar fields si existen
        for field in page.get("fields", []):
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False)
            )
        
        # Agregar estadísticas
        if page.get("show_stats", False):
            start_time = getattr(self.bot, 'start_time', time.time())
            if isinstance(start_time, datetime.datetime):
                now = discord.utils.utcnow()
                if start_time.tzinfo is None:
                    now = now.replace(tzinfo=None)
                uptime_val = int((now - start_time).total_seconds())
            else:
                uptime_val = int(time.time() - start_time)
            hours = uptime_val // 3600
            minutes = (uptime_val % 3600) // 60
            
            embed.add_field(
                name="📊 Estado del Bot",
                value=(
                    f"```\n"
                    f"Ping:    {round(self.bot.latency * 1000)}ms\n"
                    f"Uptime:  {hours}h {minutes}m\n"
                    f"Servers: {len(self.bot.guilds)}\n"
                    f"```"
                ),
                inline=False
            )
        
        embed.set_footer(
            text=f"Solicitado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="lista-comandos")
    async def comandos_list(self, ctx):
        """Lista todos los comandos disponibles"""
        
        self.refresh_commands()
        
        embed = discord.Embed(
            title="📚 Lista Completa de Comandos",
            description="Todos los comandos organizados por módulo:",
            color=0x9B59B6,
            timestamp=discord.utils.utcnow()
        )
        
        total = 0
        for module_name, commands in sorted(self.commands_cache.items()):
            emoji = HelpConfig.EMOJIS.get(module_name.lower(), "📖")
            cmds_text = ", ".join([f"`{cmd['name']}`" for cmd in commands[:5]])
            
            if len(commands) > 5:
                cmds_text += f" y {len(commands) - 5} más..."
            
            embed.add_field(
                name=f"{emoji} {module_name.title()} ({len(commands)})",
                value=cmds_text or "Sin comandos",
                inline=False
            )
            
            total += len(commands)
        
        embed.set_footer(text=f"Total: {total} comandos • Usa -centro-ayuda para más detalles")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="actualizar-ayuda")
    @commands.has_permissions(administrator=True)
    async def refresh_help(self, ctx):
        """Refresca manualmente el sistema de ayuda (Admin)"""
        
        loading = await ctx.send("🔄 Escaneando módulos...")
        
        # Refrescar
        self.refresh_commands()
        
        # Crear reporte
        embed = discord.Embed(
            title="✅ Sistema de Ayuda Actualizado",
            description="Se han escaneado todos los módulos del bot.",
            color=0x2ECC71,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="📊 Resumen",
            value=(
                f"```\n"
                f"Módulos:  {len(self.commands_cache)}\n"
                f"Comandos: {sum(len(cmds) for cmds in self.commands_cache.values())}\n"
                f"```"
            ),
            inline=False
        )
        
        # Listar módulos detectados
        modules_list = "\n".join([
            f"• {HelpConfig.EMOJIS.get(mod.lower(), '📖')} **{mod}** ({len(cmds)} cmds)"
            for mod, cmds in sorted(self.commands_cache.items())
        ])
        
        embed.add_field(
            name="📦 Módulos Detectados",
            value=modules_list or "Ninguno",
            inline=False
        )
        
        await loading.edit(content=None, embed=embed)

async def setup(bot):
    """Carga el cog"""
    # Remover comando help por defecto si existe
    if bot.get_command("help"):
        bot.remove_command("help")
    
    await bot.add_cog(HelpCog(bot))