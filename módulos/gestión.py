import discord
from discord.ext import commands
from discord import ui
import asyncio
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Style:
    MAIN = 0x2B2D31
    SUCCESS = 0x43B581
    DANGER = 0xF04747
    WARN = 0xFAA61A
    INFO = 0x7289DA
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    B_TOP = "╭────────────────────────────╮"
    B_MID = "│"
    B_BOT = "╰────────────────────────────╯"
    ARROW = "╰┈➤"
    DOT = "•"

class WarningSystem:
    def __init__(self):
        self.warnings = {}
    
    def add_warning(self, guild_id: int, user_id: int, reason: str, moderator: str):
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []
        
        warning = {
            "reason": reason,
            "moderator": moderator,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings[guild_id][user_id].append(warning)
        return len(self.warnings[guild_id][user_id])
    
    def get_warnings(self, guild_id: int, user_id: int):
        return self.warnings.get(guild_id, {}).get(user_id, [])
    
    def clear_warnings(self, guild_id: int, user_id: int):
        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            count = len(self.warnings[guild_id][user_id])
            del self.warnings[guild_id][user_id]
            return count
        return 0

warning_system = WarningSystem()

def check_admin(interaction: discord.Interaction) -> bool:
    if not interaction.user.guild_permissions.administrator:
        asyncio.create_task(
            interaction.response.send_message(
                "❌ Acceso Denegado", 
                ephemeral=True
            )
        )
        return False
    return True

class AdminSelect(ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="Gestión de Canales", description="Nuke, Lock, Hide, Slowmode, Rename...", emoji="🛠️", value="channels"),
            discord.SelectOption(label="Seguridad & Anti-Raid", description="Lockdown, Purge, Ban/Unban, Mute...", emoji="🛡️", value="security"),
            discord.SelectOption(label="Permisos & Roles", description="Sync, Reset, Add/Remove Role...", emoji="🔑", value="permissions"),
            discord.SelectOption(label="Moderación General", description="Kick, Warn, Clear Warnings...", emoji="⚖️", value="moderation"),
        ]
        super().__init__(placeholder="Selecciona una categoría de gestión...", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if not check_admin(interaction):
            return
        
        try:
            if self.values[0] == "channels":
                await interaction.response.edit_message(embed=Panels.channels(interaction.guild, interaction.channel), view=ChannelActions(self.bot, interaction.channel))
            elif self.values[0] == "security":
                await interaction.response.edit_message(embed=Panels.security(interaction.guild), view=SecurityActions(self.bot))
            elif self.values[0] == "permissions":
                await interaction.response.edit_message(embed=Panels.permissions(interaction.guild, interaction.channel), view=PermissionActions(self.bot, interaction.channel))
            elif self.values[0] == "moderation":
                await interaction.response.edit_message(embed=Panels.moderation(interaction.guild), view=ModerationActions(self.bot))
        except Exception as e:
            logger.error(f"Error en AdminSelect: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

class Panels:
    @staticmethod
    def main(guild):
        embed = discord.Embed(title="💠 SISTEMA CENTRAL DE ADMINISTRACIÓN", color=Style.MAIN, timestamp=datetime.now())
        embed.description = (
            f"{Style.B_TOP}\n"
            f" {Style.B_MID} 👤 **Admin:** {guild.me.display_name}\n"
            f" {Style.B_MID} 🌐 **Servidor:** {guild.name}\n"
            f" {Style.B_MID} 📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y')}\n"
            f"{Style.B_BOT}\n\n"
            f"**{Style.DOT} BIENVENIDO AL PANEL AVANZADO**\n"
            f"Selecciona una categoría en el menú inferior para gestionar.\n\n"
            f"{Style.DIVIDER}"
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Manus Admin System • v4.1")
        return embed

    @staticmethod
    def channels(guild, channel):
        embed = discord.Embed(title="🛠️ GESTIÓN DE CANALES", color=Style.INFO, timestamp=datetime.now())
        overwrites = channel.overwrites_for(guild.default_role)
        lock_status = "🔒 Bloqueado" if overwrites.send_messages is False else "🔓 Desbloqueado"
        hide_status = "👻 Oculto" if overwrites.view_channel is False else "👁️ Visible"
        
        embed.description = (
            f"{Style.ARROW} **Canal Actual:** {channel.mention}\n"
            f"{Style.ARROW} **Estado:** {lock_status} | {hide_status}\n"
            f"{Style.DIVIDER}\n"
            f"**Funciones disponibles:**\n"
            f"• ☢️ **Nuke** - Recrear canal (con confirmación)\n"
            f"• 🔒 **Lock/Unlock** - Bloquear/Desbloquear escritura\n"
            f"• 👻 **Hide/Show** - Ocultar/Mostrar canal\n"
            f"• ✏️ **Rename** - Cambiar nombre\n"
            f"• ⏱️ **Slowmode** - Configurar modo lento\n"
            f"{Style.DIVIDER}"
        )
        return embed

    @staticmethod
    def security(guild):
        embed = discord.Embed(title="🛡️ SEGURIDAD & ANTI-RAID", color=Style.DANGER, timestamp=datetime.now())
        embed.description = (
            f"{Style.ARROW} **Estado del Servidor:** 🟢 Protegido\n"
            f"{Style.DIVIDER}\n"
            f"**Funciones disponibles:**\n"
            f"• 🚨 **Lockdown** - Bloqueo global de canales\n"
            f"• 🧹 **Purge** - Limpiar mensajes masivamente\n"
            f"• 🔨 **Ban/Unban** - Banear/Desbanear usuarios\n"
            f"• 🔇 **Mute/Unmute** - Silenciar/Desilenciar usuarios\n"
            f"{Style.DIVIDER}"
        )
        return embed

    @staticmethod
    def permissions(guild, channel):
        embed = discord.Embed(title="🔑 PERMISOS & ROLES", color=Style.WARN, timestamp=datetime.now())
        sync_status = "✅ Sincronizado" if getattr(channel, 'category', None) else "❌ Sin categoría"
        embed.description = (
            f"{Style.ARROW} **Canal:** {channel.name}\n"
            f"{Style.ARROW} **Sync:** {sync_status}\n"
            f"{Style.DIVIDER}\n"
            f"**Funciones disponibles:**\n"
            f"• 🔄 **Sync** - Sincronizar con categoría\n"
            f"• 🔄 **Reset** - Resetear permisos\n"
            f"• ➕ **Add Role** - Agregar rol a usuario\n"
            f"• ➖ **Remove Role** - Quitar rol a usuario\n"
            f"{Style.DIVIDER}"
        )
        return embed

    @staticmethod
    def moderation(guild):
        embed = discord.Embed(title="⚖️ MODERACIÓN GENERAL", color=Style.SUCCESS, timestamp=datetime.now())
        embed.description = (
            f"{Style.ARROW} **Herramientas de Moderación**\n"
            f"{Style.DIVIDER}\n"
            f"**Funciones disponibles:**\n"
            f"• 👢 **Kick** - Expulsar usuario\n"
            f"• ⚠️ **Warn** - Advertir usuario (con sistema)\n"
            f"• 🧹 **Clear Warns** - Limpiar advertencias\n"
            f"{Style.DIVIDER}"
        )
        return embed

class ChannelActions(ui.View):
    def __init__(self, bot, channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.add_item(AdminSelect(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return check_admin(interaction)

    @ui.button(label="Nuke Canal", emoji="☢️", style=discord.ButtonStyle.danger, row=0)
    async def nuke_channel(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmView(self.bot, "nuke", self.channel)
        await interaction.response.send_message(
            f"⚠️ **¿Confirmas el Nuke de {self.channel.mention}?**\nEsto recreará el canal y eliminará todo el historial.",
            view=confirm_view,
            ephemeral=True
        )

    @ui.button(label="Lock/Unlock", emoji="🔒", style=discord.ButtonStyle.secondary, row=0)
    async def lock_toggle(self, interaction: discord.Interaction, button: ui.Button):
        try:
            overwrite = self.channel.overwrites_for(interaction.guild.default_role)
            if overwrite.send_messages is False:
                overwrite.send_messages = None
                status = "desbloqueado"
            else:
                overwrite.send_messages = False
                status = "bloqueado"
            
            await self.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"🔒 Canal **{status}** correctamente.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @ui.button(label="Hide/Show", emoji="👻", style=discord.ButtonStyle.secondary, row=0)
    async def hide_toggle(self, interaction: discord.Interaction, button: ui.Button):
        try:
            overwrite = self.channel.overwrites_for(interaction.guild.default_role)
            if overwrite.view_channel is False:
                overwrite.view_channel = True
                status = "visible"
            else:
                overwrite.view_channel = False
                status = "oculto"
            
            await self.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"👻 Canal ahora **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @ui.button(label="Renombrar", emoji="✏️", style=discord.ButtonStyle.primary, row=1)
    async def rename_channel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RenameModal(self.channel))

    @ui.button(label="Slowmode", emoji="⏱️", style=discord.ButtonStyle.primary, row=1)
    async def set_slowmode(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(SlowmodeModal(self.channel))

class SecurityActions(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.add_item(AdminSelect(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return check_admin(interaction)

    @ui.button(label="Lockdown Global", emoji="🚨", style=discord.ButtonStyle.danger, row=0)
    async def lockdown(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmView(self.bot, "lockdown", interaction.guild)
        await interaction.response.send_message(
            "🚨 **¿Confirmas el BLOQUEO GLOBAL?**\nEsto bloqueará la escritura en **todos** los canales de texto.",
            view=confirm_view,
            ephemeral=True
        )

    @ui.button(label="Purge 100", emoji="🧹", style=discord.ButtonStyle.secondary, row=0)
    async def purge(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmView(self.bot, "purge", interaction.channel, limit=100)
        await interaction.response.send_message(
            "🧹 **¿Confirmar limpieza de 100 mensajes?**\nEsta acción no se puede deshacer.",
            view=confirm_view,
            ephemeral=True
        )

    @ui.button(label="Banear", emoji="🔨", style=discord.ButtonStyle.danger, row=1)
    async def ban_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("ban", self.bot))

    @ui.button(label="Desbanear", emoji="✅", style=discord.ButtonStyle.success, row=1)
    async def unban_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("unban", self.bot))

    @ui.button(label="Mutear", emoji="🔇", style=discord.ButtonStyle.secondary, row=2)
    async def mute_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("mute", self.bot))

    @ui.button(label="Desmutear", emoji="🔊", style=discord.ButtonStyle.success, row=2)
    async def unmute_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("unmute", self.bot))

class PermissionActions(ui.View):
    def __init__(self, bot, channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.add_item(AdminSelect(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return check_admin(interaction)

    @ui.button(label="Sincronizar", emoji="🔄", style=discord.ButtonStyle.primary, row=0)
    async def sync(self, interaction: discord.Interaction, button: ui.Button):
        try:
            if self.channel.category:
                await self.channel.edit(sync_permissions=True)
                await interaction.response.send_message("🔄 Permisos sincronizados con la categoría.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Este canal no está en ninguna categoría.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @ui.button(label="Resetear", emoji="🗑️", style=discord.ButtonStyle.secondary, row=0)
    async def reset_permissions(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmView(self.bot, "reset_perms", self.channel)
        await interaction.response.send_message(
            "⚠️ **¿Resetear todos los permisos del canal?**\nSe eliminarán todos los overwrites personalizados.",
            view=confirm_view,
            ephemeral=True
        )

    @ui.button(label="Agregar Rol", emoji="➕", style=discord.ButtonStyle.success, row=1)
    async def add_role(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RoleActionModal("add", self.bot))

    @ui.button(label="Quitar Rol", emoji="➖", style=discord.ButtonStyle.danger, row=1)
    async def remove_role(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RoleActionModal("remove", self.bot))

class ModerationActions(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.add_item(AdminSelect(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return check_admin(interaction)

    @ui.button(label="Expulsar", emoji="👢", style=discord.ButtonStyle.danger, row=0)
    async def kick_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("kick", self.bot))

    @ui.button(label="Advertir", emoji="⚠️", style=discord.ButtonStyle.secondary, row=0)
    async def warn_user(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("warn", self.bot))

    @ui.button(label="Ver Advertencias", emoji="📋", style=discord.ButtonStyle.primary, row=0)
    async def view_warnings(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ViewWarningsModal(self.bot))

    @ui.button(label="Limpiar Advertencias", emoji="🧹", style=discord.ButtonStyle.success, row=1)
    async def clear_warnings(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(UserActionModal("clear_warns", self.bot))

class ConfirmView(ui.View):
    def __init__(self, bot, action, target=None, limit=None):
        super().__init__(timeout=30)
        self.bot = bot
        self.action = action
        self.target = target
        self.limit = limit

    @ui.button(label="CONFIRMAR", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        try:
            if self.action == "nuke":
                await self._execute_nuke(interaction)
            elif self.action == "lockdown":
                await self._execute_lockdown(interaction)
            elif self.action == "purge":
                await self._execute_purge(interaction)
            elif self.action == "reset_perms":
                await self._execute_reset_perms(interaction)
            
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
        except Exception as e:
            logger.error(f"Error en confirmación {self.action}: {e}")
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @ui.button(label="CANCELAR", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("❌ Acción cancelada.", ephemeral=True)

    async def _execute_nuke(self, interaction: discord.Interaction):
        channel = self.target
        new_channel = await channel.clone(reason=f"Nuke por {interaction.user}")
        await new_channel.edit(position=channel.position, category=channel.category)
        await channel.delete(reason=f"Nuke por {interaction.user}")
        embed = discord.Embed(title="☢️ Canal Nuked", description=f"Este canal fue recreado por {interaction.user.mention}", color=Style.DANGER)
        await new_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Canal nuked correctamente. Nuevo canal: {new_channel.mention}", ephemeral=True)

    async def _execute_lockdown(self, interaction: discord.Interaction):
        guild = self.target
        locked = 0
        failed = 0
        await interaction.response.defer(ephemeral=True)
        for channel in guild.text_channels:
            try:
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
                locked += 1
            except:
                failed += 1
        await interaction.followup.send(f"🚨 **Lockdown ejecutado**\n✅ Canales bloqueados: {locked}\n❌ Fallidos: {failed}", ephemeral=True)

    async def _execute_purge(self, interaction: discord.Interaction):
        deleted = await self.target.purge(limit=self.limit or 100)
        await interaction.response.send_message(f"🧹 **Limpieza completada**\nSe eliminaron {len(deleted)} mensajes.", ephemeral=True)

    async def _execute_reset_perms(self, interaction: discord.Interaction):
        await self.target.edit(overwrites={})
        await interaction.response.send_message("🔄 Permisos reseteados correctamente.", ephemeral=True)

class RenameModal(ui.Modal, title="✏️ Renombrar Canal"):
    name = ui.TextInput(label="Nuevo Nombre", placeholder="nuevo-nombre", required=True, min_length=1, max_length=100)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            old = self.channel.name
            await self.channel.edit(name=self.name.value)
            await interaction.response.send_message(f"✅ Canal renombrado: `{old}` → `{self.name.value}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class SlowmodeModal(ui.Modal, title="⏱️ Configurar Slowmode"):
    seconds = ui.TextInput(label="Segundos (0-21600)", placeholder="0 para desactivar", required=True)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            secs = int(self.seconds.value)
            if not 0 <= secs <= 21600:
                await interaction.response.send_message("❌ El valor debe estar entre 0 y 21600 segundos (6 horas).", ephemeral=True)
                return
            await self.channel.edit(slowmode_delay=secs)
            status = f"{secs} segundos" if secs > 0 else "desactivado"
            await interaction.response.send_message(f"⏱️ Slowmode {status}.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Ingresa un número válido.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class UserActionModal(ui.Modal):
    user_id = ui.TextInput(label="ID del Usuario", placeholder="123456789012345678", required=True)
    reason = ui.TextInput(label="Razón", placeholder="Opcional - describe la razón", required=False, style=discord.TextStyle.paragraph)

    def __init__(self, action, bot):
        super().__init__(title=f"Acción: {action.title()}")
        self.action = action
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.user_id.value.strip())
            reason = self.reason.value or "Sin razón especificada"
            
            if self.action == "ban":
                await self._ban(interaction, uid, reason)
            elif self.action == "unban":
                await self._unban(interaction, uid, reason)
            elif self.action == "mute":
                await self._mute(interaction, uid, reason)
            elif self.action == "unmute":
                await self._unmute(interaction, uid, reason)
            elif self.action == "kick":
                await self._kick(interaction, uid, reason)
            elif self.action == "warn":
                await self._warn(interaction, uid, reason)
            elif self.action == "clear_warns":
                await self._clear_warns(interaction, uid)
        except ValueError:
            await interaction.response.send_message("❌ ID de usuario inválida. Debe ser un número.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error en UserActionModal ({self.action}): {e}")
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    async def _ban(self, interaction, uid, reason):
        user = await self.bot.fetch_user(uid)
        await interaction.guild.ban(user, reason=f"{reason} | Por: {interaction.user}")
        await interaction.response.send_message(f"🔨 **Usuario Baneado**\n👤 {user.mention} (`{user.id}`)\n📝 Razón: {reason}", ephemeral=True)

    async def _unban(self, interaction, uid, reason):
        user = await self.bot.fetch_user(uid)
        await interaction.guild.unban(user, reason=f"{reason} | Por: {interaction.user}")
        await interaction.response.send_message(f"✅ **Usuario Desbaneado**\n👤 {user.mention} (`{user.id}`)", ephemeral=True)

    async def _mute(self, interaction, uid, reason):
        member = interaction.guild.get_member(uid)
        if not member:
            await interaction.response.send_message("❌ Usuario no encontrado en el servidor.", ephemeral=True)
            return
        
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role, reason=f"{reason} | Por: {interaction.user}")
            await interaction.response.send_message(f"🔇 **Usuario Mutado**\n👤 {member.mention}\n📝 Razón: {reason}", ephemeral=True)
        else:
            duration = discord.utils.utcnow() + timedelta(hours=1)
            await member.timeout(duration, reason=f"{reason} | Por: {interaction.user}")
            await interaction.response.send_message(f"🔇 **Usuario en Timeout (1h)**\n👤 {member.mention}\n📝 Razón: {reason}\n*Crea un rol 'Muted' para silencio permanente*", ephemeral=True)

    async def _unmute(self, interaction, uid, reason):
        member = interaction.guild.get_member(uid)
        if not member:
            await interaction.response.send_message("❌ Usuario no encontrado en el servidor.", ephemeral=True)
            return
        
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        removed = False
        
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role, reason=f"{reason} | Por: {interaction.user}")
            removed = True
        
        if member.is_timed_out():
            await member.timeout(None, reason=f"{reason} | Por: {interaction.user}")
            removed = True
        
        if removed:
            await interaction.response.send_message(f"🔊 **Usuario Desmuteado**\n👤 {member.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ El usuario no estaba muteado.", ephemeral=True)

    async def _kick(self, interaction, uid, reason):
        member = interaction.guild.get_member(uid)
        if not member:
            await interaction.response.send_message("❌ Usuario no encontrado en el servidor.", ephemeral=True)
            return
        await member.kick(reason=f"{reason} | Por: {interaction.user}")
        await interaction.response.send_message(f"👢 **Usuario Expulsado**\n👤 {member.mention} (`{member.id}`)\n📝 Razón: {reason}", ephemeral=True)

    async def _warn(self, interaction, uid, reason):
        user = await self.bot.fetch_user(uid)
        count = warning_system.add_warning(interaction.guild.id, uid, reason, str(interaction.user))
        try:
            embed = discord.Embed(title=f"⚠️ Advertencia en {interaction.guild.name}", description=f"Has recibido una advertencia.\n**Razón:** {reason}", color=Style.WARN)
            await user.send(embed=embed)
            dm_status = "📨 DM enviado"
        except:
            dm_status = "❌ No se pudo enviar DM"
        await interaction.response.send_message(f"⚠️ **Usuario Advertido**\n👤 {user.mention} (`{user.id}`)\n📝 Razón: {reason}\n📊 Total de advertencias: {count}\n{dm_status}", ephemeral=True)

    async def _clear_warns(self, interaction, uid):
        user = await self.bot.fetch_user(uid)
        count = warning_system.clear_warnings(interaction.guild.id, uid)
        if count > 0:
            await interaction.response.send_message(f"🧹 **Advertencias Limpiadas**\n👤 {user.mention}\n🗑️ Se eliminaron {count} advertencia(s).", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {user.mention} no tenía advertencias.", ephemeral=True)

class ViewWarningsModal(ui.Modal, title="📋 Ver Advertencias"):
    user_id = ui.TextInput(label="ID del Usuario", placeholder="123456789012345678", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.user_id.value.strip())
            user = await self.bot.fetch_user(uid)
            warns = warning_system.get_warnings(interaction.guild.id, uid)
            
            if not warns:
                await interaction.response.send_message(f"✅ {user.mention} no tiene advertencias.", ephemeral=True)
                return
            
            embed = discord.Embed(title=f"📋 Advertencias de {user}", description=f"Total: {len(warns)}", color=Style.WARN)
            for i, w in enumerate(warns[-10:], 1):
                embed.add_field(name=f"⚠️ Advertencia #{i}", value=f"**Razón:** {w['reason']}\n**Por:** {w['moderator']}\n**Fecha:** {w['timestamp'][:10]}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ ID inválida.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class RoleActionModal(ui.Modal):
    user_id = ui.TextInput(label="ID del Usuario", placeholder="123456789012345678", required=True)
    role_name = ui.TextInput(label="Nombre del Rol", placeholder="Nombre exacto del rol", required=True)

    def __init__(self, action, bot):
        super().__init__(title=f"Acción de Rol: {action.title()}")
        self.action = action
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.user_id.value.strip())
            role_name = self.role_name.value.strip()
            
            member = interaction.guild.get_member(uid)
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            
            if not member:
                await interaction.response.send_message("❌ Usuario no encontrado en el servidor.", ephemeral=True)
                return
            if not role:
                await interaction.response.send_message(f"❌ Rol `{role_name}` no encontrado.", ephemeral=True)
                return
            if role.position >= interaction.user.top_role.position:
                await interaction.response.send_message("❌ No puedes modificar roles iguales o superiores al tuyo.", ephemeral=True)
                return
            
            if self.action == "add":
                if role in member.roles:
                    await interaction.response.send_message(f"❌ {member.mention} ya tiene el rol {role.mention}.", ephemeral=True)
                    return
                await member.add_roles(role, reason=f"Por: {interaction.user}")
                await interaction.response.send_message(f"➕ **Rol Agregado**\n👤 {member.mention}\n🏷️ {role.mention}", ephemeral=True)
            else:
                if role not in member.roles:
                    await interaction.response.send_message(f"❌ {member.mention} no tiene el rol {role.mention}.", ephemeral=True)
                    return
                await member.remove_roles(role, reason=f"Por: {interaction.user}")
                await interaction.response.send_message(f"➖ **Rol Removido**\n👤 {member.mention}\n🏷️ {role.mention}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ ID de usuario inválida.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class PanelAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_system = warning_system

    @commands.command(name="panel-g")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def manage_panel(self, ctx):
        view = ui.View(timeout=300)
        view.add_item(AdminSelect(self.bot))
        await ctx.send(embed=Panels.main(ctx.guild), view=view)

    @commands.command(name="warnings")
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def view_warnings_cmd(self, ctx, user: discord.User):
        warns = warning_system.get_warnings(ctx.guild.id, user.id)
        if not warns:
            await ctx.send(f"✅ {user.mention} no tiene advertencias.")
            return
        embed = discord.Embed(title=f"📋 Advertencias de {user}", color=Style.WARN)
        for i, w in enumerate(warns, 1):
            embed.add_field(name=f"⚠️ #{i}", value=f"Razón: {w['reason']}\nPor: {w['moderator']}\nFecha: {w['timestamp'][:10]}", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PanelAdmin(bot))