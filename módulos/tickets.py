
import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
import os
import asyncio
import io
from PIL import Image, ImageDraw, ImageFont
import random

# ──────────────────────────────
# GENERADOR DE BANNERS PARA TICKETS
# ──────────────────────────────

async def generate_ticket_panel_banner(guild: discord.Guild):
    """Banner principal para el panel de tickets"""
    W, H = 1100, 400
    
    # Fondo con gradiente oscuro
    base = Image.new("RGBA", (W, H), "#0a0a0f")
    draw = ImageDraw.Draw(base)
    
    # Gradiente vertical
    for y in range(H):
        alpha = int(25 * (y / H))
        draw.rectangle([(0, y), (W, y+1)], fill=f"#{alpha:02x}0a{alpha+15:02x}")
    
    # Partículas decorativas
    for _ in range(60):
        x = random.randint(0, W)
        y = random.randint(0, H)
        size = random.randint(1, 3)
        alpha = random.randint(80, 200)
        draw.ellipse((x, y, x+size, y+size), fill=(255, 105, 180, alpha))
    
    # Marco elegante
    for i in range(3):
        draw.rounded_rectangle(
            (10-i, 10-i, W-10+i, H-10+i),
            radius=25,
            outline=(255, 105, 180, 100-i*20),
            width=2
        )
    draw.rounded_rectangle((10, 10, W-10, H-10), radius=25, outline="#ff69b4", width=4)
    
    # Cargar fuentes
    try:
        font_title = ImageFont.truetype("fonts/classic.ttf", 38)
        font_subtitle = ImageFont.truetype("fonts/classic.ttf", 22)
        font_text = ImageFont.truetype("fonts/classic.ttf", 18)
    except:
        font_title = font_subtitle = font_text = None
    
    # Textos
    title = "CENTRO DE SOPORTE DE NODEX"
    subtitle = "Estamos aqui para ayudarte"
    
    # Centrar el título
    if font_title:
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = bbox[2] - bbox[0]
        title_x = (W - title_width) // 2
    else:
        title_x = W // 2 - 200
    
    draw.text((title_x, 60), title, fill="#ff69b4", font=font_title)
    draw.text((W//2 - 150, 120), subtitle, fill="#d1d1d1", font=font_subtitle)
    
    # Iconos decorativos
    draw.text((80, 140), "️", font=font_title)
    draw.text((W-120, 140), "", font=font_title)
    
    # Footer
    draw.text((W//2 - 100, H-50), f"--- Sistema de Tickets ---", fill="#ff69b4", font=font_text)
    
    # Icono del servidor si existe
    if guild.icon:
        try:
            icon_bytes = await guild.icon.read()
            icon = Image.open(io.BytesIO(icon_bytes)).convert("RGBA").resize((180, 180))
            
            mask = Image.new("L", (180, 180), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 180, 180), fill=255)
            icon.putalpha(mask)
            
            base.paste(icon, (W//2 - 70, 155), icon)
        except:
            pass
    
    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

async def generate_ticket_created_banner(user: discord.Member, ticket_type: str, ticket_num: int):
    """Banner cuando se crea un ticket"""
    W, H = 800, 300
    
    base = Image.new("RGBA", (W, H), "#0f0a14")
    draw = ImageDraw.Draw(base)
    
    # Gradiente
    for y in range(H):
        alpha = int(20 * (y / H))
        draw.rectangle([(0, y), (W, y+1)], fill=f"#{alpha:02x}0a{alpha+12:02x}")
    
    # Partículas
    random.seed(user.id)
    for _ in range(40):
        x = random.randint(0, W)
        y = random.randint(0, H)
        size = random.randint(1, 2)
        draw.ellipse((x, y, x+size, y+size), fill=(255, 105, 180, random.randint(100, 200)))
    
    # Marco
    draw.rounded_rectangle((12, 12, W-12, H-12), radius=20, outline="#ff69b4", width=3)
    
    # Avatar del usuario
    avatar_size = 100
    try:
        avatar_bytes = await user.display_avatar.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((avatar_size, avatar_size))
        
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
        
        # Glow del avatar
        glow = Image.new("RGBA", (avatar_size+16, avatar_size+16), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        for i in range(8, 0, -1):
            glow_draw.ellipse((8-i, 8-i, avatar_size+8+i, avatar_size+8+i), fill=(255, 105, 180, 40-i*4))
        
        base.paste(glow, (50-8, H//2 - avatar_size//2-8), glow)
        avatar.putalpha(mask)
        
        avatar_border = Image.new("RGBA", (avatar_size+6, avatar_size+6), (0, 0, 0, 0))
        ImageDraw.Draw(avatar_border).ellipse((0, 0, avatar_size+6, avatar_size+6), outline="#ff69b4", width=3)
        base.paste(avatar_border, (50-3, H//2 - avatar_size//2-3), avatar_border)
        base.paste(avatar, (50, H//2 - avatar_size//2), avatar)
    except:
        pass
    
    # Fuentes
    try:
        font_title = ImageFont.truetype("fonts/classic.ttf", 40)
        font_info = ImageFont.truetype("fonts/classic.ttf", 24)
    except:
        font_title = font_info = None
    
    # Iconos por tipo
    icons = {
        "Reporte": ">:C",
        "Soporte": "C:",
        "Consulta": ".?"
    }
    icon = icons.get(ticket_type, "ticket")
    
    # Textos
    text_x = 200
    draw.text((text_x, 60), f"{icon} TICKET #{ticket_num}", fill="#ff69b4", font=font_title)
    draw.text((text_x, 115), f"Tipo: {ticket_type}", fill="#ffffff", font=font_info)
    draw.text((text_x, 150), f"Usuario: {user.display_name[:20]}", fill="#d1d1d1", font=font_info)
    draw.text((text_x, 185), f"Creado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill="#a0a0a0", font=font_info)
    
    # Footer
    draw.text((text_x, H-60), "NODEX♥", fill="#ff69b4", font=font_info)
    
    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ──────────────────────────────
# UTILIDADES
# ──────────────────────────────

class UI_Styles:
    @staticmethod
    def create_divider(text):
        return f"╭{'─' * 24}╮\n      {text}\n╰{'─' * 24}╯"

# ──────────────────────────────
# MODALES
# ──────────────────────────────

class TicketRenameModal(ui.Modal, title="📝 Renombrar Ticket"):
    new_name = ui.TextInput(
        label="Nuevo nombre del canal", 
        placeholder="ej: duda-pago (sin emojis)", 
        min_length=3, 
        max_length=20,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            old_name = interaction.channel.name
            prefix = old_name.split('-')[0] if '-' in old_name else "🎫"
            new_channel_name = f"{prefix}-{self.new_name.value.lower().replace(' ', '-')}"
            await interaction.channel.edit(name=new_channel_name)
            
            embed = discord.Embed(
                title="✧ Ticket Renombrado",
                description=f"✅ **Cambio exitoso:**\n`{old_name}` ➔ `{interaction.channel.name}`",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al renombrar: {e}", ephemeral=True)

class TicketAddUserModal(ui.Modal, title="👤 Añadir Usuario al Ticket"):
    user_id = ui.TextInput(
        label="ID del Usuario", 
        placeholder="Pega aquí el ID del usuario", 
        min_length=17, 
        max_length=20,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user = interaction.guild.get_member(int(self.user_id.value))
            if not user:
                return await interaction.response.send_message("❌ No se encontró al usuario en este servidor.", ephemeral=True)
            
            await interaction.channel.set_permissions(
                user, 
                view_channel=True, 
                send_messages=True, 
                read_message_history=True, 
                attach_files=True
            )
            
            embed = discord.Embed(
                title="✧ Usuario Añadido",
                description=f"✅ {user.mention} ahora tiene acceso a este ticket",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ ID inválido. Asegúrate de copiar solo los números.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# ──────────────────────────────
# VISTAS
# ──────────────────────────────

class TicketView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @ui.button(label="Reportar Usuario", emoji="🛡️", style=discord.ButtonStyle.danger, custom_id="report_user_btn", row=0)
    async def report_user(self, interaction: discord.Interaction, button: ui.Button):
        await self.create_ticket_logic(interaction, "Reporte", "🔴")

    @ui.button(label="Soporte General", emoji="🎫", style=discord.ButtonStyle.primary, custom_id="general_support_btn", row=0)
    async def general_support(self, interaction: discord.Interaction, button: ui.Button):
        await self.create_ticket_logic(interaction, "Soporte", "🔵")

    @ui.button(label="Dudas/Consultas", emoji="❓", style=discord.ButtonStyle.secondary, custom_id="queries_btn", row=0)
    async def queries(self, interaction: discord.Interaction, button: ui.Button):
        await self.create_ticket_logic(interaction, "Consulta", "⚪")

    async def create_ticket_logic(self, interaction: discord.Interaction, ticket_type: str, icon: str):
        import bot as main_bot
        guild_id, user_id = str(interaction.guild.id), str(interaction.user.id)
        
        if guild_id not in main_bot.tickets_data: 
            main_bot.tickets_data[guild_id] = {}
        
        # Verificar tickets abiertos
        for tid, tinfo in main_bot.tickets_data[guild_id].items():
            if tinfo.get("author_id") == user_id and not tinfo.get("closed"):
                existing_channel = interaction.guild.get_channel(tinfo.get("channel_id"))
                if existing_channel:
                    embed_error = discord.Embed(
                        title="❌ Ticket Ya Existente",
                        description=f"Ya tienes un ticket activo: {existing_channel.mention}\n\n⊱ ────── ✧ ────── ⊰",
                        color=discord.Color.red()
                    )
                    return await interaction.response.send_message(embed=embed_error, ephemeral=True)
                else:
                    tinfo["closed"] = True
        
        # Crear categoría si no existe
        cat_name = "📋 Soporte"
        cat = discord.utils.get(interaction.guild.categories, name=cat_name)
        if not cat:
            cat = await interaction.guild.create_category(cat_name)
        
        t_num = len(main_bot.tickets_data[guild_id]) + 1
        
        # Permisos
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True, 
                attach_files=True,
                embed_links=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True, 
                manage_channels=True,
                manage_messages=True
            )
        }
        
        # Añadir roles de staff
        admin_roles = self.bot.config.get("admin_roles", [])
        mod_roles = self.bot.config.get("mod_roles", [])
        for role_id in admin_roles + mod_roles:
            try:
                role = interaction.guild.get_role(int(role_id))
                if role: 
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True, 
                        send_messages=True, 
                        read_message_history=True,
                        manage_messages=True
                    )
            except: 
                continue

        # Crear canal
        chan = await interaction.guild.create_text_channel(
            name=f"{icon}-{ticket_type.lower()}-{t_num}", 
            category=cat, 
            overwrites=overwrites,
            topic=f"🎫 Ticket de {interaction.user.name} | ID: {user_id} | Tipo: {ticket_type} | Abierto: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        # Guardar en base de datos
        main_bot.tickets_data[guild_id][f"{guild_id}_{t_num}"] = {
            "channel_id": chan.id, 
            "author_id": user_id, 
            "type": ticket_type, 
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "closed": False,
            "ticket_number": t_num
        }
        main_bot.save_tickets(main_bot.tickets_data)
        
        # Generar banner del ticket
        banner = await generate_ticket_created_banner(interaction.user, ticket_type, t_num)
        banner_file = discord.File(banner, filename="ticket_banner.png")
        
        # Embed de bienvenida
        embed = discord.Embed(color=discord.Color.from_rgb(255, 105, 180))
        embed.title = f"🎫 TICKET #{t_num} - {ticket_type.upper()}"
        embed.description = (
            f"✨ **¡Hola {interaction.user.mention}!**\n"
            f"Bienvenido a tu canal de soporte privado.\n\n"
            f"╭─────────────────╮\n"
            f"│ **Información del Ticket** │\n"
            f"╰─────────────────╯\n"
            f"> 📂 **Categoría:** `{ticket_type}`\n"
            f"> 🔢 **Número:** `#{t_num}`\n"
            f"> ⏰ **Abierto:** `{datetime.now().strftime('%d/%m/%Y a las %H:%M')}`\n"
            f"> 👤 **Solicitante:** {interaction.user.mention}\n\n"
            f"**¿Cómo podemos ayudarte?**\n"
            f"Por favor, explica detalladamente tu {ticket_type.lower()} y un miembro del Staff te atenderá pronto.\n\n"
            f"⊱ ────── {'.⋅ Usa los botones de abajo para gestionar ⋅.'} ────── ⊰"
        )
        embed.set_image(url="attachment://ticket_banner.png")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(
            text=f"ID: {user_id} • {interaction.guild.name}", 
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )
        
        view = TicketControlView(self.bot)
        await chan.send(
            content=f"{interaction.user.mention} | 📢 **Staff notificado**", 
            embed=embed, 
            file=banner_file,
            view=view
        )
        
        # Respuesta al usuario
        success_embed = discord.Embed(
            title="✧ Ticket Creado",
            description=f"✅ Tu ticket ha sido creado: {chan.mention}\n\n⊱ ────── ✧ ────── ⊰",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

class TicketControlView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @ui.button(label="Cerrar", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", row=0)
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="🔒 Cerrar Ticket",
            description=(
                "¿Estás seguro de cerrar este ticket?\n\n"
                "✅ Se guardará una **transcripción completa**\n"
                "✅ Se enviará al canal de logs\n"
                "❌ **El canal será eliminado**\n\n"
                "⊱ ────── ✧ ────── ⊰"
            ),
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=TicketConfirmCloseView(self.bot), ephemeral=True)

    @ui.button(label="Reclamar", emoji="🙋‍♂️", style=discord.ButtonStyle.success, custom_id="claim_ticket_btn", row=0)
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        admin_roles = self.bot.config.get("admin_roles", [])
        mod_roles = self.bot.config.get("mod_roles", [])
        user_role_ids = [role.id for role in interaction.user.roles]
        
        is_staff = any(rid in admin_roles or rid in mod_roles for rid in user_role_ids) or interaction.user.guild_permissions.administrator
        
        if not is_staff:
            return await interaction.response.send_message("❌ Solo el Staff puede reclamar tickets.", ephemeral=True)
        
        embed = discord.Embed(
            title="✧ Ticket Reclamado",
            description=(
                f"✅ **Reclamado por:** {interaction.user.mention}\n"
                f"El Staff se encargará de tu solicitud.\n\n"
                f"⊱ ────── ✧ ────── ⊰"
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        
        button.disabled = True
        button.label = "Reclamado"
        button.style = discord.ButtonStyle.secondary
        await interaction.message.edit(view=self)

    @ui.button(label="Añadir", emoji="👤", style=discord.ButtonStyle.secondary, custom_id="add_user_btn", row=0)
    async def add_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketAddUserModal())

    @ui.button(label="Renombrar", emoji="📝", style=discord.ButtonStyle.secondary, custom_id="rename_ticket_btn", row=0)
    async def rename(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketRenameModal())
    
    @ui.button(label="Transcripción", emoji="📄", style=discord.ButtonStyle.primary, custom_id="transcript_btn", row=1)
    async def transcript(self, interaction: discord.Interaction, button: ui.Button):
        """Genera y envía la transcripción sin cerrar el ticket"""
        await interaction.response.defer(ephemeral=True)
        
        channel = interaction.channel
        transcript = f"╭{'─' * 50}╮\n"
        transcript += f"  TRANSCRIPCIÓN DE TICKET: {channel.name}\n"
        transcript += f"╰{'─' * 50}╯\n\n"
        transcript += f"ID del Canal: {channel.id}\n"
        transcript += f"Generado por: {interaction.user.name} ({interaction.user.id})\n"
        transcript += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        transcript += f"{'─' * 50}\n\n"
        
        try:
            msg_count = 0
            async for message in channel.history(limit=None, oldest_first=True):
                time = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = f"{message.author.name} ({message.author.id})"
                content = message.content if message.content else "[Archivo/Embed/Contenido multimedia]"
                
                transcript += f"[{time}] {author}:\n{content}\n\n"
                msg_count += 1
        except Exception as e:
            transcript += f"\n[Error al generar historial: {e}]\n"
        
        transcript += f"\n{'─' * 50}\n"
        transcript += f"Total de mensajes: {msg_count}\n"
        
        file = discord.File(
            io.BytesIO(transcript.encode('utf-8')), 
            filename=f"transcript-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        )
        
        await interaction.followup.send(
            "✅ **Transcripción generada**", 
            file=file, 
            ephemeral=True
        )

class TicketConfirmCloseView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot
        
    @ui.button(label="Confirmar Cierre", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Deshabilitar botones
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        
        import bot as main_bot
        guild_id = str(interaction.guild.id)
        channel = interaction.channel
        
        # 1. Generar Transcripción mejorada
        transcript = f"╭{'─' * 60}╮\n"
        transcript += f"  TRANSCRIPCIÓN COMPLETA DE TICKET\n"
        transcript += f"╰{'─' * 60}╯\n\n"
        transcript += f"📋 Nombre del canal: {channel.name}\n"
        transcript += f"🆔 ID del canal: {channel.id}\n"
        transcript += f"📅 Fecha de cierre: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        transcript += f"👤 Cerrado por: {interaction.user.name} ({interaction.user.id})\n"
        
        # Obtener info del ticket
        ticket_info = None
        if guild_id in main_bot.tickets_data:
            for tid, tinfo in main_bot.tickets_data[guild_id].items():
                if tinfo["channel_id"] == channel.id:
                    ticket_info = tinfo
                    transcript += f"🎫 Número de ticket: #{tinfo.get('ticket_number', 'N/A')}\n"
                    transcript += f"📂 Tipo: {tinfo.get('type', 'N/A')}\n"
                    transcript += f"👥 Abierto por: {tinfo.get('author_id', 'Desconocido')}\n"
                    transcript += f"⏰ Fecha de apertura: {tinfo.get('created_at', 'N/A')}\n"
                    break
        
        transcript += f"\n{'═' * 60}\n"
        transcript += f"HISTORIAL DE MENSAJES\n"
        transcript += f"{'═' * 60}\n\n"
        
        try:
            msg_count = 0
            async for message in channel.history(limit=None, oldest_first=True):
                time = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = f"{message.author.name}"
                content = message.content if message.content else "[Archivo/Embed]"
                
                transcript += f"┌─ [{time}]\n"
                transcript += f"│ 👤 {author}\n"
                transcript += f"└─ {content}\n\n"
                msg_count += 1
        except Exception as e:
            transcript += f"\n[❌ Error al generar historial: {e}]\n"
        
        transcript += f"\n{'═' * 60}\n"
        transcript += f"📊 ESTADÍSTICAS\n"
        transcript += f"{'═' * 60}\n"
        transcript += f"Total de mensajes: {msg_count}\n"
        transcript += f"Duración del ticket: {channel.created_at.strftime('%Y-%m-%d %H:%M')} → {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        # 2. Actualizar base de datos
        if guild_id in main_bot.tickets_data:
            for tid, tinfo in main_bot.tickets_data[guild_id].items():
                if tinfo["channel_id"] == channel.id:
                    tinfo["closed"] = True
                    tinfo["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    tinfo["closed_by"] = str(interaction.user.id)
                    break
            main_bot.save_tickets(main_bot.tickets_data)
        
        # 3. Enviar a logs
        log_channel_id = self.bot.config.get("ticket_log_channel")
        if log_channel_id:
            log_channel = self.bot.get_channel(int(log_channel_id))
            if log_channel:
                file = discord.File(
                    io.BytesIO(transcript.encode('utf-8')), 
                    filename=f"transcript-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
                )
                
                log_embed = discord.Embed(
                    title="📄 Ticket Cerrado", 
                    color=discord.Color.red(), 
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="📋 Canal", value=f"`{channel.name}`", inline=True)
                log_embed.add_field(name="🔒 Cerrado por", value=interaction.user.mention, inline=True)
                
                if ticket_info:
                    log_embed.add_field(name="👤 Abierto por", value=f"<@{ticket_info['author_id']}>", inline=True)
                    log_embed.add_field(name="📂 Tipo", value=ticket_info.get('type', 'N/A'), inline=True)
                    log_embed.add_field(name="🎫 Número", value=f"#{ticket_info.get('ticket_number', 'N/A')}", inline=True)
                    log_embed.add_field(name="⏰ Duración", value=f"Abierto: {ticket_info.get('created_at', 'N/A')}\nCerrado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", inline=False)
                
                log_embed.set_footer(text=f"Servidor: {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                
                await log_channel.send(embed=log_embed, file=file)

        # 4. Mensaje final y eliminar canal
        final_embed = discord.Embed(
            title="🔒 Ticket Finalizado",
            description=(
                f"✅ Transcripción guardada exitosamente\n"
                f"⏰ El canal se eliminará en **5 segundos**\n\n"
                f"⊱ ────── ✧ ────── ⊰"
            ),
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=final_embed)
        
        await asyncio.sleep(5)
        try:
            await channel.delete(reason=f"Ticket cerrado por {interaction.user.name}")
        except:
            pass
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="✧ Operación Cancelada",
            description="El ticket permanece abierto.\n\n⊱ ────── ✧ ────── ⊰",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

# ──────────────────────────────
# COG
# ──────────────────────────────

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(name="panel-tk")
    @commands.has_permissions(administrator=True)
    async def tickets_panel(self, ctx, channel: discord.TextChannel = None):
        """Crea el panel principal de tickets con banner personalizado"""
        channel = channel or ctx.channel
        
        # Generar banner
        banner = await generate_ticket_panel_banner(ctx.guild)
        banner_file = discord.File(banner, filename="ticket_panel.png")
        
        embed = discord.Embed(color=discord.Color.from_rgb(255, 105, 180))
        embed.title = "🛡️ CENTRO DE ASISTENCIA Y SOPORTE"
        embed.description = (
            "✨ **¿Necesitas ayuda? Nuestro equipo está listo para asistirte.**\n\n"
            "╭─────────────────╮\n"
            "│ **Selecciona tu ticket**⠀│\n"
            "╰─────────────────╯\n\n"
            "🛡️ **Reportar Usuario**\n"
            "> Para denunciar comportamientos que violen las reglas del servidor.\n\n"
            "🎫 **Soporte General**\n"
            "> Ayuda con configuraciones, dudas técnicas o problemas generales.\n\n"
            "❓ **Dudas/Consultas**\n"
            "> Preguntas rápidas, información adicional o aclaraciones.\n\n"
            "╭─────────────────╮\n"
            "│ ** ⚠️ Importante **  ⠀⠀   │\n"
            "╰─────────────────╯\n"
            "> ✦ No abras tickets sin motivo válido\n"
            "> ✦ Sé paciente, el Staff responderá pronto\n"
            "> ✦ Mantén el respeto en todo momento\n"
            "> ✦ Solo puedes tener 1 ticket abierto a la vez\n\n"
            "⊱ ─ {.⋅ Haz clic en un botón para comenzar ⋅.} ─ ⊰"
        )
        embed.set_image(url="attachment://ticket_panel.png")
        embed.set_footer(
            text=f"{ctx.guild.name}  Sistema de Tickets", 
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        await channel.send(embed=embed, file=banner_file, view=TicketView(self.bot))
        
        success_embed = discord.Embed(
            title="✧ Panel Creado",
            description=f"✅ Panel de tickets enviado a {channel.mention}\n\n⊱ ────── ✧ ────── ⊰",
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed, delete_after=10)

    @commands.command(name="set_ticket_log")
    @commands.has_permissions(administrator=True)
    async def set_ticket_log(self, ctx, channel: discord.TextChannel):
        """Configura el canal donde se enviarán los logs de tickets cerrados"""
        self.bot.config["ticket_log_channel"] = channel.id
        import bot as main_bot
        if hasattr(main_bot, 'save_config'):
            main_bot.save_config(self.bot.config)
        
        embed = discord.Embed(
            title="✧ Canal de Logs Configurado",
            description=f"✅ Los logs se enviarán a {channel.mention}\n\n⊱ ────── ✧ ────── ⊰",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="add")
    @commands.has_permissions(manage_messages=True)
    async def add_user_cmd(self, ctx, user: discord.Member):
        """Añade un usuario al ticket actual"""
        if any(word in ctx.channel.name for word in ["ticket", "soporte", "reporte", "consulta"]):
            await ctx.channel.set_permissions(
                user, 
                view_channel=True, 
                send_messages=True, 
                read_message_history=True,
                attach_files=True
            )
            
            embed = discord.Embed(
                title="✧ Usuario Añadido",
                description=f"✅ {user.mention} ha sido añadido al ticket\n\n⊱ ────── ✧ ────── ⊰",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Este comando solo puede usarse dentro de un ticket.", delete_after=5)
    
    @commands.command(name="remove")
    @commands.has_permissions(manage_messages=True)
    async def remove_user_cmd(self, ctx, user: discord.Member):
        """Remueve un usuario del ticket actual"""
        if any(word in ctx.channel.name for word in ["ticket", "soporte", "reporte", "consulta"]):
            await ctx.channel.set_permissions(user, overwrite=None)
            
            embed = discord.Embed(
                title="✧ Usuario Removido",
                description=f"✅ {user.mention} ha sido removido del ticket\n\n⊱ ────── ✧ ────── ⊰",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Este comando solo puede usarse dentro de un ticket.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Tickets(bot))