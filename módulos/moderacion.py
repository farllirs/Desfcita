import discord
from discord.ext import commands
from datetime import timedelta, datetime
import asyncio

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ෆ Decoradores de permisos ෆ
    def is_admin_or_mod():
        async def predicate(ctx):
            if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator:
                return True
            admin_roles = ctx.bot.config.get("admin_roles", [])
            mod_roles   = ctx.bot.config.get("mod_roles",   [])
            return any(r.id in admin_roles or r.id in mod_roles for r in ctx.author.roles)
        return commands.check(predicate)

    def is_admin_only():
        async def predicate(ctx):
            if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator:
                return True
            admin_roles = ctx.bot.config.get("admin_roles", [])
            return any(r.id in admin_roles for r in ctx.author.roles)
        return commands.check(predicate)

    # ෆ Vista de confirmación super linda ෆ
    class ConfirmView(discord.ui.View):
        def __init__(self, action, member, reason, timeout=35):
            super().__init__(timeout=timeout)
            self.action = action
            self.member = member
            self.reason = reason
            self.confirmed = False

        @discord.ui.button(label="Sí, está bien ♡", style=discord.ButtonStyle.red, emoji="💞")
        async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.original_user:
                await interaction.response.send_message("Solo quien invocó el comando puede decidir, corazoncito~ ♡", ephemeral=True)
                return
            self.confirmed = True
            self.stop()

        @discord.ui.button(label="Mejor no, gracias", style=discord.ButtonStyle.grey, emoji="🩰")
        async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.original_user:
                await interaction.response.send_message("Solo el que pidió puede cancelar, mi vida~", ephemeral=True)
                return
            self.stop()

    # ╭─────────────── KICK ────────────────╮
    @commands.command(name="kick", aliases=["sacar", "expulsar", "bye"])
    @is_admin_or_mod()
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No se especificó motivo ♡"):
        if member is None:
            emb = discord.Embed(color=0xFFC0CB)
            emb.set_author(name="¡Uy, faltó alguien! ♡", icon_url=self.bot.user.display_avatar.url)
            emb.description = (
                "💕 **Uso correcto:**\n"
                "```-kick @usuario [motivo opcional]```\n"
                "Ejemplo tierno:\n`-kick @Adrian portarse re travieso`"
            )
            emb.set_footer(text="Te guío con todo mi cariñito ♡")
            return await ctx.send(embed=emb)

        if member == ctx.author:
            return await ctx.send("Ay nooo, no te saques a ti mismo, mi amor~ ¿Qué haríamos sin ti? 🥺💕")

        view = self.ConfirmView("kick", member, reason)
        view.original_user = ctx.author

        emb = discord.Embed(color=0xFF9EC1)
        emb.title = "💗  ¿Lo acompañamos a la salida con amor?  💗"
        emb.description = (
            "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦\n\n"
            f"**Mi tesoro {ctx.author.mention}** está considerando...\n"
            f"→ Sacar dulcemente a **{member.mention}** del rinconcito\n\n"
            f"**Motivito:** `{reason}`\n\n"
            "Tienes 35 segunditos para decidir, corazoncito~ 🌸💞\n"
            "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦"
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text="Sistema de Cuidados con Mucho ♡ • " + datetime.now().strftime("%d/%m/%Y  %H:%M"))

        msg = await ctx.send(embed=emb, view=view)

        await view.wait()

        if view.confirmed:
            try:
                await member.kick(reason=f"{reason} | ejecutado con cariño por {ctx.author}")
                success = discord.Embed(color=0xFFB6C1)
                success.title = "🌷  ¡Se fue con amor y paz!  🌷"
                success.description = (
                    f"**{member.mention}** ya no está con nosotras/os ♡\n"
                    f"Decisión tomada por **{ctx.author.mention}**\n"
                    f"Motivo: `{reason}`\n\n"
                    "Todo quedó bonito, ordenadito y lleno de paz~ ✧"
                )
                success.set_thumbnail(url=member.display_avatar.url)
                await msg.edit(embed=success, view=None)
            except Exception as e:
                await msg.edit(content=f"Ay, ay, ay... no pude~ → {e}", embed=None, view=None)
        else:
            await msg.edit(content="¡Qué alivio! Todo sigue precioso y juntitos ♡", embed=None, view=None)

    # ╭─────────────── BAN ────────────────╮
    @commands.command(name="ban", aliases=["perma", "exiliar", "adióseterno"])
    @is_admin_only()
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No se especificó motivo ♡"):
        if member is None:
            emb = discord.Embed(color=0xFFC0CB)
            emb.set_author(name="¡Faltó el corazoncito a banear! ♡", icon_url=self.bot.user.display_avatar.url)
            emb.description = (
                "💕 **Uso correcto:**\n"
                "```-ban @usuario [motivo opcional]```\n"
                "Ejemplo:\n`-ban @Adrian romper todas las reglas`"
            )
            emb.set_footer(text="Siempre te explico con amor ♡")
            return await ctx.send(embed=emb)

        if member == ctx.author:
            return await ctx.send("¡No, no y no! No te banees a ti mismo, mi vida~ Te necesitamos aquí 💞")

        view = self.ConfirmView("ban", member, reason)
        view.original_user = ctx.author

        emb = discord.Embed(color=0xFF85A2)
        emb.title = "🩷  ¿Lo mandamos al abismo con besitos de despedida?  🩷"
        emb.description = (
            "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦\n\n"
            f"**Mi princes@ {ctx.author.mention}** está pensando en...\n"
            f"→ **Banear para siempreee** a {member.mention}\n\n"
            f"**Motivito:** `{reason}`\n\n"
            "Decídete en 35 segunditos, porfisito~ 🌸💕\n"
            "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦"
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text="Protección Eterna con Cariñito • " + datetime.now().strftime("%d/%m/%Y  %H:%M"))

        msg = await ctx.send(embed=emb, view=view)

        await view.wait()

        if view.confirmed:
            try:
                await member.ban(reason=f"{reason} | decisión cariñosa de {ctx.author}", delete_message_days=1)
                success = discord.Embed(color=0xFF69B4)
                success.title = "💔🌸  Adiós eterno, pero con amor  🌸💔"
                success.description = (
                    f"**{member.mention}** ya no podrá volver jamás ♡\n"
                    f"Elegido por **{ctx.author.mention}**\n"
                    f"Motivo: `{reason}`\n\n"
                    "El espacio quedó protegido y lleno de armonía~ ✧"
                )
                success.set_thumbnail(url=member.display_avatar.url)
                await msg.edit(embed=success, view=None)
            except Exception as e:
                await msg.edit(content=f"Ay nooo, no pude banearlo~ → {e}", embed=None, view=None)
        else:
            await msg.edit(content="¡Menos mal! Seguimos tod@s juntitos y felices ♡🌷", embed=None, view=None)

    # ╭─────────────── MUTE ────────────────╮
    @commands.command(name="mute", aliases=["silenciar", "callar", "shh"])
    @is_admin_or_mod()
    async def mute(self, ctx, member: discord.Member = None, tiempo: str = None, *, reason: str = None):
        if member is None or tiempo is None:
            emb = discord.Embed(color=0xFFC0CB)
            emb.set_author(name="¡Uy, faltaron cositas! ♡", icon_url=self.bot.user.display_avatar.url)
            emb.description = (
                "💕 **Uso correcto:**\n"
                "```-mute @usuario minutos [motivo opcional]```\n"
                "Ejemplo:\n`-mute @Adrian 45 hablando demasiado`"
            )
            emb.set_footer(text="Te ayudo con todo mi amorcito ♡")
            return await ctx.send(embed=emb)

        try:
            minutos = int(tiempo)
            if minutos < 1 or minutos > 1440:
                return await ctx.send("Elije entre 1 y 1440 minutitos, porfi~ (1 día máximo) ♡")
        except ValueError:
            return await ctx.send("El tiempo debe ser un numerito lindo, corazon~ ♡")

        try:
            dur = timedelta(minutes=minutos)
            await member.timeout(dur, reason=reason or "Portarse un poquito malito ♡")

            emb = discord.Embed(color=0xFFB6C1)
            emb.title = "🌸✨  Silencio con besitos  ✨🌸"
            emb.description = (
                f"**{member.mention}** estará calladito por **{minutos} minutos** ♡\n"
                f"Lo pidió con cariño **{ctx.author.mention}**\n"
                f"Motivito: `{reason or 'Necesita un tiempito de paz'}`\n\n"
                "Descansa la voz, pequeño tesoro~ 🌷💕"
            )
            emb.set_thumbnail(url=member.display_avatar.url)
            emb.set_footer(text="Sistema de Mimos y Reglitas • " + datetime.now().strftime("%H:%M"))

            await ctx.send(embed=emb)

        except Exception as e:
            await ctx.send(f"Ay, ay... no pude ponerle silencio~ → {e}")

    # ╭─────────────── UNMUTE ────────────────╮
    @commands.command(name="unmute", aliases=["desilenciar", "hablar", "liberarvoz"])
    @is_admin_or_mod()
    async def unmute(self, ctx, member: discord.Member = None, *, reason: str = "¡Ya puede hablar otra vez! ♡"):
        if member is None:
            emb = discord.Embed(color=0xFFC0CB)
            emb.description = (
                "¡Faltó elegir a quién devolverle la voz! ♡\n"
                "**Uso:** `-unmute @usuario [motivo opcional]`"
            )
            emb.set_footer(text="Siempre estoy para ayudarte, mi cielo ♡")
            return await ctx.send(embed=emb)

        try:
            await member.timeout(None, reason=reason)

            emb = discord.Embed(color=0xFF9EC1)
            emb.title = "🌷💞  ¡Voz restaurada con amor!  💞🌷"
            emb.description = (
                f"**{member.mention}** ya puede charlar de nuevo~ ♡\n"
                f"Lo liberó con cariño **{ctx.author.mention}**\n"
                f"Motivito: `{reason}`\n\n"
                "¡Bienvenid@ de vuelta al ruido bonito! ✧･ﾟ:*"
            )
            emb.set_thumbnail(url=member.display_avatar.url)
            emb.set_footer(text="Sistema de Cariñitos y Voces • " + datetime.now().strftime("%H:%M"))

            await ctx.send(embed=emb)

        except Exception as e:
            await ctx.send(f"No pude devolverle la voz~ → {e}")

    # ╭─────────────── CLEAR ────────────────╮
    @commands.command(name="clear", aliases=["purga", "limpiar", "cls", "borrar"])
    @is_admin_or_mod()
    async def clear(self, ctx, cantidad: str = None):
        if cantidad is None:
            emb = discord.Embed(color=0xFFC0CB)
            emb.description = (
                "¡Faltó decir cuántos mensajitos borramos, cielo! ♡\n"
                "**Uso:** `-clear número` (máximo 300)\nEjemplo: `-clear 40`"
            )
            emb.set_footer(text="Te explico todo con amorcito ♡")
            return await ctx.send(embed=emb)

        try:
            cant = int(cantidad)
            if cant < 1 or cant > 300:
                return await ctx.send("Entre 1 y 300 mensajitos, porfisito~ ♡")
        except ValueError:
            return await ctx.send("Eso no es un numerito lindo~ Usa algo como 25 ♡")

        try:
            deleted = await ctx.channel.purge(limit=cant + 1)
            count = len(deleted) - 1

            emb = discord.Embed(color=0xFF69B4)
            emb.title = "🩷✨  ¡Todo limpio, brillante y oliendo a flores!  ✨🩷"
            emb.description = (
                f"Borré **{count}** mensajitos con mucho cariño~\n"
                f"En el canal {ctx.channel.mention}\n"
                f"Lo hizo **{ctx.author.mention}** ♡\n\n"
                "¡El rinconcito quedó impecable y precioso! 🌸"
            )
            emb.set_footer(text="Sistema de Orden, Flores y Amor • " + datetime.now().strftime("%H:%M"))
            await ctx.send(embed=emb, delete_after=12)

        except Exception as e:
            await ctx.send(f"Ay no, no pude limpiar~ → {e}")


async def setup(bot):
    await bot.add_cog(Moderacion(bot))