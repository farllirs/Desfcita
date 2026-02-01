import discord, json, os, asyncio, random, aiohttp, io
from discord.ext import commands
from discord import ui
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TIKTOKERS_FILE = 'data/tiktokers.json'
BANNERS_PATH = 'banner'
FONTS_PATH = 'fonts'

def load_tiktokers():
    os.makedirs('data', exist_ok=True)
    if os.path.exists(TIKTOKERS_FILE):
        with open(TIKTOKERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tiktokers(data):
    with open(TIKTOKERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_font(size: int):
    try: return ImageFont.truetype(f'{FONTS_PATH}/classic.ttf', size)
    except: return ImageFont.load_default()

def pretty_number(n: int) -> str:
    if n < 1_000: return str(n)
    if n < 1_000_000: return f"{n/1_000:.1f}K".replace('.0', '')
    return f"{n/1_000_000:.1f}M".replace('.0', '')

COLORS = {
    'PINK': (0xFF69B4, (255, 105, 180)), 'SKY': (0x00BFFF, (0, 191, 255)),
    'MINT': (0x00FA9A, (0, 250, 154)), 'LAVENDER': (0xE6E6FA, (230, 230, 250)),
    'GOLD': (0xFFD700, (255, 215, 0)), 'CORAL': (0xFF7F50, (255, 127, 80)),
    'VIOLET': (0x8A2BE2, (138, 43, 226)), 'AQUA': (0x00CED1, (0, 206, 209)),
    'ROSE': (0xFF007F, (255, 0, 127)), 'SUNSET': (0xFF6B6B, (255, 107, 107)),
    'OCEAN': (0x4ECDC4, (78, 205, 196)), 'GRAPE': (0x9B59B6, (155, 89, 182))
}

def hex_color(name: str) -> int:
    return COLORS.get(name, COLORS['PINK'])[0]

def rgb_color(name: str) -> tuple:
    return COLORS.get(name, COLORS['PINK'])[1]

async def fetch_avatar(url: str) -> Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            return Image.open(io.BytesIO(data)).convert('RGBA')

def create_glass_panel(width: int, height: int, bg_rgb: tuple, blur: int = 20) -> Image.Image:
    base = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(base)
    
    for i in range(height):
        ratio = i / height
        r = int(bg_rgb[0] * 0.3 + 20 * ratio)
        g = int(bg_rgb[1] * 0.3 + 15 * ratio)
        b = int(bg_rgb[2] * 0.3 + 25 * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b, 255))
    
    for _ in range(15):
        x, y = random.randint(0, width), random.randint(0, height)
        size = random.randint(2, 6)
        alpha = random.randint(30, 80)
        draw.ellipse((x, y, x+size, y+size), fill=(*bg_rgb, alpha))
    
    return base

def draw_rounded_rect(draw: ImageDraw, xy: tuple, radius: int, fill: tuple):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def create_circular_avatar(avatar: Image.Image, size: int) -> Image.Image:
    avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(avatar, (0, 0), mask)
    return output

async def generate_creator_banner(tiktok_user: str, avatar_url: str, color_name: str = 'PINK') -> io.BytesIO:
    W, H = 800, 280
    bg_rgb = rgb_color(color_name)
    
    img = create_glass_panel(W, H, bg_rgb)
    draw = ImageDraw.Draw(img)
    
    glass_panel = Image.new('RGBA', (W - 40, H - 40), (255, 255, 255, 25))
    glass_draw = ImageDraw.Draw(glass_panel)
    draw_rounded_rect(glass_draw, (0, 0, W - 40, H - 40), 30, (255, 255, 255, 25))
    img.paste(glass_panel, (20, 20), glass_panel)
    
    draw.rounded_rectangle((15, 15, W - 15, H - 15), radius=35, outline=(*bg_rgb, 150), width=3)
    
    try:
        avatar = await fetch_avatar(avatar_url)
        avatar = create_circular_avatar(avatar, 120)
        
        glow = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((0, 0, 140, 140), fill=(*bg_rgb, 100))
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        img.paste(glow, (50, 70), glow)
        
        img.paste(avatar, (60, 80), avatar)
        
        ring = Image.new('RGBA', (130, 130), (0, 0, 0, 0))
        ring_draw = ImageDraw.Draw(ring)
        ring_draw.ellipse((0, 0, 130, 130), outline=(255, 255, 255, 200), width=4)
        img.paste(ring, (55, 75), ring)
    except:
        draw.ellipse((60, 80, 180, 200), fill=(*bg_rgb, 180))
    
    font_title = get_font(42)
    font_user = get_font(28)
    font_small = get_font(18)
    
    draw.text((210, 85), '✨ CREADOR VERIFICADO ✨', font=font_small, fill=(255, 255, 255, 200))
    draw.text((210, 115), f'@{tiktok_user}', font=font_title, fill=(255, 255, 255, 255))
    draw.text((210, 175), '🎵 TikTok Creator Space', font=font_user, fill=(255, 255, 255, 220))
    
    for i, alpha in enumerate([60, 40, 20]):
        draw.line([(210, 168 + i), (500, 168 + i)], fill=(255, 255, 255, alpha))
    
    draw.polygon([(W-80, H-60), (W-50, H-40), (W-80, H-20)], fill=(*bg_rgb, 150))
    draw.polygon([(W-100, H-50), (W-75, H-35), (W-100, H-20)], fill=(255, 255, 255, 80))
    
    buffer = io.BytesIO()
    img.save(buffer, 'PNG', quality=95)
    buffer.seek(0)
    return buffer

async def generate_tools_banner(user_name: str, tiktok_user: str, avatar_url: str, 
                                 color_name: str, stats: dict) -> io.BytesIO:
    W, H = 800, 320
    bg_rgb = rgb_color(color_name)
    
    img = create_glass_panel(W, H, bg_rgb)
    draw = ImageDraw.Draw(img)
    
    glass = Image.new('RGBA', (W - 30, H - 30), (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass)
    glass_draw.rounded_rectangle((0, 0, W - 30, H - 30), radius=25, fill=(255, 255, 255, 20))
    img.paste(glass, (15, 15), glass)
    
    draw.rounded_rectangle((10, 10, W - 10, H - 10), radius=30, outline=(*bg_rgb, 180), width=3)
    
    try:
        avatar = await fetch_avatar(avatar_url)
        avatar = create_circular_avatar(avatar, 100)
        
        glow = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((0, 0, 120, 120), fill=(*bg_rgb, 80))
        glow = glow.filter(ImageFilter.GaussianBlur(8))
        img.paste(glow, (35, 35), glow)
        
        img.paste(avatar, (45, 45), avatar)
        
        ring = Image.new('RGBA', (110, 110), (0, 0, 0, 0))
        ring_draw = ImageDraw.Draw(ring)
        ring_draw.ellipse((0, 0, 110, 110), outline=(255, 255, 255, 180), width=3)
        img.paste(ring, (40, 40), ring)
    except:
        draw.ellipse((45, 45, 145, 145), fill=(*bg_rgb, 150))
    
    font_name = get_font(32)
    font_tiktok = get_font(22)
    font_label = get_font(16)
    font_value = get_font(28)
    
    draw.text((170, 50), user_name, font=font_name, fill=(255, 255, 255, 255))
    draw.text((170, 90), f'@{tiktok_user}', font=font_tiktok, fill=(255, 255, 255, 200))
    draw.text((170, 120), '🎵 TikTok Creator', font=font_label, fill=(*bg_rgb, 255))
    
    stat_items = [
        ('📹', 'Videos', pretty_number(stats.get('total_posts', 0))),
        ('💖', 'Likes', pretty_number(stats.get('total_likes', 0))),
        ('👁️', 'Alcance', pretty_number(stats.get('total_views', 0)))
    ]
    
    box_w, box_h = 150, 80
    start_x = 170
    for i, (emoji, label, value) in enumerate(stat_items):
        x = start_x + i * (box_w + 20)
        y = 180
        
        box = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
        box_draw = ImageDraw.Draw(box)
        box_draw.rounded_rectangle((0, 0, box_w, box_h), radius=15, fill=(255, 255, 255, 30))
        img.paste(box, (x, y), box)
        
        draw.text((x + 15, y + 10), emoji, font=font_label, fill=(255, 255, 255, 255))
        draw.text((x + 40, y + 8), label, font=font_label, fill=(255, 255, 255, 180))
        draw.text((x + 15, y + 40), value, font=font_value, fill=(255, 255, 255, 255))
    
    goal = stats.get('follower_goal', 0)
    current = stats.get('current_followers', 0)
    if goal > 0:
        progress = min(1.0, current / goal)
        bar_w = W - 200
        bar_x, bar_y = 170, 275
        
        draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 20), radius=10, fill=(255, 255, 255, 40))
        if progress > 0:
            draw.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 20), 
                                   radius=10, fill=(*bg_rgb, 220))
        
        draw.text((bar_x, bar_y - 20), f'🎯 {pretty_number(current)} / {pretty_number(goal)}', 
                  font=font_label, fill=(255, 255, 255, 200))
    
    buffer = io.BytesIO()
    img.save(buffer, 'PNG', quality=95)
    buffer.seek(0)
    return buffer

class TiktokerRegisterView(ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @ui.button(label='✨ Unirme', style=discord.ButtonStyle.success, custom_id='tiktoker_reg_btn')
    async def register(self, inter: discord.Interaction, _):
        await inter.response.send_modal(TiktokerModal(self.cog))

class ColorSelectView(ui.View):
    def __init__(self, cog, applicant, tiktok_user, followers, content_type, reason):
        super().__init__(timeout=300)
        self.cog = cog
        self.applicant = applicant
        self.tiktok_user = tiktok_user
        self.followers = followers
        self.content_type = content_type
        self.reason = reason
        
        options = [discord.SelectOption(label=name, value=name, emoji='🎨') for name in COLORS.keys()]
        select = ui.Select(placeholder='🎨 Elige el color de tu banner...', options=options)
        select.callback = self.color_callback
        self.add_item(select)

    async def color_callback(self, inter: discord.Interaction):
        color = inter.data['values'][0]
        await inter.response.defer(ephemeral=True)
        
        await self.submit_application(inter, color)

    async def submit_application(self, inter: discord.Interaction, color: str):
        guild = self.applicant.guild
        admin_ch = discord.utils.get(guild.text_channels, name='verificacion-creadores')
        if not admin_ch:
            admin_ch = await guild.create_text_channel('verificacion-creadores',
                overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False),
                            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)})
        
        embed = discord.Embed(color=hex_color(color))
        embed.set_author(name='Nueva Solicitud', icon_url=self.applicant.display_avatar.url)
        embed.add_field(name='`👤` Solicitante', value=self.applicant.mention, inline=True)
        embed.add_field(name='`🎵` TikTok', value=f"[@{self.tiktok_user}](https://tiktok.com/@{self.tiktok_user})", inline=True)
        embed.add_field(name='`💫` Seguidores', value=self.followers, inline=True)
        embed.add_field(name='`🎨` Color', value=color, inline=True)
        embed.add_field(name='`🎭` Contenido', value=self.content_type, inline=False)
        embed.add_field(name='`💭` Razón', value=self.reason, inline=False)
        embed.set_thumbnail(url=self.applicant.display_avatar.url)
        
        view = TiktokerApprovalView(self.cog, self.applicant, self.tiktok_user, color)
        msg = await admin_ch.send(embed=embed, view=view)
        
        await inter.followup.send(f'`✅` Solicitud enviada con color **{color}**', ephemeral=True)
        
        await asyncio.sleep(300)
        if not view.processed:
            await view.approve_action(self.applicant, self.tiktok_user, color)
            await msg.edit(content='`✅` Auto-aprobado', view=None)

class TiktokerModal(ui.Modal, title='˚₊· ͟͟͞͞➳❥ Registro de Creador'):
    tiktok_user = ui.TextInput(label='👤 Usuario TikTok', placeholder='@tu_usuario', max_length=30)
    content_type = ui.TextInput(label='🎭 Tipo de Contenido', placeholder='Gaming, Baile, Comedia...', max_length=50)
    followers = ui.TextInput(label='💫 Seguidores', placeholder='10k, 50k...', max_length=20)
    reason = ui.TextInput(label='💭 ¿Por qué quieres unirte?', style=discord.TextStyle.paragraph, max_length=300)

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, inter: discord.Interaction):
        tiktok = self.tiktok_user.value.replace('@', '')
        embed = discord.Embed(color=hex_color('PINK'))
        embed.set_author(name='🎨 Elige tu color', icon_url=inter.user.display_avatar.url)
        embed.description = '**Selecciona el color de tu banner personalizado:**'
        
        view = ColorSelectView(self.cog, inter.user, tiktok, self.followers.value, 
                               self.content_type.value, self.reason.value)
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

class TiktokerApprovalView(ui.View):
    def __init__(self, cog, applicant, tiktok_user, color='PINK'):
        super().__init__(timeout=None)
        self.cog, self.applicant, self.tiktok_user = cog, applicant, tiktok_user
        self.color = color
        self.processed = False

    async def approve_action(self, member, tiktok_user, color):
        if self.processed: return
        self.processed = True
        guild = member.guild
        role = guild.get_role(1461887491094221065)
        if role: await member.add_roles(role)
        cat = guild.get_channel(1461885197904642232)
        channel = await guild.create_text_channel(f'✨・{member.name}', category=cat,
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)})
        
        self.cog.tiktokers_data[str(member.id)] = {
            'tiktok': tiktok_user, 'channel_id': channel.id,
            'approved_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'total_posts': 0, 'total_likes': 0, 'total_views': 0,
            'bio': '', 'color': color, 'notify_role': None, 'next_post': '',
            'socials': {}, 'follower_goal': 0, 'current_followers': 0
        }
        save_tiktokers(self.cog.tiktokers_data)
        
        banner = await generate_creator_banner(tiktok_user, str(member.display_avatar.url), color)
        file = discord.File(banner, filename='welcome.png')
        
        embed = discord.Embed(color=hex_color(color))
        embed.set_author(name=f'Bienvenida {member.name}', icon_url=member.display_avatar.url)
        embed.description = f"""
╭───────────────────╮
   ✨ **Tu espacio está listo** ✨
╰───────────────────╯

➤ Sube videos: `-subir <link>`
➤ Panel de control: `-tools`

*¡Muéstrale al mundo tu contenido!*"""
        embed.set_image(url='attachment://welcome.png')
        await channel.send(file=file, embed=embed)

    @ui.button(label='Aprobar', style=discord.ButtonStyle.success, emoji='✅')
    async def accept(self, inter: discord.Interaction, _):
        await self.approve_action(self.applicant, self.tiktok_user, self.color)
        await inter.response.edit_message(content='`✅` Aprobado', view=None)

    @ui.button(label='Rechazar', style=discord.ButtonStyle.danger, emoji='❌')
    async def reject(self, inter: discord.Interaction, _):
        self.processed = True
        await inter.response.edit_message(content='`❌` Rechazado', view=None)
        try: await self.applicant.send('Tu solicitud fue rechazada. ¡Sigue intentando!')
        except: pass

class SocialLinksModal(ui.Modal, title='˚₊· ͟͟͞͞➳❥ Redes Sociales'):
    instagram = ui.TextInput(label='📸 Instagram', placeholder='@usuario', required=False, max_length=30)
    youtube = ui.TextInput(label='🎬 YouTube', placeholder='URL o @canal', required=False, max_length=100)
    twitter = ui.TextInput(label='🐦 Twitter/X', placeholder='@usuario', required=False, max_length=30)
    twitch = ui.TextInput(label='💜 Twitch', placeholder='usuario', required=False, max_length=30)

    def __init__(self, cog, uid):
        super().__init__()
        self.cog, self.uid = cog, uid
        data = cog.tiktokers_data[uid].get('socials', {})
        self.instagram.default = data.get('instagram', '')
        self.youtube.default = data.get('youtube', '')
        self.twitter.default = data.get('twitter', '')
        self.twitch.default = data.get('twitch', '')

    async def on_submit(self, inter: discord.Interaction):
        self.cog.tiktokers_data[self.uid]['socials'] = {
            'instagram': self.instagram.value, 'youtube': self.youtube.value,
            'twitter': self.twitter.value, 'twitch': self.twitch.value
        }
        save_tiktokers(self.cog.tiktokers_data)
        await inter.response.send_message('`✅` Redes actualizadas', ephemeral=True)

class FollowerGoalModal(ui.Modal, title='˚₊· ͟͟͞͞➳❥ Meta de Seguidores'):
    goal = ui.TextInput(label='🎯 Meta', placeholder='Ej: 10000', max_length=10)
    current = ui.TextInput(label='📊 Actual', placeholder='Ej: 5000', max_length=10)

    def __init__(self, cog, uid):
        super().__init__()
        self.cog, self.uid = cog, uid

    async def on_submit(self, inter: discord.Interaction):
        try:
            goal = int(self.goal.value.replace('k', '000').replace('K', '000').replace(',', ''))
            current = int(self.current.value.replace('k', '000').replace('K', '000').replace(',', ''))
            self.cog.tiktokers_data[self.uid]['follower_goal'] = goal
            self.cog.tiktokers_data[self.uid]['current_followers'] = current
            save_tiktokers(self.cog.tiktokers_data)
            
            progress = min(100, (current / goal * 100)) if goal > 0 else 0
            bar_filled = int(progress / 10)
            bar = '█' * bar_filled + '░' * (10 - bar_filled)
            
            embed = discord.Embed(color=hex_color('GOLD'))
            embed.description = f"""
╭─────────────────╮
   🎯 **{pretty_number(current)}** / **{pretty_number(goal)}**
   
   `{bar}` **{progress:.1f}%**
╰─────────────────╯"""
            await inter.response.send_message(embed=embed, ephemeral=True)
        except:
            await inter.response.send_message('`❌` Ingresa números válidos', ephemeral=True)

class CreatorToolsPanel(ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=None)
        self.cog, self.uid = cog, str(user_id)

    @ui.button(label='Estadísticas', style=discord.ButtonStyle.primary, emoji='📊', row=0)
    async def stats(self, inter: discord.Interaction, _):
        data = self.cog.tiktokers_data[self.uid]
        goal = data.get('follower_goal', 0)
        current = data.get('current_followers', 0)
        progress = min(100, (current / goal * 100)) if goal > 0 else 0
        bar_filled = int(progress / 10)
        bar = '█' * bar_filled + '░' * (10 - bar_filled)
        
        embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
        embed.set_author(name='Tus Estadísticas', icon_url=inter.user.display_avatar.url)
        embed.description = f"""
╭──── **RENDIMIENTO** ────╮

  `📹` Videos: **{pretty_number(data.get('total_posts', 0))}**
  `💖` Likes: **{pretty_number(data.get('total_likes', 0))}**
  `👁️` Alcance: **{pretty_number(data.get('total_views', 0))}**

╰──── **META** ────╯

  `{bar}` **{progress:.0f}%**
  **{pretty_number(current)}** / **{pretty_number(goal)}** seguidores"""
        await inter.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label='TikTok', style=discord.ButtonStyle.danger, emoji='🎵', row=0)
    async def quick_tiktok(self, inter: discord.Interaction, _):
        data = self.cog.tiktokers_data[self.uid]
        tiktok = data.get('tiktok', '')
        view = ui.View()
        view.add_item(ui.Button(label='Ir a TikTok', url=f'https://tiktok.com/@{tiktok}', emoji='🎵'))
        embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
        embed.description = f'🎵 **[@{tiktok}](https://tiktok.com/@{tiktok})**'
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(label='Redes', style=discord.ButtonStyle.secondary, emoji='🌐', row=0)
    async def socials(self, inter: discord.Interaction, _):
        await inter.response.send_modal(SocialLinksModal(self.cog, self.uid))

    @ui.button(label='Ver Redes', style=discord.ButtonStyle.secondary, emoji='🔗', row=0)
    async def view_socials(self, inter: discord.Interaction, _):
        data = self.cog.tiktokers_data[self.uid]
        socials = data.get('socials', {})
        tiktok = data.get('tiktok', '')
        
        links = [f"🎵 [@{tiktok}](https://tiktok.com/@{tiktok})"]
        if socials.get('instagram'): links.append(f"📸 [@{socials['instagram'].replace('@','')}](https://instagram.com/{socials['instagram'].replace('@','')})")
        if socials.get('youtube'): links.append(f"🎬 [{socials['youtube']}]({socials['youtube'] if 'http' in socials['youtube'] else f'https://youtube.com/@{socials['youtube']}'})")
        if socials.get('twitter'): links.append(f"🐦 [@{socials['twitter'].replace('@','')}](https://twitter.com/{socials['twitter'].replace('@','')})")
        if socials.get('twitch'): links.append(f"💜 [{socials['twitch']}](https://twitch.tv/{socials['twitch']})")
        
        embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
        embed.description = '\n'.join(links)
        await inter.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label='Meta', style=discord.ButtonStyle.success, emoji='🎯', row=1)
    async def follower_goal(self, inter: discord.Interaction, _):
        await inter.response.send_modal(FollowerGoalModal(self.cog, self.uid))

    @ui.button(label='Color', style=discord.ButtonStyle.secondary, emoji='🌈', row=1)
    async def color(self, inter: discord.Interaction, _):
        opts = [discord.SelectOption(label=n, value=n, emoji='🎨') for n in COLORS.keys()]
        sel = ui.Select(placeholder='Elige tu color...', options=opts)
        async def callback(it: discord.Interaction):
            self.cog.tiktokers_data[self.uid]['color'] = sel.values[0]
            save_tiktokers(self.cog.tiktokers_data)
            embed = discord.Embed(color=hex_color(sel.values[0]), description=f'`✅` Color: **{sel.values[0]}**')
            await it.response.send_message(embed=embed, ephemeral=True)
        sel.callback = callback
        await inter.response.send_message(view=ui.View().add_item(sel), ephemeral=True)

    @ui.button(label='Personalizar', style=discord.ButtonStyle.secondary, emoji='🎨', row=1)
    async def customize(self, inter: discord.Interaction, _):
        modal = ui.Modal(title='˚₊· ͟͟͞͞➳❥ Personalizar Canal')
        modal.add_item(ui.TextInput(label='Nombre del canal', placeholder='mi-rincon', max_length=20))
        async def on_submit(it: discord.Interaction):
            ch = it.guild.get_channel(self.cog.tiktokers_data[self.uid]['channel_id'])
            if ch:
                await ch.edit(name=f'✨・{modal.children[0].value}')
                await it.response.send_message(f'`✅` Canal: **{modal.children[0].value}**', ephemeral=True)
        modal.on_submit = on_submit
        await inter.response.send_modal(modal)

    @ui.button(label='Bio', style=discord.ButtonStyle.secondary, emoji='📝', row=1)
    async def bio(self, inter: discord.Interaction, _):
        modal = ui.Modal(title='˚₊· ͟͟͞͞➳❥ Tu Biografía')
        modal.add_item(ui.TextInput(label='Sobre ti', placeholder='Cuenta algo...', 
                                    default=self.cog.tiktokers_data[self.uid].get('bio', ''),
                                    max_length=150, style=discord.TextStyle.paragraph))
        async def on_submit(it: discord.Interaction):
            self.cog.tiktokers_data[self.uid]['bio'] = modal.children[0].value
            save_tiktokers(self.cog.tiktokers_data)
            await it.response.send_message('`✅` Bio actualizada', ephemeral=True)
        modal.on_submit = on_submit
        await inter.response.send_modal(modal)

    @ui.button(label='Notificaciones', style=discord.ButtonStyle.secondary, emoji='🔔', row=2)
    async def noti_role(self, inter: discord.Interaction, _):
        guild = inter.guild
        role_id = self.cog.tiktokers_data[self.uid].get('notify_role')
        role = guild.get_role(role_id) if role_id else None
        if role:
            await inter.response.send_message('`🔕` Ya tienes rol de notificaciones', ephemeral=True)
        else:
            role = await guild.create_role(name=f'🔔 {inter.user.name}', color=hex_color(self.cog.tiktokers_data[self.uid].get('color', 'PINK')), mentionable=True)
            await inter.user.add_roles(role)
            self.cog.tiktokers_data[self.uid]['notify_role'] = role.id
            save_tiktokers(self.cog.tiktokers_data)
            await inter.response.send_message('`🔔` Notificaciones activadas', ephemeral=True)

    @ui.button(label='Agendar', style=discord.ButtonStyle.secondary, emoji='📅', row=2)
    async def schedule(self, inter: discord.Interaction, _):
        modal = ui.Modal(title='˚₊· ͟͟͞͞➳❥ Programar Video')
        modal.add_item(ui.TextInput(label='Fecha/hora', placeholder='Mañana 5PM', max_length=40))
        async def on_submit(it: discord.Interaction):
            self.cog.tiktokers_data[self.uid]['next_post'] = modal.children[0].value
            save_tiktokers(self.cog.tiktokers_data)
            await it.response.send_message(f'`📅` Agendado: **{modal.children[0].value}**', ephemeral=True)
        modal.on_submit = on_submit
        await inter.response.send_modal(modal)

    @ui.button(label='Mi Agenda', style=discord.ButtonStyle.secondary, emoji='📆', row=2)
    async def view_schedule(self, inter: discord.Interaction, _):
        date = self.cog.tiktokers_data[self.uid].get('next_post', 'Sin programar')
        await inter.response.send_message(f'`📅` Próximo video: **{date}**', ephemeral=True)

    @ui.button(label='Regenerar Banner', style=discord.ButtonStyle.primary, emoji='🖼️', row=2)
    async def regen_banner(self, inter: discord.Interaction, _):
        await inter.response.defer(ephemeral=True)
        data = self.cog.tiktokers_data[self.uid]
        banner = await generate_creator_banner(data['tiktok'], str(inter.user.display_avatar.url), data.get('color', 'PINK'))
        file = discord.File(banner, filename='banner.png')
        await inter.followup.send('`✅` Banner regenerado:', file=file, ephemeral=True)

    @ui.button(label='Eliminar', style=discord.ButtonStyle.danger, emoji='🗑️', row=3)
    async def delete_channel(self, inter: discord.Interaction, _):
        if not inter.user.guild_permissions.administrator:
            return await inter.response.send_message('`❌` Solo admins', ephemeral=True)
        ch = inter.guild.get_channel(self.cog.tiktokers_data[self.uid]['channel_id'])
        if ch: await ch.delete()
        self.cog.tiktokers_data.pop(self.uid)
        save_tiktokers(self.cog.tiktokers_data)
        await inter.response.send_message('`🗑️` Canal eliminado', ephemeral=True)

class Tiktokers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktokers_data = load_tiktokers()

    @commands.command(name='t_setup')
    @commands.has_permissions(administrator=True)
    async def setup_tiktokers(self, ctx):
        embed = discord.Embed(color=hex_color('PINK'))
        embed.set_author(name='✧ TIKTOKER SPACE ✧', icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.description = """
╭───────────────────────╮
   ✨ **Centro de Creadores** ✨
╰───────────────────────╯

¿Eres creador de contenido en TikTok?
¡Únete y obtén tu espacio exclusivo!

➤ Canal personalizado
➤ Banner único con tu estilo
➤ Herramientas de creador"""
        try:
            file = discord.File(f'{BANNERS_PATH}/banner-t.png', filename='banner.png')
            embed.set_image(url='attachment://banner.png')
            await ctx.send(file=file, embed=embed, view=TiktokerRegisterView(self))
        except:
            await ctx.send(embed=embed, view=TiktokerRegisterView(self))

    @commands.command(name='tools', aliases=['panel-tools', 'panel'])
    async def creator_tools(self, ctx):
        uid = str(ctx.author.id)
        if uid not in self.tiktokers_data:
            return await ctx.send('`❌` Solo para creadores verificados', delete_after=5)
        
        data = self.tiktokers_data[uid]
        async with ctx.typing():
            banner = await generate_tools_banner(
                ctx.author.name, data['tiktok'], str(ctx.author.display_avatar.url),
                data.get('color', 'PINK'), data
            )
            file = discord.File(banner, filename='panel.png')
            
            embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
            embed.set_author(name=f'Panel de {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
            embed.set_image(url='attachment://panel.png')
            
            await ctx.send(file=file, embed=embed, view=CreatorToolsPanel(self, uid))

    @commands.command(name='subir')
    async def upload_video(self, ctx, video_url: str = None):
        uid = str(ctx.author.id)
        if uid not in self.tiktokers_data:
            return await ctx.send('`❌` No eres creador verificado', delete_after=5)
        if ctx.channel.id != self.tiktokers_data[uid]['channel_id']:
            return await ctx.send('`❌` Usa este comando en tu canal', delete_after=5)
        if not video_url or 'tiktok.com' not in video_url:
            return await ctx.send('`❌` Link de TikTok inválido', delete_after=5)
        
        await ctx.message.delete()
        data = self.tiktokers_data[uid]
        data['total_posts'] = data.get('total_posts', 0) + 1
        data['total_views'] = data.get('total_views', 0) + random.randint(50, 150)
        save_tiktokers(self.tiktokers_data)
        
        embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
        embed.set_author(name='Nuevo Video', icon_url=ctx.author.display_avatar.url)
        embed.description = f"""
╭───────────────────────╮
   🎬 **¡{ctx.author.name} subió video!**
╰───────────────────────╯

➤ [**Ver en TikTok**]({video_url})
➤ [@{data['tiktok']}](https://tiktok.com/@{data['tiktok']})"""
        
        socials = data.get('socials', {})
        if any(socials.values()):
            social_links = []
            if socials.get('instagram'): social_links.append(f"[📸](https://instagram.com/{socials['instagram'].replace('@','')})")
            if socials.get('youtube'): social_links.append(f"[🎬]({socials['youtube'] if 'http' in socials['youtube'] else f'https://youtube.com/@{socials['youtube']}'})")
            if socials.get('twitter'): social_links.append(f"[🐦](https://twitter.com/{socials['twitter'].replace('@','')})")
            if socials.get('twitch'): social_links.append(f"[💜](https://twitch.tv/{socials['twitch']})")
            embed.add_field(name='Redes', value=' '.join(social_links), inline=False)
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        view = VideoSupportView(self, ctx.author.id)
        role_id = data.get('notify_role')
        content = f'<@&{role_id}>' if role_id else None
        await ctx.send(content=content, embed=embed, view=view)

    @commands.command(name='user', aliases=['creador'])
    async def user_profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        uid = str(member.id)
        if uid not in self.tiktokers_data:
            return await ctx.send('`❌` Usuario no es creador', delete_after=5)
        
        data = self.tiktokers_data[uid]
        async with ctx.typing():
            banner = await generate_tools_banner(
                member.name, data['tiktok'], str(member.display_avatar.url),
                data.get('color', 'PINK'), data
            )
            file = discord.File(banner, filename='profile.png')
            
            bio = data.get('bio', 'Sin biografía')
            embed = discord.Embed(color=hex_color(data.get('color', 'PINK')))
            embed.set_author(name=f'Perfil de {member.name}', icon_url=member.display_avatar.url)
            embed.description = f'*{bio}*'
            embed.set_image(url='attachment://profile.png')
            
            socials = data.get('socials', {})
            if any(socials.values()):
                social_links = [f"[🎵](https://tiktok.com/@{data['tiktok']})"]
                if socials.get('instagram'): social_links.append(f"[📸](https://instagram.com/{socials['instagram'].replace('@','')})")
                if socials.get('youtube'): social_links.append(f"[🎬]({socials['youtube'] if 'http' in socials['youtube'] else f'https://youtube.com/@{socials['youtube']}'})")
                if socials.get('twitter'): social_links.append(f"[🐦](https://twitter.com/{socials['twitter'].replace('@','')})")
                if socials.get('twitch'): social_links.append(f"[💜](https://twitch.tv/{socials['twitch']})")
                embed.add_field(name='Redes', value=' '.join(social_links), inline=False)
            
            view = ui.View()
            view.add_item(ui.Button(label='TikTok', url=f'https://tiktok.com/@{data["tiktok"]}', emoji='🎵'))
            await ctx.send(file=file, embed=embed, view=view)

class VideoSupportView(ui.View):
    def __init__(self, cog, creator_id):
        super().__init__(timeout=None)
        self.cog, self.cid = cog, str(creator_id)
        self.voters = []

    @ui.button(label='Apoyar', style=discord.ButtonStyle.danger, emoji='💖', custom_id='support_btn')
    async def support(self, inter: discord.Interaction, _):
        if inter.user.id in self.voters:
            return await inter.response.send_message('`💖` Ya apoyaste este video', ephemeral=True)
        self.voters.append(inter.user.id)
        self.cog.tiktokers_data[self.cid]['total_likes'] = self.cog.tiktokers_data[self.cid].get('total_likes', 0) + 1
        save_tiktokers(self.cog.tiktokers_data)
        await inter.response.send_message('`💖` ¡Apoyo enviado!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tiktokers(bot))
