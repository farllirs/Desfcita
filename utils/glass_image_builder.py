"""
🎨 Glass Image Builder - Efectos glassmorphism tipo iPhone + Desfcita Branding
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import io
import os
from typing import Tuple

class GlassImageBuilder:
    """Constructor de imágenes con efecto glass iPhone + Desfcita"""
    
    def __init__(self):
        self.fonts_dir = "fonts"
        self.title_font = self._load_font("classic.ttf", 60, bold=True)
        self.name_font = self._load_font("classic.ttf", 40)
        self.small_font = self._load_font("classic.ttf", 22)
        self.brand_font = self._load_font("classic.ttf", 28)
    
    def _load_font(self, filename: str, size: int, bold: bool = False):
        """Cargar fuente con fallback"""
        path = os.path.join(self.fonts_dir, filename)
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()
    
    def _create_gradient_bg(self, width: int, height: int, color1: Tuple[int,int,int], color2: Tuple[int,int,int]) -> Image.Image:
        """Crear fondo con gradiente"""
        img = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(img)
        
        for y in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
        return img
    
    def _create_glass_panel(self, width: int, height: int, x: int, y: int) -> Image.Image:
        """Crear panel con efecto glass"""
        panel = Image.new('RGBA', (width, height), (255, 255, 255, 25))
        
        # Blur para efecto glass
        panel = panel.filter(ImageFilter.GaussianBlur(radius=8))
        
        # Borde sutil
        draw = ImageDraw.Draw(panel)
        draw.rectangle(
            [(0, 0), (width-1, height-1)],
            outline=(255, 255, 255, 100),
            width=2
        )
        
        return panel
    
    def create_verification_panel(self, roblox_username: str, roblox_id: int, bot_icon: Image.Image = None) -> io.BytesIO:
        """Crear panel de verificación con efecto glass y banner Desfcita + icono del bot"""
        w, h = 1400, 900
        
        # Gradiente premium: azul oscuro a púrpura a rosa
        bg = self._create_gradient_bg(w, h, (10, 15, 40), (60, 20, 100))
        
        # Añadir múltiples efectos de luz
        light = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light)
        
        # Luz superior
        light_draw.ellipse(
            [(w//2 - 400, -150), (w//2 + 400, 250)],
            fill=(120, 180, 255, 35)
        )
        # Luz inferior lateral
        light_draw.ellipse(
            [(-300, h - 300), (300, h + 200)],
            fill=(200, 100, 255, 25)
        )
        
        light = light.filter(ImageFilter.GaussianBlur(radius=150))
        bg = Image.alpha_composite(bg, light)
        
        draw = ImageDraw.Draw(bg)
        
        # ═══════════════════════════════════════════
        # BANNER PREMIUM DESFCITA (Superior)
        # ═══════════════════════════════════════════
        banner_height = 120
        banner = Image.new('RGBA', (w, banner_height), (0, 0, 0, 0))
        banner_draw = ImageDraw.Draw(banner)
        
        # Fondo premium del banner
        for y in range(banner_height):
            alpha = int(200 - (y / banner_height) * 100)
            banner_draw.line([(0, y), (w, y)], fill=(50, 20, 90, alpha))
        
        # Líneas decorativas brillantes
        banner_draw.line([(0, 0), (w, 0)], fill=(150, 200, 255, 255), width=3)
        banner_draw.line([(0, banner_height - 3), (w, banner_height - 3)], fill=(255, 100, 200, 200), width=3)
        
        # Icono del bot (izquierda) - GRANDE Y PROMINENTE
        if bot_icon:
            try:
                bot_icon_resized = bot_icon.resize((100, 100), Image.Resampling.LANCZOS)
                banner.paste(bot_icon_resized, (15, 10), bot_icon_resized)
            except:
                pass
        
        # Textos principales
        try:
            banner_draw.text(
                (130, 20),
                "DESFCITA",
                font=self.brand_font,
                fill=(150, 220, 255, 255)
            )
            banner_draw.text(
                (130, 55),
                "🎮 Verificación Roblox",
                font=self._load_font("classic.ttf", 20),
                fill=(200, 150, 255, 200)
            )
        except:
            pass
        
        # Separador de línea
        banner_draw.line([(w - 300, 15), (w - 300, 105)], fill=(150, 150, 200, 100), width=2)
        
        # Texto derecha
        try:
            banner_draw.text(
                (w - 280, 35),
                "✨ Sistema Premium",
                font=self._load_font("classic.ttf", 18),
                fill=(255, 255, 255, 200)
            )
        except:
            pass
        
        bg.paste(banner, (0, 0), banner)
        
        # ═══════════════════════════════════════════
        # CONTENIDO PRINCIPAL
        # ═══════════════════════════════════════════
        
        # Panel glass izquierda - Información del usuario
        info_panel = self._create_glass_panel(w//2 - 80, 480, 40, 130)
        bg.paste(info_panel, (40, 130), info_panel)
        
        y_offset = 170
        
        try:
            # Título
            draw.text(
                (80, y_offset),
                "👤 TU USUARIO ROBLOX",
                font=self.name_font,
                fill=(120, 200, 255, 255)
            )
            
            # Usuario
            draw.text(
                (80, y_offset + 70),
                roblox_username[:25],
                font=self.title_font,
                fill=(255, 255, 255, 255)
            )
            
            # Separador
            draw.line(
                [(80, y_offset + 140), (w//2 - 80, y_offset + 140)],
                fill=(150, 150, 200, 100),
                width=2
            )
            
            # ID
            draw.text(
                (80, y_offset + 160),
                f"🔢 ID: {roblox_id}",
                font=self.small_font,
                fill=(180, 180, 220, 255)
            )
        except:
            pass
        
        # Panel glass derecha - Instrucciones
        steps_panel = self._create_glass_panel(w//2 - 80, 480, w//2 + 40, 130)
        bg.paste(steps_panel, (w//2 + 40, 130), steps_panel)
        
        try:
            # Título
            draw.text(
                (w//2 + 80, y_offset),
                "📋 GUÍA DE VERIFICACIÓN",
                font=self.name_font,
                fill=(200, 150, 255, 255)
            )
            
            steps = [
                "① Haz clic en el botón 🔗 Ir al grupo",
                "② Únete a nuestro grupo de Roblox",
                "③ Haz clic en ✅ Ya me uní",
                "④ ¡Recibirás el rol automático!"
            ]
            
            for i, step in enumerate(steps):
                draw.text(
                    (w//2 + 80, y_offset + 70 + i*45),
                    step,
                    font=self.small_font,
                    fill=(255, 255, 255, 220)
                )
        except:
            pass
        
        # ═══════════════════════════════════════════
        # BANNER INFERIOR DECORATIVO
        # ═══════════════════════════════════════════
        footer_banner = Image.new('RGBA', (w, 90), (0, 0, 0, 0))
        footer_draw = ImageDraw.Draw(footer_banner)
        
        # Gradiente del pie
        for y in range(90):
            alpha = int((y / 90) * 180)
            footer_draw.line(
                [(0, y), (w, y)],
                fill=(30, 15, 60, alpha)
            )
        
        # Línea decorativa
        footer_draw.line([(40, 10), (w - 40, 10)], fill=(120, 200, 255, 150), width=2)
        
        try:
            footer_draw.text(
                (60, 30),
                "✅ Sistema de Verificación Automático",
                font=self.small_font,
                fill=(150, 180, 220, 200)
            )
            footer_draw.text(
                (w - 400, 30),
                "⚡ Discord Bot Desfcita",
                font=self.small_font,
                fill=(200, 150, 255, 200)
            )
        except:
            pass
        
        bg.paste(footer_banner, (0, h - 90), footer_banner)
        
        # Convertir a BytesIO
        img_bytes = io.BytesIO()
        bg.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def create_roblox_panel(self, group_id: int, server_name: str = "Servidor") -> io.BytesIO:
        """Crear panel de verificación Roblox mejorado y personalizado"""
        try:
            w, h = 1400, 750
            
            # Fondo degradado
            bg = self._create_gradient_bg(w, h, (15, 20, 45), (50, 25, 100))
            
            # Efectos de luz
            light = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            light_draw = ImageDraw.Draw(light)
            light_draw.ellipse([(w//2 - 500, -200), (w//2 + 500, 400)], fill=(150, 200, 255, 50))
            light = light.filter(ImageFilter.GaussianBlur(radius=200))
            bg = Image.alpha_composite(bg, light)
            
            draw = ImageDraw.Draw(bg)
            
            # ═══════════════════════════════════════
            # BANNER PRINCIPAL
            # ═══════════════════════════════════════
            banner_h = 150
            banner = Image.new('RGBA', (w, banner_h), (30, 15, 70, 200))
            banner_draw = ImageDraw.Draw(banner)
            
            # Líneas decorativas
            banner_draw.line([(0, 0), (w, 0)], fill=(120, 200, 255, 200), width=3)
            banner_draw.line([(0, banner_h-2), (w, banner_h-2)], fill=(150, 100, 255, 200), width=2)
            
            try:
                # Título grande
                title_font = self._load_font("classic.ttf", 70)
                banner_draw.text((70, 20), "🎮 ROBLOX", font=title_font, fill=(120, 200, 255, 255))
                
                # Subtítulo
                sub_font = self._load_font("classic.ttf", 30)
                banner_draw.text((500, 50), "Verificación de Cuenta", font=sub_font, fill=(200, 150, 255, 255))
            except:
                pass
            
            bg.paste(banner, (0, 0), banner)
            
            # ═══════════════════════════════════════
            # PANEL GLASS PRINCIPAL
            # ═══════════════════════════════════════
            panel = self._create_glass_panel(w - 80, 500, 40, 160)
            bg.paste(panel, (40, 160), panel)
            
            # Contenido
            try:
                y = 200
                
                # Título sección
                title_font = self._load_font("classic.ttf", 50)
                draw.text((80, y), "Únete al Grupo", font=title_font, fill=(120, 200, 255, 255))
                y += 70
                
                # Información del grupo
                info_font = self._load_font("classic.ttf", 28)
                draw.text((80, y), f"📍 ID del Grupo: {group_id}", font=info_font, fill=(255, 255, 255, 255))
                y += 50
                
                # Pasos
                step_font = self._load_font("classic.ttf", 24)
                steps = [
                    "1️⃣  Abre el enlace del grupo",
                    "2️⃣  Únete al grupo de Roblox",
                    "3️⃣  Haz clic en '✅ Ya me uní'",
                    "4️⃣  Recibirás tu rol automáticamente"
                ]
                
                for step in steps:
                    draw.text((80, y), step, font=step_font, fill=(255, 255, 255, 220))
                    y += 40
                
            except Exception as e:
                print(f"Error en contenido: {e}")
            
            # Footer
            footer_h = 60
            footer = Image.new('RGBA', (w, footer_h), (0, 0, 0, 0))
            footer_draw = ImageDraw.Draw(footer)
            
            for y_foot in range(footer_h):
                alpha = int((y_foot / footer_h) * 150)
                footer_draw.line([(0, y_foot), (w, y_foot)], fill=(30, 15, 60, alpha))
            
            try:
                footer_text = f"Grupo: {group_id} • Servidor: {server_name} • Sistema Automático"
                footer_draw.text((60, 15), footer_text, font=self._load_font("classic.ttf", 18), fill=(150, 180, 220, 200))
            except:
                pass
            
            bg.paste(footer, (0, h - footer_h), footer)
            
            img_bytes = io.BytesIO()
            bg.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            print(f"❌ Error en create_roblox_panel: {e}")
            import traceback
            traceback.print_exc()
            blank = Image.new('RGBA', (1400, 750), (30, 15, 60, 255))
            img_bytes = io.BytesIO()
            blank.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
    
    def create_intro_panel(self, server_icon: Image.Image = None) -> io.BytesIO:
        """Crear panel introductorio para el botón de verificación"""
        try:
            w, h = 1400, 650
            
            # Gradiente de fondo
            bg = self._create_gradient_bg(w, h, (15, 20, 45), (45, 25, 90))
            
            # Efectos de luz múltiples
            light = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            light_draw = ImageDraw.Draw(light)
            
            # Luz superior
            light_draw.ellipse(
                [(w//2 - 450, -200), (w//2 + 450, 300)],
                fill=(150, 200, 255, 40)
            )
            # Luz lateral
            light_draw.ellipse(
                [(-300, h//2 - 200), (200, h//2 + 200)],
                fill=(200, 100, 255, 30)
            )
            
            light = light.filter(ImageFilter.GaussianBlur(radius=180))
            bg = Image.alpha_composite(bg, light)
            
            draw = ImageDraw.Draw(bg)
            
            # ═════════════════════════════════════════
            # BANNER SUPERIOR DECORATIVO
            # ═════════════════════════════════════════
            banner_height = 100
            banner = Image.new('RGBA', (w, banner_height), (30, 15, 60, 220))
            banner_draw = ImageDraw.Draw(banner)
            
            # Línea superior
            banner_draw.line([(0, 0), (w, 0)], fill=(120, 200, 255, 150), width=2)
            # Línea inferior
            banner_draw.line([(0, banner_height - 2), (w, banner_height - 2)], fill=(120, 200, 255, 220), width=3)
            
            # Gradiente de fondo del banner
            for x in range(w):
                alpha = int(40 + (x / w) * 100)
                banner_draw.line([(x, 0), (x, banner_height)], fill=(80, 40, 140, alpha))
            
            # Icono servidor (izquierda)
            if server_icon:
                try:
                    icon_resized = server_icon.resize((80, 80), Image.Resampling.LANCZOS)
                    banner.paste(icon_resized, (15, 10), icon_resized)
                except:
                    pass
            
            # Logos
            try:
                banner_draw.text((120, 30), "✨ DESFCITA", font=self.brand_font, fill=(100, 200, 255, 255))
                banner_draw.text((w - 380, 35), "🎮 Verificación Roblox", font=self.brand_font, fill=(200, 150, 255, 255))
            except:
                pass
            
            bg.paste(banner, (0, 0), banner)
            
            # ═════════════════════════════════════════
            # PANEL GLASS PRINCIPAL
            # ═════════════════════════════════════════
            panel = self._create_glass_panel(w - 100, 480, 50, 120)
            bg.paste(panel, (50, 120), panel)
            
            # Contenido principal
            try:
                # Título
                draw.text(
                    (100, 160),
                    "🎮 SISTEMA DE VERIFICACIÓN ROBLOX",
                    font=self.title_font,
                    fill=(120, 200, 255, 255)
                )
                
                # Separador
                draw.line(
                    [(100, 230), (w - 100, 230)],
                    fill=(150, 150, 200, 100),
                    width=2
                )
                
                # Beneficios
                benefits = [
                    ("✨", "Verifica tu cuenta de Roblox"),
                    ("🎮", "Acceso exclusivo al grupo"),
                    ("🏆", "Roles y beneficios especiales"),
                    ("⚡", "Sistema automático y seguro")
                ]
                
                for i, (emoji, text) in enumerate(benefits):
                    y = 270 + i * 55
                    draw.text(
                        (120, y),
                        f"{emoji}  {text}",
                        font=self.small_font,
                        fill=(255, 255, 255, 230)
                    )
            except Exception as e:
                print(f"Error en contenido: {e}")
            
            # ═════════════════════════════════════════
            # FOOTER
            # ═════════════════════════════════════════
            footer_h = 50
            footer = Image.new('RGBA', (w, footer_h), (0, 0, 0, 0))
            footer_draw = ImageDraw.Draw(footer)
            
            # Gradiente footer
            for y in range(footer_h):
                alpha = int((y / footer_h) * 150)
                footer_draw.line(
                    [(0, y), (w, y)],
                    fill=(30, 15, 60, alpha)
                )
            
            try:
                footer_draw.text(
                    (60, 15),
                    "👇 Haz clic en el botón de abajo para comenzar",
                    font=self._load_font("classic.ttf", 16),
                    fill=(150, 180, 220, 200)
                )
            except:
                pass
            
            bg.paste(footer, (0, h - footer_h), footer)
            
            # Convertir a BytesIO
            img_bytes = io.BytesIO()
            bg.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            print(f"❌ Error crítico en create_intro_panel: {e}")
            import traceback
            traceback.print_exc()
            # Retornar imagen mínima
            blank = Image.new('RGBA', (1400, 650), (30, 15, 60, 255))
            img_bytes = io.BytesIO()
            blank.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
    
    def _hex_to_rgb(self, hex_color):
        """Convertir hex a RGB"""
        if isinstance(hex_color, int):
            # Si es entero, convertir
            return ((hex_color >> 16) & 255, (hex_color >> 8) & 255, hex_color & 255)
        
        hex_str = str(hex_color).replace("0x", "").replace("0X", "").replace("#", "")
        if len(hex_str) == 6:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return (230, 230, 250)
    
    def _wrap_text_dynamic(self, text: str, font, max_width: int, max_length: int = 80) -> list:
        """Dividir texto inteligentemente respetando ancho máximo"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = (current_line + " " + word).strip() if current_line else word
            
            # Si la línea es muy larga, partir
            if len(test_line) > max_length:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def create_suggestion_panel(self, config: dict) -> io.BytesIO:
        """Crear panel de sugerencias adaptable - VERSIÓN MEJORADA CON TAMAÑOS"""
        try:
            # Obtener tamaños de fuente personalizados
            titulo_size = config.get("titulo_size", 36)
            subtitulo_size = config.get("subtitulo_size", 20)
            mensaje_size = config.get("mensaje_size", 32)
            pasos_size = config.get("pasos_size", 18)
            footer_size = config.get("footer_size", 14)
            
            # Limitar tamaños máximos
            titulo_size = min(titulo_size, 50)
            subtitulo_size = min(subtitulo_size, 28)
            mensaje_size = min(mensaje_size, 40)
            pasos_size = min(pasos_size, 22)
            footer_size = min(footer_size, 18)
            
            # Dimensiones base
            w = 1400
            
            # Colores
            color_principal = config.get("color_principal", 0xE6E6FA)
            color_rgb = self._hex_to_rgb(color_principal)
            
            # Contenido
            titulo = config.get("titulo", "PANEL DE SUGERENCIAS")[:60]
            subtitulo = config.get("subtitulo", "Comparte tu feedback")[:100]
            mensaje_central = config.get("mensaje_central", "Tu opinión importa")[:150]
            pie_pagina = config.get("pie_pagina", "Sistema de sugerencias")[:100]
            
            # Crear fondo degradado
            bg = self._create_gradient_bg(w, 1200, (20, 15, 40), color_rgb)
            
            # Efecto de luz
            light = Image.new('RGBA', (w, 1200), (0, 0, 0, 0))
            light_draw = ImageDraw.Draw(light)
            light_draw.ellipse([(w//2 - 400, -150), (w//2 + 400, 300)], fill=(150, 200, 255, 45))
            light = light.filter(ImageFilter.GaussianBlur(radius=150))
            bg = Image.alpha_composite(bg, light)
            
            draw = ImageDraw.Draw(bg)
            
            # Panel glass principal
            panel = self._create_glass_panel(w - 60, 1140, 30, 30)
            bg.paste(panel, (30, 30), panel)
            
            # Cargar fuentes
            title_font = self._load_font("classic.ttf", titulo_size)
            subtitle_font = self._load_font("classic.ttf", subtitulo_size)
            mensaje_font = self._load_font("classic.ttf", mensaje_size)
            pasos_font = self._load_font("classic.ttf", pasos_size)
            footer_font = self._load_font("classic.ttf", footer_size)
            
            y_offset = 60
            x_padding = 70
            max_width = w - (2 * x_padding)
            
            # ═══════════════════════════════════════════
            # TÍTULO
            # ═══════════════════════════════════════════
            titulo_text = f"💡 {titulo}"
            titulo_lines = self._wrap_text_dynamic(titulo_text, title_font, max_width, 50)
            for line in titulo_lines:
                draw.text((x_padding, y_offset), line, font=title_font, fill=(150, 220, 255, 255))
                y_offset += titulo_size + 8
            
            y_offset += 10
            
            # ═══════════════════════════════════════════
            # SUBTÍTULO
            # ═══════════════════════════════════════════
            subtitulo_lines = self._wrap_text_dynamic(subtitulo, subtitle_font, max_width, 70)
            for line in subtitulo_lines:
                draw.text((x_padding, y_offset), line, font=subtitle_font, fill=(200, 180, 255, 220))
                y_offset += subtitulo_size + 6
            
            y_offset += 15
            
            # LÍNEA SEPARADORA
            draw.line([(x_padding, y_offset), (w - x_padding, y_offset)], fill=(150, 150, 200, 120), width=2)
            y_offset += 25
            
            # ═══════════════════════════════════════════
            # MENSAJE CENTRAL
            # ═══════════════════════════════════════════
            msg_lines = mensaje_central.split('\n')
            for line in msg_lines:
                wrapped = self._wrap_text_dynamic(line, mensaje_font, max_width, 40)
                for wline in wrapped:
                    # Centrar línea
                    draw.text((x_padding, y_offset), wline, font=mensaje_font, fill=(255, 255, 255, 255))
                    y_offset += mensaje_size + 8
            
            y_offset += 15
            
            # LÍNEA SEPARADORA
            draw.line([(x_padding, y_offset), (w - x_padding, y_offset)], fill=(150, 150, 200, 120), width=2)
            y_offset += 25
            
            # ═══════════════════════════════════════════
            # PASOS DE PARTICIPACIÓN
            # ═══════════════════════════════════════════
            emoji_like = config.get("emoji_like", "👍")
            emoji_dislike = config.get("emoji_dislike", "👎")
            
            steps = [
                f"1️⃣ {emoji_like} Envía tu sugerencia",
                f"2️⃣ 💬 La comunidad opina",
                f"3️⃣ {emoji_dislike} Se implementa"
            ]
            
            for step in steps:
                draw.text((x_padding, y_offset), step, font=pasos_font, fill=(255, 255, 255, 240))
                y_offset += pasos_size + 10
            
            y_offset += 15
            
            # ═══════════════════════════════════════════
            # PIE DE PÁGINA
            # ═══════════════════════════════════════════
            pie_lines = self._wrap_text_dynamic(pie_pagina, footer_font, max_width, 100)
            for line in pie_lines:
                draw.text((x_padding, y_offset), line, font=footer_font, fill=(180, 180, 220, 200))
                y_offset += footer_size + 4
            
            y_offset += 30
            
            # REDIMENSIONAR IMAGEN AL CONTENIDO
            h = min(y_offset + 40, 1500)  # Máximo 1500px
            
            # Crear imagen final con altura adaptada
            final_bg = self._create_gradient_bg(w, h, (20, 15, 40), color_rgb)
            
            # Efecto de luz
            light_final = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            light_draw_final = ImageDraw.Draw(light_final)
            light_draw_final.ellipse([(w//2 - 400, -150), (w//2 + 400, 300)], fill=(150, 200, 255, 45))
            light_final = light_final.filter(ImageFilter.GaussianBlur(radius=150))
            final_bg = Image.alpha_composite(final_bg, light_final)
            
            # Panel glass
            panel_final = self._create_glass_panel(w - 60, h - 60, 30, 30)
            final_bg.paste(panel_final, (30, 30), panel_final)
            
            # Copiar contenido de bg a final_bg
            draw_final = ImageDraw.Draw(final_bg)
            
            y_offset_final = 60
            
            # Redibujar TODO en la imagen final
            for line in titulo_lines:
                draw_final.text((x_padding, y_offset_final), line, font=title_font, fill=(150, 220, 255, 255))
                y_offset_final += titulo_size + 8
            y_offset_final += 10
            
            for line in subtitulo_lines:
                draw_final.text((x_padding, y_offset_final), line, font=subtitle_font, fill=(200, 180, 255, 220))
                y_offset_final += subtitulo_size + 6
            y_offset_final += 15
            
            draw_final.line([(x_padding, y_offset_final), (w - x_padding, y_offset_final)], fill=(150, 150, 200, 120), width=2)
            y_offset_final += 25
            
            for line in msg_lines:
                wrapped = self._wrap_text_dynamic(line, mensaje_font, max_width, 40)
                for wline in wrapped:
                    draw_final.text((x_padding, y_offset_final), wline, font=mensaje_font, fill=(255, 255, 255, 255))
                    y_offset_final += mensaje_size + 8
            y_offset_final += 15
            
            draw_final.line([(x_padding, y_offset_final), (w - x_padding, y_offset_final)], fill=(150, 150, 200, 120), width=2)
            y_offset_final += 25
            
            for step in steps:
                draw_final.text((x_padding, y_offset_final), step, font=pasos_font, fill=(255, 255, 255, 240))
                y_offset_final += pasos_size + 10
            y_offset_final += 15
            
            for line in pie_lines:
                draw_final.text((x_padding, y_offset_final), line, font=footer_font, fill=(180, 180, 220, 200))
                y_offset_final += footer_size + 4
            
            img_bytes = io.BytesIO()
            final_bg.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
        
        except Exception as e:
            import traceback
            print(f"Error en create_suggestion_panel: {e}")
            traceback.print_exc()
            # Fallback
            blank = Image.new('RGBA', (1400, 600), (30, 15, 60, 255))
            img_bytes = io.BytesIO()
            blank.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
    
    def create_suggestion_image(self, author: str, categoria: str, sugerencia: str, detalles: str) -> io.BytesIO:
        """Crear imagen de sugerencia con efecto glass"""
        w, h = 1200, 600
        
        # Gradiente de fondo
        bg = self._create_gradient_bg(w, h, (20, 30, 60), (50, 30, 80))
        
        # Luz decorativa
        light = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light)
        light_draw.ellipse([(w//2 - 300, -100), (w//2 + 300, 250)], fill=(150, 200, 255, 40))
        light = light.filter(ImageFilter.GaussianBlur(radius=150))
        bg = Image.alpha_composite(bg, light)
        
        draw = ImageDraw.Draw(bg)
        
        # Panel glass principal
        panel = self._create_glass_panel(w - 60, h - 60, 30, 30)
        bg.paste(panel, (30, 30), panel)
        
        # Contenido
        try:
            # Título
            draw.text((70, 50), "💡 SUGERENCIA", font=self.title_font, fill=(150, 200, 255, 255))
            
            # Categoría y autor
            draw.text((70, 110), f"📂 {categoria} • 👤 {author[:20]}", 
                     font=self._load_font("classic.ttf", 18), fill=(200, 180, 255, 200))
            
            # Línea separadora
            draw.line([(70, 140), (w - 70, 140)], fill=(150, 150, 200, 100), width=2)
            
            # Sugerencia principal
            y = 160
            for line in self._wrap_text(sugerencia, 80):
                draw.text((70, y), line, font=self._load_font("classic.ttf", 16), fill=(255, 255, 255, 230))
                y += 30
            
            # Detalles
            if detalles != "Sin detalles":
                y += 10
                draw.text((70, y), "📋 Detalles:", font=self._load_font("classic.ttf", 14), fill=(180, 180, 220, 200))
                y += 25
                for line in self._wrap_text(detalles, 80):
                    draw.text((85, y), line, font=self._load_font("classic.ttf", 14), fill=(200, 200, 230, 180))
                    y += 22
        
        except:
            pass
        
        # Convertir a BytesIO
        img_bytes = io.BytesIO()
        bg.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def _wrap_text(self, text: str, max_length: int) -> list:
        """Dividir texto en líneas"""
        words = text.split()
        lines = []
        current = ""
        
        for word in words:
            if len(current) + len(word) + 1 <= max_length:
                current += word + " "
            else:
                if current:
                    lines.append(current.strip())
                current = word + " "
        
        if current:
            lines.append(current.strip())
        
        return lines
    
    def create_profile_card(self, discord_name: str, discord_avatar: Image.Image, 
                           roblox_name: str, roblox_avatar: Image.Image) -> Image.Image:
        """Crear tarjeta de perfil con efecto glass"""
        w, h = 1200, 500
        
        # Gradiente: azul a cian
        bg = self._create_gradient_bg(w, h, (20, 40, 80), (30, 80, 120))
        
        # Efecto de luz
        light = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light)
        light_draw.ellipse(
            [(w//2 - 250, -50), (w//2 + 250, 250)],
            fill=(100, 180, 255, 40)
        )
        light = light.filter(ImageFilter.GaussianBlur(radius=120))
        bg = Image.alpha_composite(bg, light)
        
        draw = ImageDraw.Draw(bg)
        
        mid_x = w // 2
        
        # Panel glass izquierda - Discord
        discord_panel = self._create_glass_panel(mid_x - 40, h - 40, 20, 20)
        bg.paste(discord_panel, (20, 20), discord_panel)
        
        # Título Discord
        try:
            draw.text((60, 40), "DISCORD", font=self.title_font, fill=(88, 101, 242, 255))
        except:
            pass
        
        # Avatar Discord con borde glass
        avatar_x = 80
        avatar_y = 130
        discord_avatar_resized = discord_avatar.resize((120, 120), Image.Resampling.LANCZOS)
        bg.paste(discord_avatar_resized, (avatar_x, avatar_y), discord_avatar_resized)
        
        # Nombre Discord
        try:
            draw.text((avatar_x, avatar_y + 140), discord_name[:18], font=self.name_font, fill=(255, 255, 255, 255))
        except:
            pass
        
        # Panel glass derecha - Roblox
        roblox_panel = self._create_glass_panel(mid_x - 40, h - 40, mid_x + 20, 20)
        bg.paste(roblox_panel, (mid_x + 20, 20), roblox_panel)
        
        # Título Roblox
        try:
            draw.text((mid_x + 60, 40), "ROBLOX", font=self.title_font, fill=(239, 124, 0, 255))
        except:
            pass
        
        # Avatar Roblox con borde glass
        avatar_x_right = mid_x + 80
        roblox_avatar_resized = roblox_avatar.resize((120, 120), Image.Resampling.LANCZOS)
        bg.paste(roblox_avatar_resized, (avatar_x_right, avatar_y), roblox_avatar_resized)
        
        # Nombre Roblox
        try:
            draw.text((avatar_x_right, avatar_y + 140), roblox_name[:18], font=self.name_font, fill=(255, 255, 255, 255))
        except:
            pass
        
        return bg
