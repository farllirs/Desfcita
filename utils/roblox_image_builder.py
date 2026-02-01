"""
🎮 Roblox Image Builder - Crear imágenes de verificación con Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple
import io
import aiohttp

class RobloxImageBuilder:
    """Constructor de imágenes de verificación Roblox"""
    
    def __init__(self):
        self.fonts_dir = "fonts"
        self.title_font = self._load_font("classic.ttf", 50, bold=True)
        self.name_font = self._load_font("classic.ttf", 35)
        self.small_font = self._load_font("classic.ttf", 20)
        
    def _load_font(self, filename: str, size: int, bold: bool = False):
        """Cargar fuente con fallback"""
        path = os.path.join(self.fonts_dir, filename)
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()
    
    def _round_corners(self, img, radius=20):
        """Redondear esquinas de una imagen"""
        try:
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
            img.putalpha(mask)
            return img
        except:
            return img
    
    async def download_image(self, url: str, size: Tuple[int, int] = (150, 150)):
        """Descargar imagen de URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200:
                        img_data = await r.read()
                        img = Image.open(io.BytesIO(img_data))
                        img = img.convert('RGBA')
                        img.thumbnail(size, Image.Resampling.LANCZOS)
                        return self._round_corners(img, radius=15)
        except:
            pass
        
        # Fallback: crear imagen simple
        fallback = Image.new('RGBA', size, (100, 100, 100, 255))
        return self._round_corners(fallback, radius=15)
    
    def create_verification_card(self, 
                                 discord_name: str, 
                                 discord_avatar: Image.Image,
                                 roblox_name: str,
                                 roblox_avatar: Image.Image) -> Image.Image:
        """Crear tarjeta de verificación con ambos usuarios"""
        try:
            # Dimensiones
            w, h = 1000, 500
            
            # Fondo
            img = Image.new('RGBA', (w, h), (25, 25, 35, 255))
            draw = ImageDraw.Draw(img)
            
            # Marco principal
            draw.rectangle([(15, 15), (w-15, h-15)], outline=(255, 182, 193), width=3)
            
            # Línea divisoria en el medio
            mid_x = w // 2
            draw.line([(mid_x, 50), (mid_x, h-50)], fill=(255, 182, 193), width=2)
            
            # ═══════════════════════════════════════════════════════════
            # LADO IZQUIERDO - DISCORD
            # ═══════════════════════════════════════════════════════════
            
            # Título
            try:
                draw.text(
                    (50, 30),
                    "DISCORD",
                    font=self.title_font,
                    fill=(88, 101, 242, 255)  # Color Discord
                )
            except:
                pass
            
            # Foto de Discord
            avatar_x = 80
            avatar_y = 120
            img.paste(discord_avatar, (avatar_x, avatar_y), discord_avatar)
            
            # Nombre Discord
            try:
                draw.text(
                    (avatar_x, avatar_y + 170),
                    discord_name[:20],
                    font=self.name_font,
                    fill=(255, 255, 255, 255)
                )
            except:
                pass
            
            # ═══════════════════════════════════════════════════════════
            # LADO DERECHO - ROBLOX
            # ═══════════════════════════════════════════════════════════
            
            # Título
            try:
                draw.text(
                    (mid_x + 50, 30),
                    "ROBLOX",
                    font=self.title_font,
                    fill=(239, 124, 0, 255)  # Color Roblox
                )
            except:
                pass
            
            # Foto de Roblox
            avatar_x_right = mid_x + 80
            img.paste(roblox_avatar, (avatar_x_right, avatar_y), roblox_avatar)
            
            # Nombre Roblox
            try:
                draw.text(
                    (avatar_x_right, avatar_y + 170),
                    roblox_name[:20],
                    font=self.name_font,
                    fill=(255, 255, 255, 255)
                )
            except:
                pass
            
            # ═══════════════════════════════════════════════════════════
            # PIE - VERIFICADO
            # ═══════════════════════════════════════════════════════════
            
            # Línea decorativa inferior
            draw.line([(50, h-80), (w-50, h-80)], fill=(255, 182, 193), width=2)
            
            # Checkmark
            try:
                draw.text(
                    (420, h-60),
                    "✅ VERIFICADO",
                    font=self.small_font,
                    fill=(76, 224, 86, 255)  # Verde
                )
            except:
                pass
            
            return img
            
        except Exception as e:
            print(f"Error creating verification card: {e}")
            # Fallback: imagen simple
            return Image.new('RGBA', (1000, 500), (25, 25, 35, 255))
    
    async def create_verification_image(self,
                                       discord_name: str,
                                       discord_avatar_url: str,
                                       roblox_name: str,
                                       roblox_avatar_url: str) -> io.BytesIO:
        """Crear y retornar imagen de verificación como BytesIO"""
        
        # Descargar avatares
        discord_img = await self.download_image(discord_avatar_url, (150, 150))
        roblox_img = await self.download_image(roblox_avatar_url, (150, 150))
        
        # Crear tarjeta
        card = self.create_verification_card(
            discord_name,
            discord_img,
            roblox_name,
            roblox_img
        )
        
        # Convertir a BytesIO
        img_bytes = io.BytesIO()
        card.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def create_simple_verification(self, discord_name: str, roblox_name: str) -> Image.Image:
        """Crear tarjeta simple sin descargar imágenes"""
        try:
            w, h = 1000, 500
            img = Image.new('RGBA', (w, h), (25, 25, 35, 255))
            draw = ImageDraw.Draw(img)
            
            # Marco
            draw.rectangle([(15, 15), (w-15, h-15)], outline=(255, 182, 193), width=3)
            
            # Línea divisoria
            mid_x = w // 2
            draw.line([(mid_x, 50), (mid_x, h-50)], fill=(255, 182, 193), width=2)
            
            # DISCORD (izquierda)
            draw.text((50, 30), "DISCORD", font=self.title_font, fill=(88, 101, 242, 255))
            draw.text((50, 200), discord_name[:20], font=self.name_font, fill=(255, 255, 255, 255))
            draw.text((80, 150), "👤", font=self._load_font("google-emojis.ttf", 60))
            
            # ROBLOX (derecha)
            draw.text((mid_x + 50, 30), "ROBLOX", font=self.title_font, fill=(239, 124, 0, 255))
            draw.text((mid_x + 50, 200), roblox_name[:20], font=self.name_font, fill=(255, 255, 255, 255))
            draw.text((mid_x + 80, 150), "🎮", font=self._load_font("google-emojis.ttf", 60))
            
            # Verificado
            draw.line([(50, h-80), (w-50, h-80)], fill=(255, 182, 193), width=2)
            draw.text((420, h-60), "✅ VERIFICADO", font=self.small_font, fill=(76, 224, 86, 255))
            
            return img
        except:
            return Image.new('RGBA', (1000, 500), (25, 25, 35, 255))
