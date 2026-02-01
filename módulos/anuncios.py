import discord
from discord.ext import commands, tasks
from discord import ui
import pytz
import math
from datetime import datetime, timedelta
import re
import json
import os
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict, fields
from enum import Enum
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import aiohttp
import textwrap
import random


class ConfigImagenes:
    ANCHO_BASE = 1200
    ALTO_BASE = 800
    MARGEN = 60

    PALETA_COLORES = {
        "cyan": (0, 191, 255),
        "dorado": (255, 215, 0),
        "morado": (155, 89, 182),
        "rojo": (255, 107, 107),
        "verde": (76, 175, 80),
        "azul": (52, 152, 219),
        "rosa": (255, 105, 180),
        "naranja": (255, 165, 0),
        "turquesa": (64, 224, 208),
        "coral": (255, 127, 80),
        "platino": (229, 228, 226),
        "obsidiana": (30, 30, 30),
        "esmeralda": (80, 200, 120)
    }

    # Rutas relativas para portabilidad
    FUENTE_TITULO = "./fonts/classic.ttf"
    FUENTE_BODY = "./fonts/classic.ttf"
    # Fallbacks del sistema (se intentarán si las anteriores fallan)
    FALLBACKS_SISTEMA = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "arial.ttf"
    ]
    FUENTE_EMOJI = "./fonts/emojis.ttf"

    TAMAÑO_TITULO = 70
    TAMAÑO_BODY = 40

    BLUR_RADIUS = 30
    RADIO_ESQUINAS = 50
    ICONO_TAMAÑO = 140
    LOGO_BOT_URL = "https://cdn.discordapp.com/embed/avatars/0.png" # Placeholder


class GeneradorImagenes:
    """Clase encargada de la generación de contenido visual con efectos de cristal (glass-morphism)."""
    
    def __init__(self):
        self.config = ConfigImagenes()
        self._cache_iconos = {}

    @lru_cache(maxsize=32)
    def _obtener_fuente_cache(self, ruta: Optional[str], tamaño: int):
        """
        💎 MOTOR DE CARGA DE FUENTES INTELIGENTE
        
        Optimiza el uso de memoria RAM y velocidad de renderizado mediante 
        un sistema de cache de último nivel (LRU).
        
        Args:
            ruta: Ruta al archivo .ttf (puede ser None para usar fallbacks).
            tamaño: Tamaño de la fuente en píxeles.
            
        Returns:
            ImageFont: Objeto de fuente listo para dibujar en el lienzo.
        """
        if ruta:
            try:
                return ImageFont.truetype(ruta, tamaño)
            except:
                pass
        
        for fallback in self.config.FALLBACKS_SISTEMA:
            try:
                return ImageFont.truetype(fallback, tamaño)
            except:
                continue
        return ImageFont.load_default()

    def _obtener_fuente(self, ruta: Optional[str], tamaño: int):
        return self._obtener_fuente_cache(ruta, tamaño)

    def _parsear_variables(self, texto: str, guild: discord.Guild, member: Optional[discord.Member] = None) -> str:
        """
        Motor de procesamiento de variables dinámicas v2.0.
        
        Soporta:
        - {user}: Nombre visible del usuario.
        - {user_mention}: Mención @usuario.
        - {user_tag}: Nombre#0000.
        - {server}: Nombre del servidor.
        - {server_id}: ID del servidor.
        - {count}: Número total de miembros.
        - {date}: Fecha actual (DD/MM/YYYY).
        - {time}: Hora actual (HH:MM).
        - {id}: Timestamp único.
        - {owner}: Nombre del dueño del servidor.
        - {boosts}: Nivel de boosters del servidor.
        """
        if not texto: return ""
        mapeo = {
            "{user}": member.display_name if member else "Usuario",
            "{user_mention}": member.mention if member else "@usuario",
            "{user_tag}": str(member) if member else "Usuario#0000",
            "{server}": guild.name,
            "{server_id}": str(guild.id),
            "{count}": str(guild.member_count),
            "{date}": datetime.now().strftime("%d/%m/%Y"),
            "{time}": datetime.now().strftime("%H:%M"),
            "{id}": str(int(datetime.now().timestamp())),
            "{owner}": str(guild.owner) if guild.owner else "Dueño",
            "{boosts}": str(guild.premium_subscription_count)
        }
        for k, v in mapeo.items():
            texto = texto.replace(k, v)
        return texto

    async def crear_imagen_anuncio(self, tipo: str, titulo: str, contenido: str,
                                   guild_icon_url: Optional[str] = None,
                                   color_personalizado: Optional[str] = None,
                                   fondo_url: Optional[str] = None,
                                   estilo: str = "moderno",
                                   guild_name: str = "Servidor",
                                   es_3d: bool = False,
                                   context_guild: Optional[discord.Guild] = None,
                                   context_member: Optional[discord.Member] = None) -> io.BytesIO:

        # Procesar variables si el contexto está disponible
        if context_guild:
            titulo = self._parsear_variables(titulo, context_guild, context_member)
            contenido = self._parsear_variables(contenido, context_guild, context_member)

        alto = self._calcular_altura(titulo, contenido)
        color_base = self.config.PALETA_COLORES.get(color_personalizado or tipo, (0, 191, 255))

        if fondo_url:
            img = await self._crear_fondo_personalizado(self.config.ANCHO_BASE, alto, fondo_url, color_base)
        else:
            img = self._crear_fondo_glass_iphone(self.config.ANCHO_BASE, alto, color_base, estilo)

        # Agregar partículas según estilo
        img = self._agregar_particulas(img, estilo, color_base)

        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Ajuste automático de fuentes
        tamaño_titulo = self._auto_ajustar_fuente(titulo, self.config.TAMAÑO_TITULO, 20)
        font_titulo = self._obtener_fuente(self.config.FUENTE_TITULO, tamaño_titulo)
        font_body = self._obtener_fuente(self.config.FUENTE_BODY, self.config.TAMAÑO_BODY)

        if guild_icon_url:
            overlay = await self._agregar_icono_servidor(overlay, guild_icon_url)

        y_offset = self.config.MARGEN + 180

        # Renderizar Título
        titulo_lines = textwrap.wrap(titulo, width=int(25 * (70/tamaño_titulo)))
        for line in titulo_lines:
            bbox = draw.textbbox((0, 0), line, font=font_titulo)
            w = bbox[2] - bbox[0]
            x = (self.config.ANCHO_BASE - w) // 2
            self._renderizar_texto_con_sombra(draw, (x, y_offset), line, font_titulo, (255, 255, 255, 255))
            y_offset += (bbox[3] - bbox[1]) + 20

        y_offset += 40

        # Renderizar Contenido
        contenido_lines = textwrap.wrap(contenido, width=40)
        for line in contenido_lines:
            bbox = draw.textbbox((0, 0), line, font=font_body)
            w = bbox[2] - bbox[0]
            x = (self.config.ANCHO_BASE - w) // 2
            self._renderizar_texto_con_sombra(draw, (x, y_offset), line, font_body, (240, 240, 240, 255), offset=2)
            y_offset += (bbox[3] - bbox[1]) + 15

        img = Image.alpha_composite(img, overlay)
        img = self._agregar_borde_glass(img, color_base)
        
        # Footer branding
        img = await self._renderizar_footer_imagen(img, guild_name)

        # Motor 3D Simulator
        if es_3d:
            img = self._aplicar_efecto_3d(img, color_base)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)

        return buffer

    async def crear_gif_anuncio(self, **kwargs) -> io.BytesIO:
        """
        Crea un anuncio animado (GIF) con efectos de brillo desplazándose.
        Requiere los mismos argumentos que crear_imagen_anuncio.
        """
        # Desactivar 3D temporalmente para GIFs por rendimiento
        kwargs["es_3d"] = False 
        
        frames = []
        num_frames = 10
        
        # Generar imagen base estática (sin overlay de brillo)
        # Para optimizar, generamos la base una vez y luego pegamos el brillo
        img_base_buffer = await self.crear_imagen_anuncio(**kwargs)
        img_base = Image.open(img_base_buffer).convert('RGBA')
        
        ancho, alto = img_base.size
        
        for i in range(num_frames):
            frame = img_base.copy()
            draw = ImageDraw.Draw(frame)
            
            # Dibujar un rayo de luz diagonal desplazándose
            offset = (i / num_frames) * (ancho + alto) - alto
            # Coordenadas: una banda diagonal
            puntos = [
                (offset, 0),
                (offset + 150, 0),
                (offset + 150 + alto, alto),
                (offset + alto, alto)
            ]
            
            # Capa de brillo
            overlay = Image.new('RGBA', frame.size, (0, 0, 0, 0))
            o_draw = ImageDraw.Draw(overlay)
            o_draw.polygon(puntos, fill=(255, 255, 255, 40))
            overlay = overlay.filter(ImageFilter.GaussianBlur(10))
            
            frame = Image.alpha_composite(frame, overlay)
            frames.append(frame)

        buffer = io.BytesIO()
        # Guardar como GIF animado optimizado
        frames[0].save(
            buffer, 
            format='GIF', 
            append_images=frames[1:], 
            save_all=True, 
            duration=100, 
            loop=0,
            optimize=True
        )
        buffer.seek(0)
        return buffer

    def _calcular_altura(self, titulo: str, contenido: str) -> int:
        titulo_lines = len(textwrap.wrap(titulo, width=25))
        contenido_lines = len(textwrap.wrap(contenido, width=35))

        altura_base = 500
        altura_titulo = titulo_lines * 90
        altura_contenido = contenido_lines * 60

        return max(self.config.ALTO_BASE, altura_base + altura_titulo + altura_contenido)

    async def _crear_fondo_personalizado(self, ancho: int, alto: int, url: str, color_base: tuple) -> Image.Image:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        bg = Image.open(io.BytesIO(data)).convert('RGBA')
                        bg = bg.resize((ancho, alto), Image.Resampling.LANCZOS)
                        bg = bg.filter(ImageFilter.GaussianBlur(15))
                        
                        # Capa de tinte color base
                        tinte = Image.new('RGBA', (ancho, alto), color_base + (100,))
                        bg = Image.alpha_composite(bg, tinte)
                        return bg
        except:
            pass
        return self._crear_fondo_glass_iphone(ancho, alto, color_base)

    def _renderizar_texto_con_sombra(self, draw, pos, texto, font, fill, shadow_fill=(0, 0, 0, 120), offset=4):
        x, y = pos
        draw.text((x + offset, y + offset), texto, fill=shadow_fill, font=font)
        draw.text((x, y), texto, fill=fill, font=font)

    def _auto_ajustar_fuente(self, texto: str, tamaño_max: int, largo_umbral: int) -> int:
        if len(texto) <= largo_umbral: return tamaño_max
        return max(30, tamaño_max - (len(texto) - largo_umbral) // 2)

    def _agregar_particulas(self, img: Image.Image, estilo: str, color_base: tuple) -> Image.Image:
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        ancho, alto = img.size

        if estilo == "cyberpunk":
            # Líneas de escaneo y circuitos neón
            for i in range(0, alto, 15):
                draw.line([(0, i), (ancho, i)], fill=(color_base[0], color_base[1], color_base[2], 30), width=1)
            for _ in range(15):
                x = random.randint(0, ancho)
                y = random.randint(0, alto)
                l = random.randint(50, 200)
                draw.line([(x, y), (x + l, y)], fill=(255, 0, 255, 80), width=2)
        
        elif estilo == "elegante":
            # Estrellas/Destellos suaves
            for _ in range(40):
                x, y = random.randint(0, ancho), random.randint(0, alto)
                r = random.randint(1, 3)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 215, 0, 150))
        
        return Image.alpha_composite(img, overlay)

    async def _renderizar_footer_imagen(self, img: Image.Image, guild_name: str) -> Image.Image:
        draw = ImageDraw.Draw(img)
        ancho, alto = img.size
        font_footer = self._obtener_fuente(self.config.FUENTE_BODY, 25)
        
        footer_text = f"© {datetime.now().year} {guild_name} | echo por DEX/NYX/FARLLIRS"
        bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
        fw = bbox[2] - bbox[0]
        
        # Barra semi-transparente al final
        bar_height = 50
        draw.rectangle([(0, alto - bar_height), (ancho, alto)], fill=(0, 0, 0, 100))
        draw.text(((ancho - fw)//2, alto - bar_height + 10), footer_text, fill=(200, 200, 200, 200), font=font_footer)
        
        return img

    def _aplicar_efecto_3d(self, img: Image.Image, color_base: tuple) -> Image.Image:
        """
        💎 MOTOR DE RENDERIZADO 3D SIMULATOR v1.0
        
        Aplica transformaciones espaciales a una imagen 2D para simular un panel
        de cristal flotando en un entorno tridimensional.
        
        Mecánicas aplicadas:
        1. Transformación Afin: Genera la perspectiva isométrica.
        2. Drop Shadow: Proyecta una sombra Gaussiana según el ángulo de la luz.
        3. Depth Extrusion: Añade un borde de grosor coloreado para simular volumen.
        
        Args:
            img: La imagen 2D ya renderizada.
            color_base: Color para las sombras y el grosor del cristal.
        """
        ancho, alto = img.size
        # Crear lienzo expandido para la sombra y perspectiva
        lienzo = Image.new('RGBA', (ancho + 100, alto + 100), (0, 0, 0, 0))
        
        # Sombra proyectada (Drop Shadow)
        sombra = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(sombra)
        s_draw.rectangle([0, 0, ancho, alto], fill=(0, 0, 0, 150))
        sombra = sombra.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Rotación leve para efecto isométrico (Simulado con transform)
        coeffs = (1, 0.05, -20, 0, 1, 0)
        img_transformed = img.transform((ancho + 50, alto + 50), Image.Transform.AFFINE, coeffs, Image.Resampling.BICUBIC)
        sombra_transformed = sombra.transform((ancho + 50, alto + 50), Image.Transform.AFFINE, coeffs, Image.Resampling.BICUBIC)
        
        lienzo.paste(sombra_transformed, (40, 40), sombra_transformed)
        lienzo.paste(img_transformed, (10, 10), img_transformed)
        
        # Añadir un "borde de grosor" lateral
        draw = ImageDraw.Draw(lienzo)
        grosor_color = (int(color_base[0]*0.4), int(color_base[1]*0.4), int(color_base[2]*0.4), 255)
        draw.line([(10+ancho, 10), (40+ancho, 40)], fill=grosor_color, width=5)
        draw.line([(10, 10+alto), (40, 40+alto)], fill=grosor_color, width=5)
        
        return lienzo

    async def analizar_branding_servidor(self, url: str) -> List[str]:
        """Analiza los colores predominantes del icono del servidor."""
        data = await self._descargar_imagen(url)
        if not data: return ["cyan", "dorado"]
        
        img = Image.open(io.BytesIO(data)).convert('RGB')
        img = img.resize((50, 50))
        img = img.quantize(colors=8).convert('RGB')
        colores = img.getcolors(50*50)
        if not colores: return ["cyan", "dorado"]
        colores.sort(key=lambda x: x[0], reverse=True)
        
        hex_colors = []
        for count, rgb in colores[:3]:
            hex_colors.append('#%02x%02x%02x' % rgb)
        return hex_colors

    def renderizar_grafica_barras(self, ancho: int, alto: int, votos: dict, titulo: str, color_base: tuple) -> Image.Image:
        """
        💎 MOTOR DE ANALÍTICAS VISUALES PRO
        
        Renderiza gráficas de barras de alta fidelidad con estilo glass-morphism.
        
        Características:
        - Escalado dinámico basado en el valor máximo de votos.
        - Etiquetas auto-truncadas para evitar desbordamiento.
        - Bordes suaves y sombras internas para un acabado premium.
        """
        img = self._crear_fondo_glass_iphone(ancho, alto, color_base, "elegante")
        draw = ImageDraw.Draw(img)
        font_titulo = self._obtener_fuente(self.config.FUENTE_TITULO, 50)
        font_texto = self._obtener_fuente(self.config.FUENTE_BODY, 30)
        
        bbox = draw.textbbox((0, 0), titulo, font=font_titulo)
        draw.text(((ancho-(bbox[2]-bbox[0]))//2, 50), titulo, fill=(255, 255, 255), font=font_titulo)
        
        if not votos:
            draw.text((ancho//2-100, alto//2), "Sin votos aún", fill=(255, 255, 255), font=font_texto)
            return img

        max_votos = max(votos.values()) if votos.values() else 1
        x_start, y_start = 150, 150
        chart_w, chart_h = ancho - 300, alto - 300
        bar_w = chart_w // len(votos) - 40
        
        for i, (opcion, cantidad) in enumerate(votos.items()):
            h = (cantidad / max_votos) * chart_h
            x = x_start + i * (bar_w + 40)
            y = y_start + (chart_h - h)
            draw.rectangle([x, y, x + bar_w, y_start + chart_h], fill=color_base + (180,), outline=(255, 255, 255, 200))
            draw.text((x + bar_w//2 - 10, y - 40), str(cantidad), fill=(255, 255, 255), font=font_texto)
            draw.text((x, y_start + chart_h + 20), str(opcion)[:10], fill=(255, 255, 255), font=font_texto)
            
        return self._agregar_borde_glass(img, color_base)

    def _crear_fondo_glass_iphone(self, ancho: int, alto: int, color_base: tuple, estilo: str = "moderno") -> Image.Image:
        img = Image.new('RGBA', (ancho, alto))
        draw = ImageDraw.Draw(img)

        # Gradiente base según estilo
        if estilo == "cyberpunk":
            c1, c2 = color_base, (255, 0, 255)
        elif estilo == "elegante":
            c1, c2 = color_base, (20, 20, 20)
        else: # moderno
            c1, c2 = color_base, (int(color_base[0]*0.6), int(color_base[1]*0.6), int(color_base[2]*0.6))

        for y in range(alto):
            f = y / alto
            r = int(c1[0]*(1-f) + c2[0]*f)
            g = int(c1[1]*(1-f) + c2[1]*f)
            b = int(c1[2]*(1-f) + c2[2]*f)
            draw.rectangle([(0, y), (ancho, y + 1)], fill=(r, g, b, 220))

        # Gradiente radial (Vignette)
        vignette = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        v_draw = ImageDraw.Draw(vignette)
        cx, cy = ancho // 2, alto // 2
        max_dist = (cx**2 + cy**2)**0.5
        for y in range(0, alto, 5):
            for x in range(0, ancho, 5):
                dist = ((x - cx)**2 + (y - cy)**2)**0.5
                factor = dist / max_dist
                alpha = int(100 * factor)
                v_draw.rectangle([x, y, x + 5, y + 5], fill=(0, 0, 0, alpha))
        
        img = Image.alpha_composite(img, vignette)
        img = self._agregar_burbujas_glass(img, color_base)
        img = img.filter(ImageFilter.GaussianBlur(radius=self.config.BLUR_RADIUS))

        overlay = Image.new('RGBA', img.size, (255, 255, 255, 30))
        img = Image.alpha_composite(img, overlay)

        # Ruido y destellos
        noise_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        noise_draw = ImageDraw.Draw(noise_overlay)
        for _ in range(700):
            x = random.randint(0, ancho)
            y = random.randint(0, alto)
            size = random.randint(1, 3)
            alpha = random.randint(10, 50)
            noise_draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, alpha))

        img = Image.alpha_composite(img, noise_overlay)
        return img

    def _agregar_burbujas_glass(self, img: Image.Image, color_base: tuple) -> Image.Image:
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        num_burbujas = random.randint(8, 15)

        for _ in range(num_burbujas):
            x = random.randint(0, img.size[0])
            y = random.randint(0, img.size[1])
            radio = random.randint(80, 250)

            r = min(255, int(color_base[0] * 1.3))
            g = min(255, int(color_base[1] * 1.3))
            b = min(255, int(color_base[2] * 1.3))
            alpha = random.randint(30, 70)

            draw.ellipse([x - radio, y - radio, x + radio, y + radio],
                        fill=(r, g, b, alpha))

            highlight_radio = radio // 3
            draw.ellipse([x - radio//2 - highlight_radio, y - radio//2 - highlight_radio,
                         x - radio//2 + highlight_radio, y - radio//2 + highlight_radio],
                        fill=(255, 255, 255, 50))

        return Image.alpha_composite(img, overlay)

    async def _descargar_imagen(self, url: str) -> Optional[bytes]:
        """Descarga una imagen con sistema de cache simple para evitar peticiones redundantes."""
        if url in self._cache_iconos:
            return self._cache_iconos[url]
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        self._cache_iconos[url] = data
                        # Limpiar cache si es muy grande
                        if len(self._cache_iconos) > 50:
                            self._cache_iconos.pop(next(iter(self._cache_iconos)))
                        return data
        except:
            pass
        return None

    async def _agregar_icono_servidor(self, img: Image.Image, icon_url: str) -> Image.Image:
        """
        Añade el icono del servidor con efecto de resplandor al overlay de la imagen.
        
        Args:
            img: Imagen base.
            icon_url: URL del icono del servidor.
        """
        icon_data = await self._descargar_imagen(icon_url)
        if icon_data:
            try:
                icon = Image.open(io.BytesIO(icon_data)).convert('RGBA')
                icon = icon.resize((self.config.ICONO_TAMAÑO, self.config.ICONO_TAMAÑO),
                                 Image.Resampling.LANCZOS)

                mask = Image.new('L', (self.config.ICONO_TAMAÑO, self.config.ICONO_TAMAÑO), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, self.config.ICONO_TAMAÑO, self.config.ICONO_TAMAÑO),
                                fill=255)

                icon.putalpha(mask)

                glow = Image.new('RGBA', (self.config.ICONO_TAMAÑO + 20,
                                          self.config.ICONO_TAMAÑO + 20), (0, 0, 0, 0))
                glow_draw = ImageDraw.Draw(glow)
                glow_draw.ellipse((0, 0, self.config.ICONO_TAMAÑO + 20,
                                  self.config.ICONO_TAMAÑO + 20),
                                 fill=(255, 255, 255, 60))
                glow = glow.filter(ImageFilter.GaussianBlur(10))

                x_pos = (img.size[0] - self.config.ICONO_TAMAÑO) // 2
                y_pos = 40

                img.paste(glow, (x_pos - 10, y_pos - 10), glow)
                img.paste(icon, (x_pos, y_pos), icon)
            except:
                pass

        return img

    def _agregar_borde_glass(self, img: Image.Image, color_base: tuple) -> Image.Image:
        draw = ImageDraw.Draw(img)
        r, g, b = [min(255, int(c * 1.5)) for c in color_base]

        for i in range(4):
            draw.rectangle(
                [(i, i), (img.size[0] - i - 1, img.size[1] - i - 1)],
                outline=(r, g, b, 150 - i * 30)
            )
        
        img = self._agregar_borde_letras(img, color_base)
        return img

    def _agregar_borde_letras(self, img: Image.Image, color_base: tuple) -> Image.Image:
        draw = ImageDraw.Draw(img)
        # Intentar cargar la fuente de emojis especial del usuario
        font_emoji = self._obtener_fuente(self.config.FUENTE_EMOJI, 30)
        # La fuente mapea 'a' y 'e' a emojis, así que usamos las letras normales
        letras = ["a", "e"]

        ancho, alto = img.size
        paso = 40
        
        # Color contrastado para las letras
        color_letra = (255, 255, 255, 180)

        for i in range(0, ancho, paso):
            # Arriba
            draw.text((i, 5), letras[(i//paso)%2], fill=color_letra, font=font_emoji)
            # Abajo
            draw.text((i, alto - 35), letras[(i//paso)%2], fill=color_letra, font=font_emoji)

        for i in range(0, alto, paso):
            # Izquierda
            draw.text((5, i), letras[(i//paso)%2], fill=color_letra, font=font_emoji)
            # Derecha
            draw.text((ancho - 30, i), letras[(i//paso)%2], fill=color_letra, font=font_emoji)

        return img

    async def crear_imagen_emblema(self, tipo: str, titulo: str, icon_url: Optional[str] = None, 
                                   color_personalizado: str = "dorado", es_3d: bool = False) -> io.BytesIO:
        ancho, alto = 600, 600
        color_base = self.config.PALETA_COLORES.get(color_personalizado, (255, 215, 0))
        
        # Crear base circular
        img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fondo glass circular
        fondo = self._crear_fondo_glass_iphone(ancho, alto, color_base)
        mask = Image.new('L', (ancho, alto), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((20, 20, ancho-20, alto-20), fill=255)
        
        emblema = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        emblema.paste(fondo, (0, 0), mask)
        
        # Borde de letras circular (aproximado)
        draw_emblema = ImageDraw.Draw(emblema)
        font_emoji = self._obtener_fuente(self.config.FUENTE_EMOJI, 40)
        letras = ["a", "e"]
            
        radio = ancho // 2 - 40
        centro = (ancho // 2, alto // 2)
        
        for i in range(36):
            angulo = math.radians(i * 10)
            x = centro[0] + radio * math.cos(angulo) - 15
            y = centro[1] + radio * math.sin(angulo) - 15
            draw_emblema.text((x, y), letras[i%2], fill=(255, 255, 255, 200), font=font_emoji)

        if icon_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url) as resp:
                    if resp.status == 200:
                        icon_data = await resp.read()
                        icon = Image.open(io.BytesIO(icon_data)).convert('RGBA')
                        icon = icon.resize((200, 200), Image.Resampling.LANCZOS)
                        
                        # Mascara circular para el icono
                        icon_mask = Image.new('L', (200, 200), 0)
                        ImageDraw.Draw(icon_mask).ellipse((0, 0, 200, 200), fill=255)
                        icon.putalpha(icon_mask)
                        
                        emblema.paste(icon, (ancho//2 - 100, alto//2 - 140), icon)

        # Header (Tipo)
        font_header = self._obtener_fuente(self.config.FUENTE_TITULO, 35)
        header_text = tipo.upper()
        bbox_h = draw_emblema.textbbox((0, 0), header_text, font=font_header)
        hw = bbox_h[2] - bbox_h[0]
        draw_emblema.text(((ancho - hw)//2, 80), header_text, fill=(255, 255, 255, 180), font=font_header)

        # Titulo
        font_titulo = self._obtener_fuente(self.config.FUENTE_TITULO, 50)
        bbox = draw_emblema.textbbox((0, 0), titulo, font=font_titulo)
        tw = bbox[2] - bbox[0]
        draw_emblema.text(((ancho - tw)//2, alto//2 + 80), titulo, fill=(255, 255, 255, 255), font=font_titulo)

        # Motor 3D para emblemas
        if es_3d:
            emblema = self._aplicar_efecto_3d(emblema, color_base)

        buffer = io.BytesIO()
        emblema.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer


class TipoAnuncio(Enum):
    ANUNCIO = "anuncio"
    EVENTO = "evento"
    ENCUESTA = "encuesta"
    NOTICIA = "noticia"
    SORTEO = "sorteo"


@dataclass
class AnuncioData:
    id: str
    tipo: str
    titulo: str
    contenido: str
    autor_id: int
    guild_id: int
    canal_id: int
    mensaje_id: Optional[int] = None
    fecha_creacion: str = None
    prioridad: str = "normal"
    color_usado: Optional[str] = None
    expiracion: Optional[str] = None
    recordatorio_enviado: bool = False
    plantilla_id: Optional[str] = None
    programado_para: Optional[str] = None
    estilo: str = "moderno"
    fondo_personalizado: Optional[str] = None
    participantes: List[int] = None
    ganadores_count: int = 1
    rsvps: Dict[str, List[int]] = None
    votos: Dict[str, List[int]] = None
    finalizado: bool = False
    requisitos: Dict[str, Any] = None
    es_3d: bool = False
    modo_hibrido: bool = False
    roles_recompensa: List[int] = None
    animado: bool = False
    variables_activas: bool = True
    meta_data: Dict[str, Any] = None

    def __post_init__(self):
        """Inicializa diccionarios y listas por defecto si son None."""
        if self.participantes is None: self.participantes = []
        if self.rsvps is None: self.rsvps = {"si": [], "no": [], "quizas": []}
        if self.votos is None: self.votos = {}
        if self.requisitos is None: self.requisitos = {"dias_min": 0, "roles_id": []}
        if self.roles_recompensa is None: self.roles_recompensa = []

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la dataclass a un diccionario serializable."""
        d = asdict(self)
        if d["meta_data"] is None: d["meta_data"] = {}
        return d

@dataclass
class PlantillaData:
    id: str
    nombre: str
    tipo: str
    titulo: str
    contenido: str
    color: str
    autor_id: int
    guild_id: int
    estilo: str = "moderno"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ConfigServidor:
    """Configuración persistente para cada servidor de Discord."""
    guild_id: int
    canal_anuncios: Optional[int] = None
    canal_logs: Optional[int] = None
    recordatorios_activos: bool = True
    idioma: str = "es"
    prefijo_personalizado: Optional[str] = None
    roles_admin: List[int] = None
    branding_colores: Optional[List[str]] = None
    recompensas_config: Dict[str, List[int]] = None
    canales_broadcast: List[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a dict."""
        d = asdict(self)
        if d["roles_admin"] is None: d["roles_admin"] = []
        if d["branding_colores"] is None: d["branding_colores"] = []
        if d["recompensas_config"] is None: d["recompensas_config"] = {}
        return d


class BaseDatos:
    """
    💎 GESTOR DE PERSISTENCIA DIAMOND EDITION
    
    Esta clase maneja toda la infraestructura de datos del bot, incluyendo:
    - Almacenamiento atómico de anuncios y eventos.
    - Sistema de plantillas globales por servidor.
    - Historial de logs administrativos para auditoría.
    - Configuraciones avanzadas de branding y recompensas.
    
    Utiliza una arquitectura de archivos JSON local con mecanismos de seguridad
    para prevenir la pérdida de datos y permitir migraciones automáticas entre versiones.
    """
    def __init__(self, ruta: str = "./data/anuncios_datos.json"):
        self.ruta = ruta
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        if not os.path.exists(self.ruta):
            with open(self.ruta, 'w', encoding='utf-8') as f:
                json.dump(self._default_data(), f, indent=2, ensure_ascii=False)

    def _default_data(self):
        return {
            "anuncios": [], "eventos": [], "encuestas": [],
            "noticias": [], "sorteos": [], "configuracion": {},
            "plantillas": [], "logs": [],
            "estadisticas": {"total_creados": 0, "imagenes_generadas": 0}
        }

    def cargar(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.ruta): return self._default_data()
            with open(self.ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Migración básica si faltan llaves
                default = self._default_data()
                for key in default:
                    if key not in data: data[key] = default[key]
                return data
        except:
            return self._default_data()

    def guardar(self, datos: Dict[str, Any]):
        with open(self.ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def agregar(self, tipo: str, anuncio: AnuncioData):
        datos = self.cargar()
        if tipo in datos:
            datos[tipo].append(anuncio.to_dict())
            datos["estadisticas"]["total_creados"] += 1
            self.guardar(datos)

    def obtener_por_servidor(self, guild_id: int) -> Dict[str, List]:
        datos = self.cargar()
        return {
            "anuncios": [a for a in datos.get("anuncios", []) if a["guild_id"] == guild_id],
            "eventos": [e for e in datos.get("eventos", []) if e["guild_id"] == guild_id],
            "encuestas": [e for e in datos.get("encuestas", []) if e["guild_id"] == guild_id],
            "noticias": [n for n in datos.get("noticias", []) if n["guild_id"] == guild_id],
            "sorteos": [s for s in datos.get("sorteos", []) if s["guild_id"] == guild_id]
        }

    def obtener_estadisticas_servidor(self, guild_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas detalladas filtradas por servidor."""
        datos = self.cargar()
        stats = {
            "anuncios": len([a for a in datos.get("anuncios", []) if a["guild_id"] == guild_id]),
            "eventos": len([a for a in datos.get("eventos", []) if a["guild_id"] == guild_id]),
            "encuestas": len([a for a in datos.get("encuestas", []) if a["guild_id"] == guild_id]),
            "noticias": len([a for a in datos.get("noticias", []) if a["guild_id"] == guild_id]),
            "sorteos": len([a for a in datos.get("sorteos", []) if a["guild_id"] == guild_id])
        }
        stats["total"] = sum(stats.values())
        return stats

    def obtener_estadisticas(self) -> Dict[str, Any]:
        datos = self.cargar()
        return {
            "anuncios": len(datos.get("anuncios", [])),
            "eventos": len(datos.get("eventos", [])),
            "encuestas": len(datos.get("encuestas", [])),
            "noticias": len(datos.get("noticias", [])),
            "sorteos": len(datos.get("sorteos", [])),
            "total": datos.get("estadisticas", {}).get("total_creados", 0)
        }

    def obtener_config(self, guild_id: int) -> ConfigServidor:
        datos = self.cargar()
        conf_dict = datos.get("configuracion", {}).get(str(guild_id), {})
        if not conf_dict: return ConfigServidor(guild_id=guild_id)
        # Quitar guild_id del dict para evitar duplicado en kwargs
        conf_dict.pop("guild_id", None)
        return ConfigServidor(guild_id=guild_id, **conf_dict)

    def guardar_config(self, config: ConfigServidor):
        datos = self.cargar()
        datos["configuracion"][str(config.guild_id)] = config.to_dict()
        self.guardar(datos)

    def establecer_canal_anuncios(self, guild_id: int, canal_id: int):
        config = self.obtener_config(guild_id)
        config.canal_anuncios = canal_id
        self.guardar_config(config)

    def obtener_canal_anuncios(self, guild_id: int) -> Optional[int]:
        return self.obtener_config(guild_id).canal_anuncios

    def registrar_log(self, guild_id: int, mensaje: str, nivel: str = "INFO"):
        datos = self.cargar()
        log_entry = {
            "fecha": datetime.now().isoformat(),
            "guild_id": guild_id,
            "mensaje": mensaje,
            "nivel": nivel
        }
        datos["logs"].append(log_entry)
        # Mantener solo los últimos 1000 logs
        if len(datos["logs"]) > 1000: datos["logs"] = datos["logs"][-1000:]
        self.guardar(datos)

    def guardar_plantilla(self, plantilla: PlantillaData):
        datos = self.cargar()
        datos["plantillas"].append(plantilla.to_dict())
        self.guardar(datos)

    def obtener_plantillas(self, guild_id: int) -> List[Dict[str, Any]]:
        datos = self.cargar()
        return [p for p in datos.get("plantillas", []) if p["guild_id"] == guild_id]

    def eliminar_plantilla(self, plantilla_id: str):
        datos = self.cargar()
        datos["plantillas"] = [p for p in datos.get("plantillas", []) if p["id"] != plantilla_id]
        self.guardar(datos)

    def eliminar_anuncio(self, tipo: str, anuncio_id: str):
        datos = self.cargar()
        if tipo in datos:
            datos[tipo] = [a for a in datos[tipo] if a["id"] != anuncio_id]
            self.guardar(datos)

    def obtener_todos_anuncios(self, guild_id: int) -> List[Dict[str, Any]]:
        datos = self.cargar()
        todos = []
        for tipo in ["anuncios", "eventos", "encuestas", "noticias", "sorteos"]:
            todos.extend([a for a in datos.get(tipo, []) if a["guild_id"] == guild_id])
        return todos


class VistaParticiparSorteo(ui.View):
    def __init__(self, db, sorteo_id: str):
        super().__init__(timeout=None)
        self.db = db
        self.sorteo_id = sorteo_id

    async def _validar_requisitos(self, member: discord.Member, requisitos: dict):
        if not requisitos: return True, ""
        dias_min = requisitos.get("dias_min", 0)
        if dias_min > 0 and member.joined_at:
            dias_en_guild = (datetime.now(pytz.utc) - member.joined_at).days
            if dias_en_guild < dias_min:
                return False, f"Necesitas al menos {dias_min} días en el servidor."
        roles_id = requisitos.get("roles_id", [])
        if roles_id:
            if not any(r.id in roles_id for r in member.roles):
                return False, "No tienes los roles requeridos para participar."
        return True, ""

    @ui.button(label="Participar", style=discord.ButtonStyle.success, emoji="🎉", custom_id="participar_sorteo")
    async def btn_participar(self, interaction: discord.Interaction, button: ui.Button):
        datos = self.db.cargar()
        sorteo = next((s for s in datos["sorteos"] if s["id"] == self.sorteo_id), None)
        
        if not sorteo or sorteo.get("finalizado"):
            return await interaction.response.send_message("❌ Este sorteo ya ha finalizado.", ephemeral=True)
        
        # Validar Requisitos
        pasa, msg = await self._validar_requisitos(interaction.user, sorteo.get("requisitos", {}))
        if not pasa:
            return await interaction.response.send_message(f"❌ **Requisito no cumplido:** {msg}", ephemeral=True)

        if interaction.user.id in sorteo.get("participantes", []):
            return await interaction.response.send_message("⚠️ Ya estás participando.", ephemeral=True)
        
        if "participantes" not in sorteo: sorteo["participantes"] = []
        sorteo["participantes"].append(interaction.user.id)
        self.db.guardar(datos)
        
        # Asignar roles de recompensa si existen
        roles_added = []
        for rid in sorteo.get("roles_recompensa", []):
            role = interaction.guild.get_role(rid)
            if role:
                try:
                    await interaction.user.add_roles(role)
                    roles_added.append(role.name)
                except: pass
        
        msg_extra = f"\n🎁 Roles otorgados: {', '.join(roles_added)}" if roles_added else ""
        await interaction.response.send_message(f"✅ ¡Ya estás participando, {interaction.user.name}!{msg_extra}", ephemeral=True)

class VistaRSVPEvento(ui.View):
    def __init__(self, db, evento_id: str):
        super().__init__(timeout=None)
        self.db = db
        self.evento_id = evento_id

    async def _validar(self, member):
        datos = self.db.cargar()
        evento = next((e for e in datos["eventos"] if e["id"] == self.evento_id), None)
        if not evento: return False, "Evento no encontrado."
        req = evento.get("requisitos", {})
        if req.get("dias_min", 0) > 0 and member.joined_at:
            if (datetime.now(pytz.utc) - member.joined_at).days < req["dias_min"]:
                return False, f"Mínimo {req['dias_min']} días en el servidor."
        return True, ""

    async def _update_rsvp(self, interaction: discord.Interaction, status: str):
        user_id = interaction.user.id
        datos = self.db.cargar()
        evento = next((e for e in datos["eventos"] if e["id"] == self.evento_id), None)
        if not evento: return False
        
        if "rsvps" not in evento: evento["rsvps"] = {"si": [], "no": [], "quizas": []}
        for s in ["si", "no", "quizas"]:
            if user_id in evento["rsvps"][s]: evento["rsvps"][s].remove(user_id)
            
        evento["rsvps"][status].append(user_id)
        self.db.guardar(datos)

        # Gestionar roles por RSVP
        for rid in evento.get("roles_recompensa", []):
            role = interaction.guild.get_role(rid)
            if role:
                try:
                    if status == "si": await interaction.user.add_roles(role)
                    else: await interaction.user.remove_roles(role)
                except: pass
        return True

    @ui.button(label="Asistiré", style=discord.ButtonStyle.success, emoji="✅", custom_id="rsvp_si")
    async def btn_si(self, interaction: discord.Interaction, button: ui.Button):
        pasa, msg = await self._validar(interaction.user)
        if not pasa: return await interaction.response.send_message(f"❌ {msg}", ephemeral=True)
        await self._update_rsvp(interaction, "si")
        await interaction.response.send_message("✅ Confirmada tu asistencia. Se te ha asignado el rol del evento.", ephemeral=True)

    @ui.button(label="Quizás", style=discord.ButtonStyle.secondary, emoji="🤔", custom_id="rsvp_quizas")
    async def btn_quizas(self, interaction: discord.Interaction, button: ui.Button):
        await self._update_rsvp(interaction, "quizas")
        await interaction.response.send_message("🤔 Marcado como posible asistencia.", ephemeral=True)

    @ui.button(label="No asistiré", style=discord.ButtonStyle.danger, emoji="❌", custom_id="rsvp_no")
    async def btn_no(self, interaction: discord.Interaction, button: ui.Button):
        await self._update_rsvp(interaction, "no")
        await interaction.response.send_message("❌ Confirmado que no asistirás. Se ha removido tu rol del evento.", ephemeral=True)

    @ui.button(label="Quizás", style=discord.ButtonStyle.secondary, emoji="🤔", custom_id="rsvp_quizas")
    async def btn_quizas(self, interaction: discord.Interaction, button: ui.Button):
        await self._update_rsvp(interaction.user.id, "quizas")
        await interaction.response.send_message("🤔 Marcado como posible asistencia.", ephemeral=True)

    @ui.button(label="No asistiré", style=discord.ButtonStyle.danger, emoji="❌", custom_id="rsvp_no")
    async def btn_no(self, interaction: discord.Interaction, button: ui.Button):
        await self._update_rsvp(interaction.user.id, "no")
        await interaction.response.send_message("❌ Confirmado que no asistirás.", ephemeral=True)


class VistaVotarEncuesta(ui.View):
    def __init__(self, db, encuesta_id: str, opciones: list):
        super().__init__(timeout=None)
        self.db = db
        self.encuesta_id = encuesta_id
        for i, op in enumerate(opciones):
            btn = ui.Button(label=op[:20], style=discord.ButtonStyle.secondary, custom_id=f"vote_{encuesta_id}_{i}")
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            datos = self.db.cargar()
            enc = next((e for e in datos["encuestas"] if e["id"] == self.encuesta_id), None)
            if not enc: return await interaction.response.send_message("❌ Error", ephemeral=True)
            
            if "votos" not in enc: enc["votos"] = {}
            user_id = str(interaction.user.id)
            
            # Un solo voto por persona
            for k, v in enc["votos"].items():
                if user_id in v: v.remove(user_id)
            
            idx_str = str(index)
            if idx_str not in enc["votos"]: enc["votos"][idx_str] = []
            enc["votos"][idx_str].append(user_id)
            
            self.db.guardar(datos)
            await interaction.response.send_message("✅ Voto registrado.", ephemeral=True)
        return callback

    @ui.button(label="Ver Resultados", style=discord.ButtonStyle.primary, emoji="📊", custom_id="ver_resultados", row=4)
    async def btn_resultados(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        datos = self.db.cargar()
        enc = next((e for e in datos["encuestas"] if e["id"] == self.encuesta_id), None)
        
        # Generar imagen de resultados
        votos_final = {enc["contenido"].split("|")[int(k)]: len(v) for k, v in enc.get("votos", {}).items()}
        color_base = ConfigImagenes.PALETA_COLORES.get(enc.get("color_usado", "cyan"), (0, 191, 255))
        
        generador = GeneradorImagenes()
        img_buffer = io.BytesIO()
        img = generador.renderizar_grafica_barras(1000, 700, votos_final, enc["titulo"], color_base)
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        file = discord.File(fp=img_buffer, filename="resultados.png")
        await interaction.followup.send("📊 Aquí tienes los resultados actuales:", file=file, ephemeral=True)


class SelectorConfig(ui.View):
    def __init__(self, ctx, db, generador, tipo_anuncio: str, timeout=300):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.db = db
        self.generador = generador
        self.tipo_anuncio = tipo_anuncio
        self.color = "cyan"
        self.estilo = "moderno"
        self.es_3d = False
        self.animado = False
        self.hibrido = False
        self.requisitos = {"dias_min": 0, "roles_id": []}

    @ui.select(
        placeholder="🎨 Color base",
        options=[
            discord.SelectOption(label="Cyan", value="cyan", emoji="💠"),
            discord.SelectOption(label="Dorado", value="dorado", emoji="✨"),
            discord.SelectOption(label="Morado", value="morado", emoji="🔮"),
            discord.SelectOption(label="Platino", value="platino", emoji="⚪"),
            discord.SelectOption(label="Obsidiana", value="obsidiana", emoji="⚫"),
            discord.SelectOption(label="Esmeralda", value="esmeralda", emoji="🟢")
        ]
    )
    async def select_color(self, interaction: discord.Interaction, select: ui.Select):
        self.color = select.values[0]
        await interaction.response.edit_message(view=self)

    @ui.select(
        placeholder="🎭 Estilo visual",
        options=[
            discord.SelectOption(label="Moderno (Suave)", value="moderno", emoji="📱"),
            discord.SelectOption(label="Elegante (Oscuro)", value="elegante", emoji="🎩"),
            discord.SelectOption(label="Cyberpunk (Neón)", value="cyberpunk", emoji="🌆")
        ]
    )
    async def select_estilo(self, interaction: discord.Interaction, select: ui.Select):
        self.estilo = select.values[0]
        await interaction.response.edit_message(view=self)

    @ui.button(label="3D: OFF", style=discord.ButtonStyle.secondary, emoji="🧊", row=2)
    async def btn_3d(self, interaction: discord.Interaction, button: ui.Button):
        self.es_3d = not self.es_3d
        button.label = f"3D: {'ON' if self.es_3d else 'OFF'}"
        button.style = discord.ButtonStyle.success if self.es_3d else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    @ui.button(label="GIF: OFF", style=discord.ButtonStyle.secondary, emoji="🎞️", row=2)
    async def btn_anim(self, interaction: discord.Interaction, button: ui.Button):
        self.animado = not self.animado
        button.label = f"GIF: {'ON' if self.animado else 'OFF'}"
        button.style = discord.ButtonStyle.success if self.animado else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    @ui.button(label="Híbrido: OFF", style=discord.ButtonStyle.secondary, emoji="🔗", row=2)
    async def btn_hibrid(self, interaction: discord.Interaction, button: ui.Button):
        self.hibrido = not self.hibrido
        button.label = f"Híbrido: {'ON' if self.hibrido else 'OFF'}"
        button.style = discord.ButtonStyle.success if self.hibrido else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    @ui.button(label="Config. Requisitos", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def btn_reqs(self, interaction: discord.Interaction, button: ui.Button):
        class ModalReqs(ui.Modal, title="🛡️ Configurar Requisitos"):
            dias = ui.TextInput(label="Días mínimos en el servidor", placeholder="0 para desactivar", default="0")
            roles = ui.TextInput(label="IDs de roles (separados por coma)", placeholder="ID1, ID2...", required=False)

            def __init__(self, parent):
                super().__init__()
                self.parent = parent

            async def on_submit(self, inter: discord.Interaction):
                try:
                    self.parent.requisitos["dias_min"] = int(self.dias.value)
                    r_ids = [int(r.strip()) for r in self.roles.value.split(",") if r.strip().isdigit()]
                    self.parent.requisitos["roles_id"] = r_ids
                    await inter.response.send_message("✅ Requisitos guardados para este anuncio.", ephemeral=True)
                except:
                    await inter.response.send_message("❌ Error en el formato.", ephemeral=True)

        await interaction.response.send_modal(ModalReqs(self))

    @ui.button(label="Previsualizar", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def btn_preview(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        # Generar una imagen de prueba rápida
        img_buffer = await self.generador.crear_imagen_anuncio(
            tipo=self.tipo_anuncio,
            titulo="Título de Ejemplo",
            contenido="Este es un contenido de ejemplo para mostrar cómo se verá el estilo seleccionado.",
            color_personalizado=self.color,
            estilo=self.estilo
        )
        file = discord.File(fp=img_buffer, filename="preview.png")
        await interaction.followup.send("🖼️ Aquí tienes una previsualización de tu diseño:", file=file, ephemeral=True)

    @ui.button(label="Continuar", style=discord.ButtonStyle.success, emoji="➡️")
    async def btn_continuar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ No tienes permiso", ephemeral=True)

        kwargs = {
            "db": self.db, "ctx": self.ctx, "generador": self.generador, 
            "color": self.color, "estilo": self.estilo, "es_3d": self.es_3d,
            "animado": self.animado, "hibrido": self.hibrido,
            "requisitos": self.requisitos, "cog": self.ctx.cog
        }

        if self.tipo_anuncio == "anuncio":
            await interaction.response.send_modal(ModalAnuncio(**kwargs))
        elif self.tipo_anuncio == "evento":
            await interaction.response.send_modal(ModalEvento(**kwargs))
        elif self.tipo_anuncio == "encuesta":
            await interaction.response.send_modal(ModalEncuesta(**kwargs))
        elif self.tipo_anuncio == "noticia":
            await interaction.response.send_modal(ModalNoticia(**kwargs))
        elif self.tipo_anuncio == "sorteo":
            await interaction.response.send_modal(ModalSorteo(**kwargs))
        elif self.tipo_anuncio == "emblema":
            # El emblema necesita saber el tipo específicamente
            kwargs.pop("requisitos")
            await interaction.response.send_modal(ModalEmblema(tipo=self.tipo_anuncio, **kwargs))


class PanelPrincipal(ui.View):
    def __init__(self, ctx, db, generador, pagina=1):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.db = db
        self.generador = generador
        self.pagina = pagina
        self._set_buttons()

    def _set_buttons(self):
        # Limpiar items existentes antes de añadir nuevos si fuera dinámico puro
        # Pero como usamos decoradores, controlaremos visibilidad/estado o usaremos sub-vistas
        pass

    def _check_user(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    async def _send_config_view(self, interaction: discord.Interaction, tipo: str, color_embed: int):
        embed = discord.Embed(
            title="🎨 Configuración Visual Pro",
            description=f"Personaliza el estilo para tu **{tipo}**",
            color=color_embed
        )
        view = SelectorConfig(self.ctx, self.db, self.generador, tipo)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(label="📢 Anuncio", style=discord.ButtonStyle.primary, row=0)
    async def btn_anuncio(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "anuncio", 0x00BFFF)

    @ui.button(label="🗓️ Evento", style=discord.ButtonStyle.primary, row=0)
    async def btn_evento(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "evento", 0xFFD700)

    @ui.button(label="📊 Encuesta", style=discord.ButtonStyle.primary, row=0)
    async def btn_encuesta(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "encuesta", 0x9B59B6)

    @ui.button(label="📰 Noticia", style=discord.ButtonStyle.success, row=1)
    async def btn_noticia(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "noticia", 0xFF6B6B)

    @ui.button(label="🎁 Sorteo", style=discord.ButtonStyle.success, row=1)
    async def btn_sorteo(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "sorteo", 0x4CAF50)

    @ui.button(label="🛡️ Emblema", style=discord.ButtonStyle.success, row=1)
    async def btn_emblema(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        await self._send_config_view(interaction, "emblema", 0xFFD700)

    @ui.button(label="Plantillas", style=discord.ButtonStyle.secondary, emoji="📁", row=1)
    async def btn_plantillas(self, interaction: discord.Interaction, button: ui.Button):
        plantillas = self.db.obtener_plantillas(self.ctx.guild.id)
        if not plantillas:
            return await interaction.response.send_message("❌ No tienes plantillas guardadas", ephemeral=True)
        
        embed = discord.Embed(title="📁 Mis Plantillas", color=discord.Color.blue())
        view = ui.View()
        options = [discord.SelectOption(label=p["nombre"], value=p["id"]) for p in plantillas[:25]]
        select = ui.Select(placeholder="Elige una plantilla", options=options)
        
        async def select_callback(inter: discord.Interaction):
            pid = select.values[0]
            p = next(pt for pt in plantillas if pt["id"] == pid)
            # Aquí se aplicaría la plantilla abriendo el modal correspondiente pre-rellenado
            await inter.response.send_message(f"✅ Plantilla `{p['nombre']}` seleccionada. (Función en desarrollo)", ephemeral=True)
        
        select.callback = select_callback
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(label="📜 Historial", style=discord.ButtonStyle.secondary, emoji="📚", row=2)
    async def btn_historial(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        anuncios = self.db.obtener_todos_anuncios(self.ctx.guild.id)
        if not anuncios:
            return await interaction.response.send_message("❌ No hay historial disponible.", ephemeral=True)
        
        view = VistaPaginacion(anuncios)
        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

    @ui.button(label="🛠️ Editor Live", style=discord.ButtonStyle.secondary, emoji="✏️", row=2)
    async def btn_editor(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        class ModalInputID(ui.Modal, title="✏️ Editor de Anuncios"):
            aid = ui.TextInput(label="ID del Anuncio", placeholder="Ej: 1712345678900")
            def __init__(self, cog):
                super().__init__()
                self.cog = cog
            async def on_submit(self, inter: discord.Interaction):
                # Llamar al comando editar internamente
                await self.cog.editar(inter, self.aid.value)
        await interaction.response.send_modal(ModalInputID(self.ctx.cog))

    @ui.button(label="Config Pro", style=discord.ButtonStyle.danger, emoji="⚙️", row=2)
    async def btn_config(self, interaction: discord.Interaction, button: ui.Button):
        if not self._check_user(interaction): return
        config = self.db.obtener_config(self.ctx.guild.id)
        view = VistaConfigPro(self.db, config, self.generador)
        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)


class VistaConfigPro(ui.View):
    """Interfaz avanzada para la configuración de características Premium del servidor."""
    def __init__(self, db, config, generador):
        super().__init__(timeout=300)
        self.db = db
        self.config = config
        self.generador = generador

    def get_embed(self):
        embed = discord.Embed(title="⚙️ Centro de Configuración Platinum", color=discord.Color.red())
        embed.description = "Gestiona las funciones avanzadas y el branding visual de tu servidor."
        embed.add_field(name="Canal de Logs", value=f"<#{self.config.canal_logs}>" if self.config.canal_logs else "`No definido`", inline=True)
        embed.add_field(name="Notificaciones", value="🔔 `Activadas`" if self.config.recordatorios_activos else "🔕 `Desactivadas`", inline=True)
        
        branding_info = ", ".join([f"`{c}`" for c in self.config.branding_colores]) if self.config.branding_colores else "`Por defecto`"
        embed.add_field(name="🎨 Paleta de Branding", value=branding_info, inline=False)
        embed.set_footer(text="Glass Announcements v10.0 Platinum")
        return embed

    @ui.button(label="🔔 Notificaciones", style=discord.ButtonStyle.secondary)
    async def toggle_reminders(self, inter: discord.Interaction, btn: ui.Button):
        self.config.recordatorios_activos = not self.config.recordatorios_activos
        self.db.guardar_config(self.config)
        await inter.response.edit_message(embed=self.get_embed(), view=self)

    @ui.button(label="🎨 Analizar Branding", style=discord.ButtonStyle.success, emoji="🖌️")
    async def auto_branding(self, inter: discord.Interaction, btn: ui.Button):
        await inter.response.defer(ephemeral=True)
        url = inter.guild.icon.url if inter.guild.icon else None
        if not url: return await inter.followup.send("❌ El servidor requiere un icono para el análisis.", ephemeral=True)
        
        colores = await self.generador.analizar_branding_servidor(url)
        self.config.branding_colores = colores
        self.db.guardar_config(self.config)
        await inter.followup.send(f"✅ Análisis completado. Colores detectados: `{colores}`", ephemeral=True)
        await inter.edit_original_response(embed=self.get_embed())

    @ui.button(label="🎁 Configurar Recompensas", style=discord.ButtonStyle.primary, emoji="🏅")
    async def config_rewards(self, inter: discord.Interaction, btn: ui.Button):
        class ModalRewards(ui.Modal, title="🏅 Configurar Roles de Recompensa"):
            sorteo_roles = ui.TextInput(label="Roles por Sorteo (IDs separados por ,)", required=False)
            evento_roles = ui.TextInput(label="Roles por Evento (IDs separados por ,)", required=False)

            def __init__(self, parent):
                super().__init__()
                self.parent = parent

            async def on_submit(self, inter_modal: discord.Interaction):
                try:
                    s_roles = [int(r.strip()) for r in self.sorteo_roles.value.split(",") if r.strip().isdigit()]
                    e_roles = [int(r.strip()) for r in self.evento_roles.value.split(",") if r.strip().isdigit()]
                    self.parent.config.recompensas_config = {"sorteos": s_roles, "eventos": e_roles}
                    self.parent.db.guardar_config(self.parent.config)
                    await inter_modal.response.send_message("✅ Configuración de recompensas guardada.", ephemeral=True)
                except:
                    await inter_modal.response.send_message("❌ Formato de IDs inválido.", ephemeral=True)

        await inter.response.send_modal(ModalRewards(self))

    @ui.button(label="📊 Reset Stats", style=discord.ButtonStyle.danger)
    async def reset_stats(self, inter: discord.Interaction, btn: ui.Button):
        await inter.response.send_message("⚠️ Esta función requiere confirmación manual vía `/borrar-todo`.", ephemeral=True)


class VistaPaginacion(ui.View):
    def __init__(self, data: list, per_page: int = 5):
        super().__init__(timeout=180)
        self.data = data
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(data) - 1) // per_page + 1

    def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        items = self.data[start:end]
        
        embed = discord.Embed(title=f"📚 Historial de Anuncios (Pág {self.current_page + 1}/{self.total_pages})", color=0x5865F2)
        for i, item in enumerate(items):
            embed.add_field(
                name=f"{i+1}. {item['titulo'][:50]}",
                value=f"ID: `{item['id']}` | Tipo: `{item['tipo']}`\nCreado: <t:{int(datetime.fromisoformat(item['fecha_creacion']).timestamp())}:d>",
                inline=False
            )
        return embed

    @ui.button(label="Anterior", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def btn_prev(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @ui.button(label="Siguiente", style=discord.ButtonStyle.gray, emoji="➡️")
    async def btn_next(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)


class ModalEmblema(ui.Modal, title="🛡️ Crear Emblema"):
    titulo = ui.TextInput(label="Nombre del Emblema", max_length=50, placeholder="Ej: Miembro VIP")

    def __init__(self, db, ctx, generador, color: str, tipo: str, es_3d: bool = False, cog=None, **kwargs):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.tipo = tipo
        self.es_3d = es_3d
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        imagen_buffer = await self.generador.crear_imagen_emblema(
            tipo=self.tipo,
            titulo=self.titulo.value,
            icon_url=icon_url,
            color_personalizado=self.color,
            es_3d=self.es_3d
        )

        archivo = discord.File(fp=imagen_buffer, filename="emblema_glass.png")
        await interaction.followup.send(file=archivo, ephemeral=True)


class ModalAnuncio(ui.Modal, title="📢 Crear Anuncio"):
    titulo = ui.TextInput(label="Título del Anuncio", max_length=100, placeholder="Escribe un título llamativo...")
    contenido = ui.TextInput(label="Contenido", style=discord.TextStyle.long, max_length=1500, placeholder="Describe tu anuncio...")
    fondo_url = ui.TextInput(label="URL de Fondo (Opcional)", placeholder="https://imagen.com/fondo.jpg", required=False)

    def __init__(self, db, ctx, generador, color: str, estilo: str, es_3d: bool, animado: bool, hibrido: bool, requisitos: dict, cog):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.estilo = estilo
        self.es_3d = es_3d
        self.animado = animado
        self.hibrido = hibrido
        self.requisitos = requisitos
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        canal_id = self.db.obtener_canal_anuncios(self.ctx.guild.id)
        canal = self.ctx.bot.get_channel(canal_id) if canal_id else self.ctx.channel

        if not canal:
            return await interaction.followup.send("❌ Canal no válido", ephemeral=True)

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        gen_kwargs = {
            "tipo": "anuncio",
            "titulo": self.titulo.value,
            "contenido": self.contenido.value,
            "guild_icon_url": icon_url,
            "color_personalizado": self.color,
            "fondo_url": self.fondo_url.value,
            "estilo": self.estilo,
            "guild_name": self.ctx.guild.name,
            "es_3d": self.es_3d
        }

        if self.animado:
            imagen_buffer = await self.generador.crear_gif_anuncio(**gen_kwargs)
            ext = "gif"
        else:
            imagen_buffer = await self.generador.crear_imagen_anuncio(**gen_kwargs)
            ext = "png"

        filename = f"anuncio_glass.{ext}"
        
        anuncio_obj = AnuncioData(
            id=str(int(datetime.now().timestamp() * 1000)),
            tipo=TipoAnuncio.ANUNCIO.value,
            titulo=self.titulo.value,
            contenido=self.contenido.value,
            autor_id=self.ctx.author.id,
            guild_id=self.ctx.guild.id,
            canal_id=canal.id,
            color_usado=self.color,
            estilo=self.estilo,
            es_3d=self.es_3d,
            animado=self.animado,
            modo_hibrido=self.hibrido,
            requisitos=self.requisitos
        )

        if self.hibrido:
            msg = await self.cog._enviar_anuncio_hibrido(canal, anuncio_obj, imagen_buffer, filename)
        else:
            imagen_buffer.seek(0)
            archivo = discord.File(fp=imagen_buffer, filename=filename)
            msg = await canal.send(file=archivo)

        anuncio_obj.mensaje_id = msg.id
        anuncio_obj.fecha_creacion = datetime.now().isoformat()
        self.db.agregar("anuncios", anuncio_obj)
        # Realizar broadcast
        await self.cog._realizar_broadcast(self.ctx.guild, anuncio_obj, imagen_buffer, filename)

        embed = discord.Embed(
            title="✅ Anuncio Publicado",
            description=f"ID: `{anuncio_obj.id}`\nColor: **{self.color.title()}**",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class ModalEvento(ui.Modal, title="🗓️ Crear Evento"):
    titulo = ui.TextInput(label="Título del Evento", max_length=100)
    hora = ui.TextInput(label="Hora", placeholder="HH:MM o DD/MM HH:MM", max_length=20)
    descripcion = ui.TextInput(label="Descripción", style=discord.TextStyle.long, max_length=1500)
    fondo_url = ui.TextInput(label="URL de Fondo (Opcional)", required=False)

    def __init__(self, db, ctx, generador, color: str, estilo: str, es_3d: bool, animado: bool, hibrido: bool, requisitos: dict, cog):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.estilo = estilo
        self.es_3d = es_3d
        self.animado = animado
        self.hibrido = hibrido
        self.requisitos = requisitos
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        evento_dt = self._parse_datetime(self.hora.value)
        if not evento_dt:
            return await interaction.followup.send("❌ Formato inválido. Usa `HH:MM` o `DD/MM HH:MM`", ephemeral=True)

        tz_col = pytz.timezone("America/Bogota")
        evento_dt = tz_col.localize(evento_dt) if evento_dt.tzinfo is None else evento_dt

        hora_12h = self._format_12h(evento_dt)
        contenido_completo = f"{self.descripcion.value}\n\n⏰ {hora_12h}"

        canal_id = self.db.obtener_canal_anuncios(self.ctx.guild.id)
        canal = self.ctx.bot.get_channel(canal_id) if canal_id else self.ctx.channel

        if not canal:
            return await interaction.followup.send("❌ Canal no válido", ephemeral=True)

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        gen_kwargs = {
            "tipo": "evento",
            "titulo": self.titulo.value,
            "contenido": contenido_completo,
            "guild_icon_url": icon_url,
            "color_personalizado": self.color,
            "fondo_url": self.fondo_url.value,
            "estilo": self.estilo,
            "guild_name": self.ctx.guild.name,
            "es_3d": self.es_3d
        }

        if self.animado:
            imagen_buffer = await self.generador.crear_gif_anuncio(**gen_kwargs)
            ext = "gif"
        else:
            imagen_buffer = await self.generador.crear_imagen_anuncio(**gen_kwargs)
            ext = "png"

        evento_id = str(int(datetime.now().timestamp() * 1000))
        filename = f"evento_glass.{ext}"
        
        evento_obj = AnuncioData(
            id=evento_id,
            tipo=TipoAnuncio.EVENTO.value,
            titulo=self.titulo.value,
            contenido=self.descripcion.value,
            autor_id=self.ctx.author.id,
            guild_id=self.ctx.guild.id,
            canal_id=canal.id,
            fecha_creacion=datetime.now().isoformat(),
            color_usado=self.color,
            expiracion=evento_dt.isoformat(),
            estilo=self.estilo,
            es_3d=self.es_3d,
            animado=self.animado,
            modo_hibrido=self.hibrido,
            requisitos=self.requisitos
        )

        view = VistaRSVPEvento(self.db, evento_id)
        if self.hibrido:
            msg = await self.cog._enviar_anuncio_hibrido(canal, evento_obj, imagen_buffer, filename, view=view)
        else:
            imagen_buffer.seek(0)
            archivo = discord.File(fp=imagen_buffer, filename=filename)
            msg = await canal.send(file=archivo, view=view)

        evento_obj.mensaje_id = msg.id
        self.db.agregar("eventos", evento_obj)
        # Realizar broadcast
        await self.cog._realizar_broadcast(self.ctx.guild, evento_obj, imagen_buffer, filename)

        embed = discord.Embed(
            title="✅ Evento Creado",
            description=f"ID: `{evento_id}`\nColor: **{self.color.title()}**",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    def _parse_datetime(self, input_str: str) -> Optional[datetime]:
        tz_col = pytz.timezone("America/Bogota")
        ahora = datetime.now(tz_col)

        match_full = re.match(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})", input_str)
        if match_full:
            day, month, hour, minute = map(int, match_full.groups())
            try:
                dt = ahora.replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if dt < ahora:
                    dt = dt.replace(year=ahora.year + 1)
                return dt
            except ValueError:
                return None

        match_time = re.match(r"(\d{1,2}):(\d{1,2})", input_str)
        if match_time:
            hour, minute = map(int, match_time.groups())
            dt = ahora.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if dt < ahora:
                dt += timedelta(days=1)
            return dt

        return None

    def _format_12h(self, dt: datetime) -> str:
        hour = dt.strftime("%I:%M")
        if dt.hour < 12:
            period = "de la mañana"
        elif dt.hour < 19:
            period = "de la tarde"
        else:
            period = "de la noche"
        return f"{hour} {period}"


class ModalEncuesta(ui.Modal, title="📊 Crear Encuesta"):
    titulo = ui.TextInput(label="Título de la Encuesta", max_length=100)
    opciones = ui.TextInput(label="Opciones", placeholder="Opción 1 | Opción 2 | Opción 3", style=discord.TextStyle.long, max_length=500)
    fondo_url = ui.TextInput(label="URL de Fondo (Opcional)", required=False)

    def __init__(self, db, ctx, generador, color: str, estilo: str, es_3d: bool, animado: bool, hibrido: bool, requisitos: dict, cog):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.estilo = estilo
        self.es_3d = es_3d
        self.animado = animado
        self.hibrido = hibrido
        self.requisitos = requisitos
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        lista_opciones = [opt.strip() for opt in self.opciones.value.split("|")]

        if len(lista_opciones) < 2 or len(lista_opciones) > 10:
            return await interaction.followup.send("❌ Mínimo 2, máximo 10 opciones", ephemeral=True)

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        contenido_encuesta = "\n".join([f"{emojis[i]} {op}" for i, op in enumerate(lista_opciones)])

        canal_id = self.db.obtener_canal_anuncios(self.ctx.guild.id)
        canal = self.ctx.bot.get_channel(canal_id) if canal_id else self.ctx.channel

        if not canal:
            return await interaction.followup.send("❌ Canal no válido", ephemeral=True)

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        gen_kwargs = {
            "tipo": "encuesta",
            "titulo": self.titulo.value,
            "contenido": contenido_encuesta,
            "guild_icon_url": icon_url,
            "color_personalizado": self.color,
            "fondo_url": self.fondo_url.value,
            "estilo": self.estilo,
            "guild_name": self.ctx.guild.name,
            "es_3d": self.es_3d
        }

        if self.animado:
            imagen_buffer = await self.generador.crear_gif_anuncio(**gen_kwargs)
            ext = "gif"
        else:
            imagen_buffer = await self.generador.crear_imagen_anuncio(**gen_kwargs)
            ext = "png"

        enc_id = str(int(datetime.now().timestamp() * 1000))
        filename = f"encuesta_glass.{ext}"
        
        encuesta_obj = AnuncioData(
            id=enc_id,
            tipo=TipoAnuncio.ENCUESTA.value,
            titulo=self.titulo.value,
            contenido="|".join(lista_opciones),
            autor_id=self.ctx.author.id,
            guild_id=self.ctx.guild.id,
            canal_id=canal.id,
            fecha_creacion=datetime.now().isoformat(),
            color_usado=self.color,
            estilo=self.estilo,
            es_3d=self.es_3d,
            animado=self.animado,
            modo_hibrido=self.hibrido,
            requisitos=self.requisitos
        )

        view = VistaVotarEncuesta(self.db, enc_id, lista_opciones)
        if self.hibrido:
            msg = await self.cog._enviar_anuncio_hibrido(canal, encuesta_obj, imagen_buffer, filename, view=view)
        else:
            imagen_buffer.seek(0)
            archivo = discord.File(fp=imagen_buffer, filename=filename)
            msg = await canal.send(file=archivo, view=view)

        encuesta_obj.mensaje_id = msg.id
        self.db.agregar("encuestas", encuesta_obj)
        # Realizar broadcast
        await self.cog._realizar_broadcast(self.ctx.guild, encuesta_obj, imagen_buffer, filename)

        embed = discord.Embed(
            title="✅ Encuesta Creada",
            description=f"ID: `{encuesta.id}`\nColor: **{self.color.title()}**",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class ModalNoticia(ui.Modal, title="📰 Crear Noticia"):
    titulo = ui.TextInput(label="Título de la Noticia", max_length=100)
    contenido = ui.TextInput(label="Contenido", style=discord.TextStyle.long, max_length=1500)
    fondo_url = ui.TextInput(label="URL de Fondo (Opcional)", required=False)

    def __init__(self, db, ctx, generador, color: str, estilo: str, es_3d: bool, animado: bool, hibrido: bool, requisitos: dict, cog):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.estilo = estilo
        self.es_3d = es_3d
        self.animado = animado
        self.hibrido = hibrido
        self.requisitos = requisitos
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        canal_id = self.db.obtener_canal_anuncios(self.ctx.guild.id)
        canal = self.ctx.bot.get_channel(canal_id) if canal_id else self.ctx.channel

        if not canal:
            return await interaction.followup.send("❌ Canal no válido", ephemeral=True)

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        gen_kwargs = {
            "tipo": "noticia",
            "titulo": self.titulo.value,
            "contenido": self.contenido.value,
            "guild_icon_url": icon_url,
            "color_personalizado": self.color,
            "fondo_url": self.fondo_url.value,
            "estilo": self.estilo,
            "guild_name": self.ctx.guild.name,
            "es_3d": self.es_3d
        }

        if self.animado:
            imagen_buffer = await self.generador.crear_gif_anuncio(**gen_kwargs)
            ext = "gif"
        else:
            imagen_buffer = await self.generador.crear_imagen_anuncio(**gen_kwargs)
            ext = "png"

        noticia_id = str(int(datetime.now().timestamp() * 1000))
        filename = f"noticia_glass.{ext}"
        
        noticia_obj = AnuncioData(
            id=noticia_id,
            tipo=TipoAnuncio.NOTICIA.value,
            titulo=self.titulo.value,
            contenido=self.contenido.value,
            autor_id=self.ctx.author.id,
            guild_id=self.ctx.guild.id,
            canal_id=canal.id,
            fecha_creacion=datetime.now().isoformat(),
            color_usado=self.color,
            estilo=self.estilo,
            es_3d=self.es_3d,
            animado=self.animado,
            modo_hibrido=self.hibrido,
            requisitos=self.requisitos
        )

        if self.hibrido:
            msg = await self.cog._enviar_anuncio_hibrido(canal, noticia_obj, imagen_buffer, filename)
        else:
            imagen_buffer.seek(0)
            archivo = discord.File(fp=imagen_buffer, filename=filename)
            msg = await canal.send(file=archivo)

        noticia_obj.mensaje_id = msg.id
        self.db.agregar("noticias", noticia_obj)
        # Realizar broadcast
        await self.cog._realizar_broadcast(self.ctx.guild, noticia_obj, imagen_buffer, filename)

        embed = discord.Embed(
            title="✅ Noticia Publicada",
            description=f"ID: `{noticia_id}`\nColor: **{self.color.title()}**",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class ModalSorteo(ui.Modal, title="🎁 Crear Sorteo"):
    titulo = ui.TextInput(label="Título del Sorteo", max_length=100)
    descripcion = ui.TextInput(label="Descripción", style=discord.TextStyle.long, max_length=1500)
    duracion = ui.TextInput(label="Duración", placeholder="24h, 7d, 1h", max_length=20)
    fondo_url = ui.TextInput(label="URL de Fondo (Opcional)", required=False)

    def __init__(self, db, ctx, generador, color: str, estilo: str, es_3d: bool, animado: bool, hibrido: bool, requisitos: dict, cog):
        super().__init__()
        self.db = db
        self.ctx = ctx
        self.generador = generador
        self.color = color
        self.estilo = estilo
        self.es_3d = es_3d
        self.animado = animado
        self.hibrido = hibrido
        self.requisitos = requisitos
        self.cog = cog

    def _parse_duracion(self, duracion_str: str) -> Optional[datetime]:
        match = re.match(r"(\d+)([hdm])", duracion_str.lower())
        if not match: return None
        cantidad, unidad = int(match.group(1)), match.group(2)
        ahora = datetime.now(pytz.timezone("America/Bogota"))
        if unidad == 'h': return ahora + timedelta(hours=cantidad)
        if unidad == 'd': return ahora + timedelta(days=cantidad)
        if unidad == 'm': return ahora + timedelta(minutes=cantidad)
        return None

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        exp_dt = self._parse_duracion(self.duracion.value)
        if not exp_dt:
            return await interaction.followup.send("❌ Duración inválida. Usa ej: `24h`, `7d`, `60m`", ephemeral=True)

        contenido_completo = f"{self.descripcion.value}\n\n⏱️ Finaliza: <t:{int(exp_dt.timestamp())}:R>\n🎉 Reacciona para participar"

        canal_id = self.db.obtener_canal_anuncios(self.ctx.guild.id)
        canal = self.ctx.bot.get_channel(canal_id) if canal_id else self.ctx.channel

        if not canal:
            return await interaction.followup.send("❌ Canal no válido", ephemeral=True)

        icon_url = self.ctx.guild.icon.url if self.ctx.guild.icon else None
        gen_kwargs = {
            "tipo": "sorteo",
            "titulo": self.titulo.value,
            "contenido": contenido_completo,
            "guild_icon_url": icon_url,
            "color_personalizado": self.color,
            "fondo_url": self.fondo_url.value,
            "estilo": self.estilo,
            "guild_name": self.ctx.guild.name,
            "es_3d": self.es_3d
        }

        if self.animado:
            imagen_buffer = await self.generador.crear_gif_anuncio(**gen_kwargs)
            ext = "gif"
        else:
            imagen_buffer = await self.generador.crear_imagen_anuncio(**gen_kwargs)
            ext = "png"

        sorteo_id = str(int(datetime.now().timestamp() * 1000))
        filename = f"sorteo_glass.{ext}"
        
        sorteo_obj = AnuncioData(
            id=sorteo_id,
            tipo=TipoAnuncio.SORTEO.value,
            titulo=self.titulo.value,
            contenido=self.descripcion.value,
            autor_id=self.ctx.author.id,
            guild_id=self.ctx.guild.id,
            canal_id=canal.id,
            fecha_creacion=datetime.now().isoformat(),
            color_usado=self.color,
            expiracion=exp_dt.isoformat(),
            estilo=self.estilo,
            es_3d=self.es_3d,
            animado=self.animado,
            modo_hibrido=self.hibrido,
            requisitos=self.requisitos
        )

        view = VistaParticiparSorteo(self.db, sorteo_id)
        if self.hibrido:
            msg = await self.cog._enviar_anuncio_hibrido(canal, sorteo_obj, imagen_buffer, filename, view=view)
        else:
            imagen_buffer.seek(0)
            archivo = discord.File(fp=imagen_buffer, filename=filename)
            msg = await canal.send(file=archivo, view=view)

        sorteo_obj.mensaje_id = msg.id
        self.db.agregar("sorteos", sorteo_obj)
        # Realizar broadcast
        await self.cog._realizar_broadcast(self.ctx.guild, sorteo_obj, imagen_buffer, filename)

        embed = discord.Embed(
            title="✅ Sorteo Creado",
            description=f"ID: `{sorteo_id}`\nColor: **{self.color.title()}**",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class PanelAnuncios(commands.Cog):
    """
    💎 SISTEMA DE ANUNCIOS DIAMOND EDITION
    
    Este es el núcleo operativo del bot. Se encarga de:
    1. Orquestar la generación de imágenes y animaciones GIF.
    2. Gestionar la interactividad de botones (Sorteos, RSVPs, Encuestas).
    3. Automatizar tareas como recordatorios y selección de ganadores.
    4. Proveer una suite administrativa para la gestión de contenido y analíticas.
    
    Diseñado bajo una arquitectura orientada a objetos para garantizar la 
    máxima eficiencia y estabilidad en servidores de alto tráfico.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db = BaseDatos()
        self.generador = GeneradorImagenes()
        self.verificar_expiraciones.start()
        # Registrar vistas persistentes al iniciar
        self.bot.loop.create_task(self._registrar_vistas_persistentes())

    async def _registrar_vistas_persistentes(self):
        """Registra las vistas de sorteos y eventos activos para que funcionen tras un reinicio."""
        await self.bot.wait_until_ready()
        datos = self.db.cargar()
        count = 0
        for sorteo in datos.get("sorteos", []):
            if not sorteo.get("finalizado"):
                self.bot.add_view(VistaParticiparSorteo(self.db, sorteo["id"]))
                count += 1
        for evento in datos.get("eventos", []):
            if not evento.get("finalizado"):
                self.bot.add_view(VistaRSVPEvento(self.db, evento["id"]))
                count += 1
        
    def cog_unload(self):
        self.verificar_expiraciones.cancel()

    @tasks.loop(minutes=5)
    async def verificar_expiraciones(self):
        ahora = datetime.now(pytz.timezone("America/Bogota"))
        datos = self.db.cargar()
        hubo_cambios = False
        
        # Recordatorios
        for tipo in ["eventos", "sorteos"]:
            for item in datos.get(tipo, []):
                if item.get("expiracion") and not item.get("recordatorio_enviado") and not item.get("finalizado"):
                    exp_dt = datetime.fromisoformat(item["expiracion"])
                    if exp_dt.tzinfo is None:
                        exp_dt = pytz.timezone("America/Bogota").localize(exp_dt)
                        
                    tiempo_restante = exp_dt - ahora
                    if timedelta(0) < tiempo_restante <= timedelta(hours=1):
                        canal = self.bot.get_channel(item["canal_id"])
                        if canal:
                            await canal.send(f"🔔 **Recordatorio:** El {tipo[:-1]} `{item['titulo']}` finalizará pronto!")
                            item["recordatorio_enviado"] = True
                            hubo_cambios = True

        # Finalización automática de sorteos
        for sorteo in datos.get("sorteos", []):
            if sorteo.get("expiracion") and not sorteo.get("finalizado"):
                exp_dt = datetime.fromisoformat(sorteo["expiracion"])
                if exp_dt.tzinfo is None:
                    exp_dt = pytz.timezone("America/Bogota").localize(exp_dt)
                
                if ahora >= exp_dt:
                    await self._terminar_sorteo_logica(sorteo)
                    hubo_cambios = True

        if hubo_cambios:
            self.db.guardar(datos)

    async def _terminar_sorteo_logica(self, sorteo_dict: dict):
        sorteo_dict["finalizado"] = True
        canal = self.bot.get_channel(sorteo_dict["canal_id"])
        if not canal: return

        participantes = sorteo_dict.get("participantes", [])
        if not participantes:
            await canal.send(f"❌ El sorteo `{sorteo_dict['titulo']}` ha terminado pero no hubo participantes.")
            return

        ganadores_count = min(len(participantes), sorteo_dict.get("ganadores_count", 1))
        ganadores = random.sample(participantes, ganadores_count)
        menciones = ", ".join([f"<@{g}>" for g in ganadores])
        
        embed = discord.Embed(
            title="🎉 Sorteo Finalizado",
            description=f"El sorteo **{sorteo_dict['titulo']}** ha terminado!",
            color=0xFFD700
        )
        embed.add_field(name="🏆 Ganadores", value=menciones)
        embed.set_footer(text=f"ID: {sorteo_dict['id']}")
        
        await canal.send(content=f"¡Felicidades {menciones}!", embed=embed)
        self.db.registrar_log(sorteo_dict["guild_id"], f"Sorteo {sorteo_dict['id']} finalizado. Ganadores: {ganadores}")

    @verificar_expiraciones.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()

    def is_admin():
        async def predicate(ctx):
            return ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    @commands.command(name="config-canal")
    @is_admin()
    async def config_canal(self, ctx, canal: discord.TextChannel):
        self.db.establecer_canal_anuncios(ctx.guild.id, canal.id)

        embed = discord.Embed(
            title="✅ Canal Configurado",
            description=f"Los anuncios se publicarán en {canal.mention}",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Configurado por {ctx.author.name}")
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="panel-a")
    @is_admin()
    async def panel_anuncio(self, ctx):
        canal_config = self.db.obtener_canal_anuncios(ctx.guild.id)
        canal_info = f"{self.bot.get_channel(canal_config).mention}" if canal_config else "Canal actual"
        stats = self.db.obtener_estadisticas()

        embed = discord.Embed(
            title="🎭 Panel de Anuncios Glass",
            description="Sistema de anuncios con efectos glass tipo iPhone",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="📢 Anuncio", value="`Publicar`", inline=True)
        embed.add_field(name="🗓️ Evento", value="`Programar`", inline=True)
        embed.add_field(name="📊 Encuesta", value="`Votación`", inline=True)
        embed.add_field(name="📰 Noticia", value="`Informar`", inline=True)
        embed.add_field(name="🎁 Sorteo", value="`Galar`", inline=True)
        embed.add_field(name="🛡️ Emblema", value="`Insignias`", inline=True)
        
        embed.add_field(name="📈 Estadísticas Rápidas", 
                        value=f"Total: `{stats['total']}` | Hoy: `{stats['anuncios'] + stats['eventos']}`", 
                        inline=False)
        embed.add_field(name="📍 Canal Configurado", value=canal_info, inline=False)
        embed.add_field(name="🎨 Bordes Especiales", value="Letras 'a' y 'e' con fuente de emojis", inline=False)

        embed.set_footer(text=f"Panel Pro v7.0 | {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        view = PanelPrincipal(ctx, self.db, self.generador)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="config-log")
    @is_admin()
    async def config_log(self, ctx, canal: discord.TextChannel):
        config = self.db.obtener_config(ctx.guild.id)
        config.canal_logs = canal.id
        self.db.guardar_config(config)
        await ctx.send(f"✅ Canal de logs configurado en {canal.mention}")

    @commands.command(name="borrar-todo")
    @is_admin()
    async def borrar_todo(self, ctx):
        # Confirmación simple
        await ctx.send("⚠️ ¿Estás seguro de borrar TODOS los datos de este servidor? (Responde 'si')")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'si'
        try:
            await self.bot.wait_for('message', check=check, timeout=15)
            datos = self.db.cargar()
            for key in ["anuncios", "eventos", "encuestas", "noticias", "sorteos", "plantillas"]:
                datos[key] = [a for a in datos[key] if a.get("guild_id") != ctx.guild.id]
            self.db.guardar(datos)
            await ctx.send("✅ Todos los datos han sido eliminados.")
        except:
            await ctx.send("❌ Operación cancelada.")

    @commands.command(name="plantilla-crear")
    @is_admin()
    async def plantilla_crear(self, ctx, nombre: str, tipo: str, color: str, *, contenido: str):
        plantilla = PlantillaData(
            id=str(int(datetime.now().timestamp())),
            nombre=nombre,
            tipo=tipo,
            titulo=f"Plantilla {nombre}",
            contenido=contenido,
            color=color,
            autor_id=ctx.author.id,
            guild_id=ctx.guild.id
        )
        self.db.guardar_plantilla(plantilla)
        await ctx.send(f"✅ Plantilla `{nombre}` guardada correctamente.")

    async def _enviar_anuncio_hibrido(self, canal: discord.TextChannel, data: AnuncioData, buffer: io.BytesIO, filename: str, view: Optional[ui.View] = None):
        """Envía un anuncio en modo híbrido (Embed + Imagen adjunta)."""
        buffer.seek(0)
        file = discord.File(fp=buffer, filename=filename)
        
        color_val = self.generador.config.PALETA_COLORES.get(data.color_usado, (52, 152, 219))
        if isinstance(color_val, tuple):
            color = discord.Color.from_rgb(*color_val)
        else:
            color = color_val

        embed = discord.Embed(
            title=data.titulo,
            description=data.contenido,
            color=color
        )
        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text=f"ID: {data.id} | Platinum Pro")
        return await canal.send(embed=embed, file=file, view=view)

    @commands.command(name="editar")
    @is_admin()
    async def editar(self, ctx: Union[commands.Context, discord.Interaction], anuncio_id: str):
        """
        Diamond Live Editor: Permite modificar el contenido de un anuncio ya publicado.
        
        El bot regenerará la imagen (incluyendo animaciones y 3D) y actualizará el mensaje
        original, manteniendo el mismo ID y estadísticas de interacción.
        """
        datos = self.db.cargar()
        anuncio_dict = None
        tipo_encontrado = None
        for tipo in ["anuncios", "eventos", "encuestas", "noticias", "sorteos"]:
            for a in datos.get(tipo, []):
                if a["id"] == anuncio_id:
                    anuncio_dict = a
                    tipo_encontrado = tipo
                    break
        
        if not anuncio_dict:
            return await ctx.send("❌ No se encontró ningún anuncio con ese ID.")

        # Convertir dict a objeto AnuncioData para facilitar manejo (filtrando llaves extra)
        valid_keys = {f.name for f in fields(AnuncioData)}
        filtered_dict = {k: v for k, v in anuncio_dict.items() if k in valid_keys}
        obj = AnuncioData(**filtered_dict)
        
        class ModalEditorLive(ui.Modal, title=f"🛠️ Editando {tipo_encontrado[:-1]}"):
            titulo = ui.TextInput(label="Nuevo Título", default=obj.titulo)
            contenido = ui.TextInput(label="Nuevo Contenido", style=discord.TextStyle.long, default=obj.contenido)
            
            def __init__(self, parent_cog, db, original_obj, tipo_p):
                super().__init__()
                self.cog = parent_cog
                self.db = db
                self.obj = original_obj
                self.tipo_p = tipo_p

            async def on_submit(self, inter: discord.Interaction):
                await inter.response.defer(ephemeral=True)
                # Actualizar objeto
                self.obj.titulo = self.titulo.value
                self.obj.contenido = self.contenido.value
                
                # Regenerar imagen
                gen_kwargs = {
                    "tipo": self.obj.tipo,
                    "titulo": self.obj.titulo,
                    "contenido": self.obj.contenido,
                    "color_personalizado": self.obj.color_usado,
                    "estilo": self.obj.estilo,
                    "es_3d": self.obj.es_3d,
                    "guild_name": inter.guild.name,
                    "guild_icon_url": inter.guild.icon.url if inter.guild.icon else None
                }
                
                if self.obj.animado:
                    img_buffer = await self.cog.generador.crear_gif_anuncio(**gen_kwargs)
                    filename = f"edited_{self.obj.id}.gif"
                else:
                    img_buffer = await self.cog.generador.crear_imagen_anuncio(**gen_kwargs)
                    filename = f"edited_{self.obj.id}.png"
                
                # Intentar editar el mensaje original
                canal = inter.guild.get_channel(self.obj.canal_id)
                if canal:
                    try:
                        msg = await canal.fetch_message(self.obj.mensaje_id)
                        img_buffer.seek(0)
                        if self.obj.modo_hibrido:
                            color_val = self.cog.generador.config.PALETA_COLORES.get(self.obj.color_usado, (52, 152, 219))
                            color = discord.Color.from_rgb(*color_val) if isinstance(color_val, tuple) else color_val
                            
                            embed = discord.Embed(title=self.obj.titulo, description=self.obj.contenido, color=color)
                            file = discord.File(fp=img_buffer, filename=filename)
                            embed.set_image(url=f"attachment://{filename}")
                            await msg.edit(embed=embed, attachments=[file])
                        else:
                            file = discord.File(fp=img_buffer, filename=filename)
                            await msg.edit(attachments=[file])
                    except:
                        return await inter.followup.send("⚠️ No pude editar el mensaje original. ¿Fue borrado?", ephemeral=True)
                
                # Guardar cambios en DB
                datos_db = self.db.cargar()
                lista = datos_db[self.tipo_p]
                for i, a in enumerate(lista):
                    if a["id"] == self.obj.id:
                        lista[i] = self.obj.to_dict()
                        break
                self.db.guardar(datos_db)
                await inter.followup.send("✅ Anuncio actualizado correctamente.", ephemeral=True)

        # Manejar si ctx es Context o Interaction
        if isinstance(ctx, discord.Interaction):
            await ctx.response.send_modal(ModalEditorLive(self, self.db, obj, tipo_encontrado))
        else:
            # Si es Context, avisamos que debe ser interacción
            await ctx.send("⚠️ Por favor, usa el botón **Editor Live** en el panel para una mejor experiencia.")

    @commands.command(name="stats-visual")
    @is_admin()
    async def stats_visual(self, ctx):
        """Genera un reporte visual profesional en formato glass."""
        await ctx.send("📊 Generando analíticas visuales de alta precisión...")
        stats = self.db.obtener_estadisticas_servidor(ctx.guild.id)
        
        # Mapeo para nombres más bonitos en la gráfica
        datos_grafica = {
            "Anuncios": stats["anuncios"],
            "Eventos": stats["eventos"],
            "Encuestas": stats["encuestas"],
            "Noticias": stats["noticias"],
            "Sorteos": stats["sorteos"]
        }
        
        # Usar el color del servidor si está disponible
        config = self.db.obtener_config(ctx.guild.id)
        color_hex = config.branding_colores[0] if config.branding_colores else "cyan"
        # Convertir hex a RGB simple si no es de la paleta
        color_rgb = (0, 191, 255) # default
        if color_hex in self.generador.config.PALETA_COLORES:
            color_rgb = self.generador.config.PALETA_COLORES[color_hex]

        img = self.generador.renderizar_grafica_barras(
            1200, 800, datos_grafica, 
            f"Reporte de Actividad: {ctx.guild.name}", 
            color_rgb
        )
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        file = discord.File(fp=img_buffer, filename="stats_pro_visual.png")
        await ctx.send("🖼️ Aquí tienes el resumen visual de actividad de tu servidor:", file=file)

    @commands.command(name="stats-pro")
    @is_admin()
    async def stats_pro(self, ctx):
        """Muestra estadísticas avanzadas del bot en este servidor."""
        stats = self.db.obtener_estadisticas_servidor(ctx.guild.id)
        config = self.db.obtener_config(ctx.guild.id)
        
        embed = discord.Embed(title="📊 Estadísticas Pro", color=discord.Color.gold())
        embed.add_field(name="Total Creados", value=f"`{stats['total']}`", inline=True)
        embed.add_field(name="Canal Configurado", value=f"<#{config.canal_anuncios}>" if config.canal_anuncios else "No", inline=True)
        embed.add_field(name="Idiomas", value=f"`{config.idioma.upper()}`", inline=True)
        
        # Calcular actividad hoy
        ahora = datetime.now()
        datos = self.db.cargar()
        hoy_count = 0
        for tipo in ["anuncios", "eventos", "encuestas", "noticias", "sorteos"]:
            for item in datos.get(tipo, []):
                if item.get("fecha_creacion"):
                    creado = datetime.fromisoformat(item["fecha_creacion"])
                    if creado.date() == ahora.date() and item.get("guild_id") == ctx.guild.id:
                        hoy_count += 1
        
        embed.add_field(name="Actividad Hoy", value=f"`{hoy_count}` anuncios", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="history")
    @is_admin()
    async def history(self, ctx):
        """Muestra el historial completo de anuncios de forma interactiva y paginada."""
        anuncios = self.db.obtener_todos_anuncios(ctx.guild.id)
        if not anuncios:
            return await ctx.send("❌ No se encontraron registros de anuncios en la base de datos de este servidor.")
        
        # Ordenar por fecha descendente (más nuevos primero)
        anuncios.sort(key=lambda x: x.get("fecha_creacion", ""), reverse=True)
        
        view = VistaPaginacion(anuncios)
        embed = view.get_embed()
        embed.set_author(name=f"Historial Pro - {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="preview")
    @is_admin()
    async def preview(self, ctx, color: str = "cyan", estilo: str = "moderno", es_3d: bool = False):
        """
        Genera una imagen de previsualización de alta fidelidad.
        Uso: /preview <color> <estilo> <3d:True/False>
        """
        async with ctx.typing():
            await ctx.send(f"⏳ Generando previsualización Diamond (Color: `{color}`, Estilo: `{estilo}`, 3D: `{es_3d}`)...")
            img_buffer = await self.generador.crear_imagen_anuncio(
                tipo="anuncio",
                titulo="Diamond Preview Edition",
                contenido=f"Diseñado para {ctx.guild.name}. Este sistema soporta variables dinámicas y efectos visuales de última generación.",
                color_personalizado=color,
                estilo=estilo,
                guild_name=ctx.guild.name,
                guild_icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
                es_3d=es_3d,
                context_guild=ctx.guild,
                context_member=ctx.author
            )
            file = discord.File(fp=img_buffer, filename="preview_diamond.png")
            await ctx.send("🖼️ Aquí tienes el resultado final de tu configuración:", file=file)

    @commands.command(name="help-anuncios")
    async def help_anuncios(self, ctx):
        """Muestra la guía completa del sistema de anuncios Platinum."""
        paginas = [
            {
                "titulo": "📢 Sistema de Anuncios Glass",
                "desc": "Bienvenido al generador de anuncios más avanzado. Usa `/panel-anuncio` para empezar.",
                "campos": [
                    ("🎨 Estilos", "Moderno, Elegante, Cyberpunk.", True),
                    ("🧊 Motor 3D", "Simula profundidad y sombras realistas.", True),
                    ("🛡️ Requisitos", "Filtra participantes por roles o antigüedad.", True)
                ]
            },
            {
                "titulo": "🎁 Sorteos y Eventos",
                "desc": "Automatiza la gestión de tu comunidad.",
                "campos": [
                    ("🏆 Sorteos", "Selección automática de ganadores al finalizar.", True),
                    ("📅 Eventos", "Confirmación de asistencia (RSVP) interactiva.", True),
                    ("📊 Encuestas", "Votación con resultados en gráficas de barras.", True)
                ]
            },
            {
                "titulo": "⚙️ Configuración Avanzada",
                "desc": "Herramientas para administradores.",
                "campos": [
                    ("🎨 Auto-Branding", "Analiza tu icono para sugerir colores.", True),
                    ("📁 Plantillas", "Guarda tus mejores diseños para reusarlos.", True),
                    ("📜 Logs", "Registro de todas las acciones administrativas.", True)
                ]
            },
            {
                "titulo": "🏷️ Variables Dinámicas",
                "desc": "Usa estas etiquetas en tus textos para personalizarlos automáticamente.",
                "campos": [
                    ("{user}", "Nombre del usuario.", True),
                    ("{server}", "Nombre del servidor.", True),
                    ("{count}", "Total de miembros.", True),
                    ("{date}", "Fecha actual.", True),
                    ("{boosts}", "Nivel de boosters.", True),
                    ("{owner}", "Dueño del servidor.", True)
                ]
            }
        ]

        class HelpView(ui.View):
            def __init__(self, p):
                super().__init__(timeout=60)
                self.p = p
                self.curr = 0

            def get_embed(self):
                data = self.p[self.curr]
                embed = discord.Embed(title=data["titulo"], description=data["desc"], color=0x5865F2)
                for n, v, i in data["campos"]: embed.add_field(name=n, value=v, inline=i)
                embed.set_footer(text=f"Página {self.curr + 1} de {len(self.p)}")
                return embed

            @ui.button(label="Anterior", style=discord.ButtonStyle.gray)
            async def prev(self, inter, btn):
                self.curr = (self.curr - 1) % len(self.p)
                await inter.response.edit_message(embed=self.get_embed())

            @ui.button(label="Siguiente", style=discord.ButtonStyle.gray)
            async def next(self, inter, btn):
                self.curr = (self.curr + 1) % len(self.p)
                await inter.response.edit_message(embed=self.get_embed())

        view = HelpView(paginas)
        await ctx.send(embed=view.get_embed(), view=view)

    @commands.command(name="config-broadcast")
    @is_admin()
    async def config_broadcast(self, ctx, canal: discord.TextChannel):
        """Configura un canal para la retransmisión automática de anuncios (Cross-posting)."""
        config = self.db.obtener_config(ctx.guild.id)
        if config.canales_broadcast is None: config.canales_broadcast = []
        
        if canal.id in config.canales_broadcast:
            config.canales_broadcast.remove(canal.id)
            msg = f"❌ Canal {canal.mention} removido de la red de broadcast."
        else:
            config.canales_broadcast.append(canal.id)
            msg = f"✅ Canal {canal.mention} añadido a la red de broadcast."
        
        self.db.guardar_config(config)
        await ctx.send(msg)

    async def _realizar_broadcast(self, guild: discord.Guild, data: AnuncioData, buffer: io.BytesIO, filename: str):
        """Envía el anuncio a todos los canales configurados en la red de broadcast."""
        config = self.db.obtener_config(guild.id)
        if not config.canales_broadcast: return
        
        buffer.seek(0)
        content_bytes = buffer.read()
        
        for cid in config.canales_broadcast:
            canal = self.bot.get_channel(cid)
            if canal:
                try:
                    # Crear nuevo buffer para cada envío
                    f = discord.File(fp=io.BytesIO(content_bytes), filename=filename)
                    if data.modo_hibrido:
                        embed = discord.Embed(title=f"📡 Broadcast: {data.titulo}", description=data.contenido, color=discord.Color.blue())
                        embed.set_image(url=f"attachment://{filename}")
                        await canal.send(embed=embed, file=f)
                    else:
                        await canal.send(content=f"📡 **Retransmisión desde {guild.name}**", file=f)
                except: continue

    @commands.command(name="gestionar")
    @is_admin()
    async def gestionar(self, ctx):
        anuncios = self.db.obtener_todos_anuncios(ctx.guild.id)
        if not anuncios:
            return await ctx.send("❌ No hay anuncios para gestionar")

        class GestionView(ui.View):
            def __init__(self, db, anuncios):
                super().__init__(timeout=180)
                self.db = db
                options = [
                    discord.SelectOption(
                        label=f"{a['titulo'][:25]}...", 
                        description=f"ID: {a['id']} | Tipo: {a['tipo']}", 
                        value=f"{a['tipo']}|{a['id']}"
                    ) for a in anuncios[-25:] # Discord solo permite 25 opciones
                ]
                self.select = ui.Select(placeholder="Selecciona un anuncio para eliminar", options=options)
                self.select.callback = self.callback
                self.add_item(self.select)

            async def callback(self, interaction: discord.Interaction):
                tipo_plural, aid = self.select.values[0].split("|")
                # El tipo en el select es el singular o el que viene de AnuncioData
                # Pero eliminar_anuncio espera el nombre de la lista en el JSON
                self.db.eliminar_anuncio(tipo_plural + "s" if not tipo_plural.endswith("s") else tipo_plural, aid)
                await interaction.response.send_message(f"✅ Anuncio `{aid}` eliminado", ephemeral=True)
                self.stop()

        await ctx.send("📋 Selecciona el anuncio que deseas eliminar:", view=GestionView(self.db, anuncios))


async def setup(bot):
    await bot.add_cog(PanelAnuncios(bot))
