import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
import os
import glob

# ══════════════════════════════════════════════════════════════════════════════
# 📢 MÓDULO DE NOVEDADES / UPDATES
# ══════════════════════════════════════════════════════════════════════════════

class UpdateSelectMenu(ui.Select):
    """Menú para seleccionar versión a enviar"""
    
    def __init__(self, cog, versions: list):
        self.cog = cog
        options = [
            discord.SelectOption(
                label=v.replace('-', '.').replace('version.', 'v'),
                value=v,
                description=f"Changelog de la versión {v.replace('-', '.').replace('version.', '')}",
                emoji="📋"
            ) for v in versions[:25]
        ]
        super().__init__(
            placeholder="📋 Selecciona una versión...",
            options=options,
            custom_id="update:version_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        version = self.values[0]
        await self.cog.send_update(interaction, version)


class UpdateView(ui.View):
    """Vista para el panel de novedades"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @ui.button(label='Enviar Última', style=discord.ButtonStyle.primary, emoji='🚀', custom_id='update:send_latest')
    async def send_latest(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message('`❌` Sin permisos', ephemeral=True)
        
        versions = self.cog.get_versions()
        if not versions:
            return await interaction.response.send_message('`❌` No hay versiones disponibles', ephemeral=True)
        
        await self.cog.send_update(interaction, versions[0])
    
    @ui.button(label='Ver Canal', style=discord.ButtonStyle.secondary, emoji='📺', custom_id='update:view_channel')
    async def view_channel(self, interaction: discord.Interaction, button: ui.Button):
        channel_id = self.cog.bot.config.get('updates_channel')
        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                await interaction.response.send_message(f'`📺` Canal de novedades: {channel.mention}', ephemeral=True)
            else:
                await interaction.response.send_message('`⚠️` Canal configurado pero no encontrado', ephemeral=True)
        else:
            await interaction.response.send_message('`⚠️` No hay canal configurado. Usa `-setcanal-updates #canal`', ephemeral=True)
    
    @ui.button(label='Refrescar', style=discord.ButtonStyle.secondary, emoji='🔃', custom_id='update:refresh')
    async def refresh(self, interaction: discord.Interaction, button: ui.Button):
        embed = self.cog.create_panel_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed)


class VersionSelectView(ui.View):
    """Vista con selector de versiones"""
    
    def __init__(self, cog, versions: list):
        super().__init__(timeout=120)
        self.add_item(UpdateSelectMenu(cog, versions))


class Novedades(commands.Cog):
    """Sistema de anuncios de actualizaciones"""
    
    def __init__(self, bot):
        self.bot = bot
        self.versions_folder = "."
    
    def get_versions(self) -> list:
        """Obtiene todas las versiones disponibles ordenadas"""
        files = glob.glob(os.path.join(self.versions_folder, "version-*.txt"))
        versions = []
        for f in files:
            name = os.path.basename(f).replace('.txt', '')
            versions.append(name)
        versions.sort(reverse=True, key=lambda x: [int(n) for n in x.replace('version-', '').split('-') if n.isdigit()])
        return versions
    
    def get_version_content(self, version: str) -> str:
        """Lee el contenido de una versión"""
        path = os.path.join(self.versions_folder, f"{version}.txt")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def create_panel_embed(self, guild: discord.Guild) -> discord.Embed:
        """Crea el embed del panel de novedades"""
        versions = self.get_versions()
        channel_id = self.bot.config.get('updates_channel')
        channel = guild.get_channel(channel_id) if channel_id else None
        
        embed = discord.Embed(
            title="📢 Panel de Novedades",
            description="Gestiona y envía actualizaciones del bot",
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📺 Canal Configurado",
            value=channel.mention if channel else "`No configurado`",
            inline=True
        )
        
        embed.add_field(
            name="📋 Versiones Disponibles",
            value=f"`{len(versions)}`",
            inline=True
        )
        
        if versions:
            latest = versions[0].replace('version-', 'v').replace('-', '.')
            embed.add_field(name="🚀 Última Versión", value=f"`{latest}`", inline=True)
            
            versions_list = '\n'.join([
                f"• `{v.replace('version-', 'v').replace('-', '.')}`" 
                for v in versions[:5]
            ])
            embed.add_field(name="📦 Versiones Recientes", value=versions_list, inline=False)
        
        embed.set_footer(text=f"{self.bot.BotConfig.BOT_EMOJI} {self.bot.BotConfig.BOT_NAME}")
        return embed
    
    async def send_update(self, interaction: discord.Interaction, version: str):
        """Envía una actualización al canal configurado"""
        channel_id = self.bot.config.get('updates_channel')
        
        if not channel_id:
            return await interaction.response.send_message(
                '`❌` No hay canal configurado. Usa `-setcanal-updates #canal`',
                ephemeral=True
            )
        
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            return await interaction.response.send_message(
                '`❌` El canal configurado no existe',
                ephemeral=True
            )
        
        content = self.get_version_content(version)
        if not content:
            return await interaction.response.send_message(
                f'`❌` No se encontró el archivo {version}.txt',
                ephemeral=True
            )
        
        version_display = version.replace('version-', 'v').replace('-', '.')
        
        embed = discord.Embed(
            title=f"🌸 ✨ ACTUALIZACIÓN {version_display.upper()} ✨ 🌸",
            description=content[:4000],
            color=0xFF69B4,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"{self.bot.BotConfig.BOT_EMOJI} {self.bot.BotConfig.BOT_NAME} • Actualización Oficial",
            icon_url=self.bot.user.display_avatar.url
        )
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            await channel.send(embed=embed)
            await interaction.followup.send(
                f'`✅` Actualización **{version_display}** enviada a {channel.mention}',
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send('`❌` No tengo permisos para enviar mensajes en ese canal', ephemeral=True)
    
    @commands.command(name="panel-updates", aliases=["panel-novedades", "updates"])
    @commands.has_permissions(administrator=True)
    async def panel_updates(self, ctx):
        """Muestra el panel de gestión de novedades"""
        embed = self.create_panel_embed(ctx.guild)
        view = UpdateView(self)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="setcanal-updates", aliases=["set-updates", "setupdates"])
    @commands.has_permissions(administrator=True)
    async def set_updates_channel(self, ctx, canal: discord.TextChannel):
        """Establece el canal de novedades"""
        self.bot.config['updates_channel'] = canal.id
        self.bot.save_config(self.bot.config)
        
        embed = discord.Embed(
            title="📢 Canal de Novedades Configurado",
            description=f"Las actualizaciones se enviarán a {canal.mention}",
            color=0x5CFF9D
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="enviar-update", aliases=["send-update", "update"])
    @commands.has_permissions(administrator=True)
    async def enviar_update(self, ctx, version: str = None):
        """Envía una actualización. Sin argumento muestra selector."""
        versions = self.get_versions()
        
        if not versions:
            return await ctx.send('`❌` No hay archivos de versión disponibles')
        
        if version:
            version_file = f"version-{version.replace('v', '').replace('.', '-')}"
            if version_file not in versions:
                return await ctx.send(f'`❌` Versión `{version}` no encontrada')
            
            class FakeInteraction:
                def __init__(self, ctx):
                    self.guild = ctx.guild
                    self.user = ctx.author
                    self._responded = False
                
                async def response_send(self, content, ephemeral=False):
                    await ctx.send(content)
                    self._responded = True
                
                async def defer(self, ephemeral=False):
                    pass
                
                @property
                def response(self):
                    class Response:
                        async def send_message(s, content, ephemeral=False):
                            await ctx.send(content)
                        async def defer(s, ephemeral=False):
                            pass
                    return Response()
                
                @property
                def followup(self):
                    class Followup:
                        async def send(s, content, ephemeral=False):
                            await ctx.send(content)
                    return Followup()
            
            fake = FakeInteraction(ctx)
            await self.send_update(fake, version_file)
        else:
            embed = discord.Embed(
                title="📋 Seleccionar Versión",
                description="Elige la versión que deseas enviar:",
                color=0xFF69B4
            )
            view = VersionSelectView(self, versions)
            await ctx.send(embed=embed, view=view)
    
    @commands.command(name="ver-updates", aliases=["list-updates", "versiones"])
    async def ver_updates(self, ctx):
        """Lista todas las versiones disponibles"""
        versions = self.get_versions()
        
        if not versions:
            return await ctx.send('`📦` No hay versiones disponibles')
        
        embed = discord.Embed(
            title="📦 Versiones Disponibles",
            color=0xFF69B4
        )
        
        versions_text = '\n'.join([
            f"• `{v.replace('version-', 'v').replace('-', '.')}`" 
            for v in versions
        ])
        
        embed.description = versions_text
        embed.set_footer(text=f"Total: {len(versions)} versiones")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Novedades(bot))
