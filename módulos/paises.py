import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
from PIL import Image
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.country_image_builder import CountryImageBuilder

async def setup(bot):
    await bot.add_cog(Paises(bot))

class Paises(commands.Cog):
    """Sistema de Identidad de Países con Panel Visual"""
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.Colors = bot.Colors
        self.PAISES_LATAM = bot.PAISES_LATAM
        self.image_builder = CountryImageBuilder()

    def create_welcome_embed(self, guild):
        """Embed de bienvenida"""
        embed = discord.Embed(
            color=self.Colors.PINK,
            description=(
                "```\n"
                "✨ ────────────────────────────────── ✨\n"
                "       🌸 SELECTOR DE NACIONALIDAD 🌸\n"
                "✨ ────────────────────────────────── ✨\n"
                "```\n"
                "**🎀 ¡Bienvenida a tu Comunidad Global! 🎀**\n\n"
                "Tu bandera es el reflejo de tu historia. Elige tu país y desbloquea una identidad única.\n\n"
                "✨ BENEFICIOS:\n"
                "🎭 Rol Personalizado\n"
                "🌍 Conexión Regional\n"
                "🕒 Eventos Locales\n\n"
                "Haz clic en **'Elegir mi Nación'** para comenzar."
            )
        )
        
        embed.set_author(
            name=f"✨ Portal de Identidad | {guild.name} ✨", 
            icon_url=guild.icon.url if guild.icon else None
        )
        
        paises = list(self.PAISES_LATAM.values())
        banderas = " ".join([p["bandera"] for p in paises])
        embed.add_field(
            name="🌍 Naciones Disponibles", 
            value=f"```{banderas}```", 
            inline=False
        )
        
        embed.set_footer(
            text="Hecho con ❤️ para una comunidad hermosa ✨", 
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = datetime.now()
        
        return embed

    @commands.command(name="pais")
    @commands.has_permissions(administrator=True)
    async def pais(self, ctx, accion: str = "help", *, argumento: str = None):
        """Comando de administración - Gestiona el sistema de países"""
        accion = accion.lower()
        
        if accion == "setup":
            """Configurar sistema inicial"""
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
                ctx.guild.me: discord.PermissionOverwrite(send_messages=True, manage_messages=True, manage_roles=True)
            }
            
            category = discord.utils.get(ctx.guild.categories, name="✨ CONFIGURACIÓN ✨") or \
                       await ctx.guild.create_category("✨ CONFIGURACIÓN ✨")
            
            channel = await ctx.guild.create_text_channel(
                name="🌸-nacionalidad",
                overwrites=overwrites,
                category=category,
                topic="✨ Selecciona tu país y personaliza tu estancia ✨"
            )
            
            view = PaisView(self.bot)
            embed = self.create_welcome_embed(ctx.guild)
            msg = await channel.send(embed=embed, view=view)
            
            self.config["pais_channel"] = channel.id
            self.config["pais_message"] = msg.id
            self.bot.save_config(self.config)
            
            await ctx.send(f"✨ **¡Portal configurado!** 🌸\nCanal: {channel.mention}")
            
        elif accion == "refresh":
            """Refrescar el menú"""
            channel_id = self.config.get("pais_channel")
            if not channel_id:
                return await ctx.send("❌ Sistema no configurado. Usa `-pais setup`")
            
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return await ctx.send("❌ Canal no encontrado")
            
            old_msg_id = self.config.get("pais_message")
            if old_msg_id:
                try:
                    old_msg = await channel.fetch_message(int(old_msg_id))
                    await old_msg.delete()
                except:
                    pass
            
            view = PaisView(self.bot)
            embed = self.create_welcome_embed(ctx.guild)
            msg = await channel.send(embed=embed, view=view)
            self.config["pais_message"] = msg.id
            self.bot.save_config(self.config)
            await ctx.send("✨ **¡Menú actualizado!** 🌸")

        elif accion == "gallery":
            """Mostrar galería visual"""
            async with ctx.typing():
                try:
                    gallery = self.image_builder.create_countries_grid(self.PAISES_LATAM)
                    
                    img_bytes = io.BytesIO()
                    gallery.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    file = discord.File(img_bytes, filename="galeria.png")
                    embed = discord.Embed(
                        title="🌍 Galería de Naciones",
                        description="Todos los países disponibles",
                        color=self.Colors.PINK
                    )
                    embed.set_image(url="attachment://galeria.png")
                    await ctx.send(embed=embed, file=file)
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)[:80]}")

        elif accion == "banner":
            """Mostrar banner"""
            async with ctx.typing():
                try:
                    banner = self.image_builder.create_welcome_banner(
                        ctx.guild.name,
                        len(self.PAISES_LATAM)
                    )
                    
                    img_bytes = io.BytesIO()
                    banner.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    file = discord.File(img_bytes, filename="banner.png")
                    embed = discord.Embed(color=self.Colors.PINK)
                    embed.set_image(url="attachment://banner.png")
                    await ctx.send(embed=embed, file=file)
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)[:80]}")

        elif accion in ["rename", "nombre"]:
            """Renombrar canal"""
            channel_id = self.config.get("pais_channel")
            channel = self.bot.get_channel(int(channel_id))
            if channel and argumento:
                await channel.edit(name=argumento)
                await ctx.send(f"✨ Canal renombrado a: `{argumento}`")

        elif accion == "canal":
            """Mover a otro canal"""
            if ctx.message.channel_mentions:
                channel = ctx.message.channel_mentions[0]
                view = PaisView(self.bot)
                embed = self.create_welcome_embed(ctx.guild)
                msg = await channel.send(embed=embed, view=view)
                self.config["pais_channel"] = channel.id
                self.config["pais_message"] = msg.id
                self.bot.save_config(self.config)
                await ctx.send(f"✨ Sistema movido a: {channel.mention}")
        else:
            embed = discord.Embed(
                title="✨ Sistema de Países",
                color=self.Colors.PINK,
                description=(
                    "`-pais setup` - Configurar sistema\n"
                    "`-pais refresh` - Actualizar menú\n"
                    "`-pais gallery` - Ver galería\n"
                    "`-pais banner` - Ver banner\n"
                    "`-pais rename <nombre>` - Renombrar canal\n"
                    "`-pais canal #canal` - Mover a otro canal"
                )
            )
            await ctx.send(embed=embed)

class PaisView(ui.View):
    """Vista persistente del panel de países"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Elegir Nación", style=discord.ButtonStyle.primary, emoji="✨", custom_id="pais_select_btn")
    async def select_pais(self, interaction: discord.Interaction, button: ui.Button):
        """Botón para seleccionar país"""
        view = SelectionView(self.bot)
        embed = discord.Embed(
            title="🌸 Elige tu País",
            description="Selecciona de los menús abajo",
            color=self.bot.Colors.PINK
        )
        embed.set_footer(text="Solo tú ves esto ✨")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(label="Mi Perfil", style=discord.ButtonStyle.secondary, emoji="👤", custom_id="pais_profile_btn")
    async def my_profile(self, interaction: discord.Interaction, button: ui.Button):
        """Ver perfil actual"""
        guild, user = interaction.guild, interaction.user
        country_roles = self.bot.config.get("country_roles", {}).get(str(guild.id), {})
        
        current_country = None
        for key, rid in country_roles.items():
            role = guild.get_role(int(rid))
            if role and role in user.roles:
                current_country = self.bot.PAISES_LATAM.get(key)
                break
        
        if current_country:
            try:
                # Generar tarjeta visual
                image_builder = CountryImageBuilder()
                card = image_builder.create_profile_card(current_country, user.name)
                
                img_bytes = io.BytesIO()
                card.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                file = discord.File(img_bytes, filename="perfil.png")
                embed = discord.Embed(
                    title="✨ Tu Perfil",
                    description=f"{current_country['bandera']} **{current_country['nombre']}**",
                    color=discord.Color(current_country.get("color", 0xFF69B4))
                )
                embed.set_image(url="attachment://perfil.png")
                await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
            except:
                # Fallback
                embed = discord.Embed(
                    title="✨ Tu Perfil",
                    description=f"{current_country['bandera']} {current_country['nombre']}",
                    color=discord.Color(current_country.get("color", 0xFF69B4))
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Sin Nación",
                description="Aún no tienes un país asignado 🌍",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Quitar Rol", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="pais_remove_btn")
    async def remove_pais(self, interaction: discord.Interaction, button: ui.Button):
        """Remover país"""
        guild, user = interaction.guild, interaction.user
        country_roles = self.bot.config.get("country_roles", {}).get(str(guild.id), {})
        
        removed = False
        for rid in country_roles.values():
            role = guild.get_role(int(rid))
            if role and role in user.roles:
                await user.remove_roles(role)
                removed = True
        
        if removed:
            await interaction.response.send_message("✨ Rol removido", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No tienes ningún país asignado", ephemeral=True)

class SelectionView(ui.View):
    """Vista para seleccionar país"""
    def __init__(self, bot):
        super().__init__(timeout=60)
        p_list = list(bot.PAISES_LATAM.items())
        mid = len(p_list) // 2
        self.add_item(CountryDropdown(bot, dict(p_list[:mid]), "🎀 Parte I (A-M)"))
        self.add_item(CountryDropdown(bot, dict(p_list[mid:]), "🎀 Parte II (N-Z)"))

class CountryDropdown(ui.Select):
    """Dropdown para seleccionar país"""
    def __init__(self, bot, paises, placeholder):
        self.bot = bot
        options = [
            discord.SelectOption(
                label=d["nombre"], 
                value=k, 
                emoji=d.get("bandera", "🌍"),
                description=f"Representar a {d['nombre']}"
            ) for k, d in paises.items()
        ]
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        """Procesar selección"""
        try:
            pais_key = self.values[0]
            pais_data = self.bot.PAISES_LATAM[pais_key]
            guild, user = interaction.guild, interaction.user
            
            # Obtener config actual
            country_roles = self.bot.config.get("country_roles", {})
            if str(guild.id) not in country_roles:
                country_roles[str(guild.id)] = {}
            
            guild_country_roles = country_roles[str(guild.id)]
            
            # Remover rol anterior
            for rid in guild_country_roles.values():
                try:
                    role = guild.get_role(int(rid))
                    if role and role in user.roles:
                        await user.remove_roles(role)
                except:
                    pass
            
            # Crear/Asignar nuevo rol
            role_name = f"{pais_data.get('bandera', '🌍')} {pais_data['nombre']}"
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                # Crear rol nuevo
                role = await guild.create_role(
                    name=role_name, 
                    color=discord.Color(pais_data.get("color", 0xFF69B4)),
                    reason="Sistema de Países"
                )
            
            # IMPORTANTE: SIEMPRE guardar en config
            guild_country_roles[pais_key] = role.id
            country_roles[str(guild.id)] = guild_country_roles
            self.bot.config["country_roles"] = country_roles
            self.bot.save_config(self.bot.config)
            
            # Asignar rol al usuario
            await user.add_roles(role)
            
            embed = discord.Embed(
                title="✨ ¡Identidad Confirmada!",
                description=f"{pais_data.get('bandera', '🌍')} **{pais_data['nombre']}**\n\nTu nuevo rol ha sido asignado 🌸",
                color=discord.Color(pais_data.get("color", 0xFF69B4))
            )
            await interaction.response.edit_message(embed=embed, view=None)
        except:
            await interaction.response.send_message("❌ Error al cambiar país", ephemeral=True)
