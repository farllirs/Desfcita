"""
🎨 Country Image Builder - Panel Visual de Países con Pillow
Crea imágenes hermosas de países usando fonts personalizadas
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, Tuple

class CountryImageBuilder:
    """Constructor de imágenes de países con diseño premium"""
    
    def __init__(self):
        self.fonts_dir = "fonts"
        self.emoji_font = self._load_font("google-emojis.ttf", 80)
        self.title_font = self._load_font("classic.ttf", 60, bold=True)
        self.text_font = self._load_font("classic.ttf", 35)
        self.small_font = self._load_font("classic.ttf", 25)
        
    def _load_font(self, filename: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Cargar fuente con fallback"""
        path = os.path.join(self.fonts_dir, filename)
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()
    
    def _color_to_rgb(self, color) -> Tuple[int, int, int]:
        """Convertir color (int hex o string) a RGB tuple"""
        if isinstance(color, int):
            return ((color >> 16) & 255, (color >> 8) & 255, color & 255)
        elif isinstance(color, str):
            if color.startswith("#"):
                color = color[1:]
            try:
                return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            except:
                return (200, 100, 200)  # Fallback magenta
        return (200, 100, 200)
    
    def create_country_panel(self, country: Dict) -> Image.Image:
        """Crear panel individual de país"""
        try:
            w, h = 800, 400
            
            # Colores
            bg_color = (25, 25, 35)
            accent_color = self._color_to_rgb(country.get("color", 0xFF69B4))
            border_color = accent_color
            
            # Crear imagen
            img = Image.new("RGB", (w, h), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Marco
            draw.rectangle(
                [(4, 4), (w-4, h-4)],
                outline=border_color,
                width=4
            )
            
            # Línea decorativa
            draw.line([(50, 120), (w-50, 120)], fill=border_color, width=2)
            
            # Bandera grande
            try:
                # Usar emoji_font para la bandera
                emoji = country.get("bandera", "🌍")
                draw.text((50, 15), emoji, font=self.emoji_font, fill="white")
            except:
                pass
            
            # Nombre del país
            try:
                draw.text(
                    (250, 40),
                    country.get("nombre", "País").upper(),
                    font=self.title_font,
                    fill="white"
                )
            except:
                pass
            
            # Decoración (sin mostrar hex)
            try:
                draw.text(
                    (60, 180),
                    "✨ Elige tu nación ✨",
                    font=self.small_font,
                    fill=accent_color
                )
            except:
                pass
            
            return img
        except Exception as e:
            # Fallback: imagen simple
            img = Image.new("RGB", (800, 400), (25, 25, 35))
            return img
    
    def create_countries_grid(self, countries: Dict, cols: int = 2) -> Image.Image:
        """Crear grid de países"""
        try:
            if not countries:
                return Image.new("RGB", (800, 600), (25, 25, 35))
            
            country_list = list(countries.items())
            rows = (len(country_list) + cols - 1) // cols
            
            panel_w, panel_h = 800, 400
            gap = 30
            
            total_w = cols * panel_w + (cols - 1) * gap + 100
            total_h = rows * panel_h + (rows - 1) * gap + 150
            
            grid_img = Image.new("RGB", (total_w, total_h), (15, 15, 25))
            
            # Header
            try:
                header_draw = ImageDraw.Draw(grid_img)
                header_font = self._load_font("classic.ttf", 50)
                header_draw.text(
                    (50, 30),
                    "NACIONES",
                    font=header_font,
                    fill=(255, 182, 193)
                )
            except:
                pass
            
            # Pegar paneles
            for idx, (key, country) in enumerate(country_list):
                try:
                    row = idx // cols
                    col = idx % cols
                    
                    x = 50 + col * (panel_w + gap)
                    y = 120 + row * (panel_h + gap)
                    
                    panel = self.create_country_panel(country)
                    grid_img.paste(panel, (x, y))
                except:
                    continue
            
            return grid_img
        except Exception as e:
            img = Image.new("RGB", (800, 600), (25, 25, 35))
            return img
    
    def create_profile_card(self, country: Dict, username: str) -> Image.Image:
        """Crear tarjeta de perfil"""
        try:
            w, h = 600, 400
            
            accent_color = self._color_to_rgb(country.get("color", 0xFF69B4))
            
            img = Image.new("RGB", (w, h), (25, 25, 35))
            draw = ImageDraw.Draw(img)
            
            # Marco
            draw.rectangle(
                [(10, 10), (w-10, h-10)],
                outline=accent_color,
                width=3
            )
            
            # Bandera
            try:
                draw.text((30, 50), country.get("bandera", "🌍"), font=self.emoji_font, fill="white")
            except:
                pass
            
            # Usuario
            try:
                draw.text(
                    (150, 70),
                    username[:20].upper(),
                    font=self.title_font,
                    fill="white"
                )
            except:
                pass
            
            # País
            try:
                draw.text(
                    (150, 150),
                    country.get("nombre", "País"),
                    font=self.text_font,
                    fill=accent_color
                )
            except:
                pass
            
            # Línea decorativa
            draw.line([(30, 280), (w-30, 280)], fill=accent_color, width=2)
            
            # Mensaje
            try:
                draw.text(
                    (50, 310),
                    "Representando con Orgullo",
                    font=self.small_font,
                    fill=(200, 200, 200)
                )
            except:
                pass
            
            return img
        except:
            img = Image.new("RGB", (600, 400), (25, 25, 35))
            return img
    
    def create_welcome_banner(self, guild_name: str, total_countries: int) -> Image.Image:
        """Crear banner de bienvenida"""
        try:
            w, h = 1200, 300
            
            img = Image.new("RGB", (w, h), (25, 25, 35))
            draw = ImageDraw.Draw(img)
            
            # Marco decorativo
            draw.rectangle([(10, 10), (w-10, h-10)], outline=(255, 182, 193), width=3)
            draw.line([(50, 90), (w-50, 90)], fill=(255, 182, 193), width=2)
            draw.line([(50, h-50), (w-50, h-50)], fill=(255, 182, 193), width=2)
            
            # Emojis decorativos en las esquinas
            try:
                emoji_font = self._load_font("google-emojis.ttf", 60)
                draw.text((w-120, 20), "🌍", font=emoji_font, fill="white")
                draw.text((50, h-80), "🌸", font=emoji_font, fill="white")
            except:
                pass
            
            # Título - Nombre del servidor
            try:
                title_font = self._load_font("classic.ttf", 70)
                name_text = guild_name.upper()[:25]
                draw.text(
                    (50, 15),
                    name_text,
                    font=title_font,
                    fill=(255, 182, 193)
                )
            except:
                pass
            
            # Subtítulo - Cantidad de naciones
            try:
                subtitle_font = self._load_font("classic.ttf", 45)
                draw.text(
                    (50, 130),
                    f"✨ {total_countries} Naciones Disponibles ✨",
                    font=subtitle_font,
                    fill=(200, 200, 200)
                )
            except:
                pass
            
            return img
        except:
            img = Image.new("RGB", (1200, 300), (25, 25, 35))
            return img
