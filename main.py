from ctypes.wintypes import RGB
from openslide import open_slide
import openslide
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from openslide.deepzoom import DeepZoomGenerator
import os
import tkinter as tk
from tkinter import filedialog
import base64
from io import BytesIO
import requests

API_URL = 'http://127.0.0.1:8084/'
TILE_SIZE = 512
ZOOM_LEVELS = [12, 13, 14]

class Converter():

    def open_file(self):
        """Extrai as informações necessárias a respeito do arquivo mirax desejado."""
        root = tk.Tk()
        root.withdraw()

        path = filedialog.askopenfilename()

        self.file_folder = os.path.dirname(path)
        self.file_path = path
        self.file_name = os.path.split(self.file_path)[1]
        self.slide_name = self.file_name.replace('.mrxs', '')

        self.open_slide()

    def open_slide(self):
        """Converte o arquivo da lamina para futura manipulação."""
        self.slide = open_slide(self.file_path)
        thumbnail = self.slide.get_thumbnail(size=(400,400))
        thumbnail_string = self.convert_image_to_base64(thumbnail)

        self.store_sheet(thumbnail_string)

    def store_sheet(self, slide: str):
        """Insere uma nova lâmina no banco de dados, caso ela já exista nada é feito."""
        url = API_URL + 'sheet'
        slide_obj = {
            'name' : self.slide_name,
            'description' : self.slide_name,
            'thumbnail' : slide
        }
        result = requests.post(url=url, json=slide_obj)
        status = result.status_code
        if(status == 201):
            self.sheet_idsheet = result.json()[1]
            self.map_slide_images()
            # CONVERTER A IMAGEM PARA O MAPEAMENTO EM ZOOM
        if(status == 200):
            print('A imagem já se encontra no sistema.')
        exit()
    
    def map_slide_images(self):
        """Converte a imagem da lâmina para uma sequência mapeada de imagens."""
        self.slide_tiles = DeepZoomGenerator(self.slide, tile_size=TILE_SIZE, overlap=0, limit_bounds=False)
        for zoom_level in ZOOM_LEVELS:
            self.get_zoom_tiles(zoom_level)

    def get_zoom_tiles(self, zoom_level: int):
        """Obtem as imagens de uma lâmina para determinado nível de ampliação"""
        rows, cols = self.slide_tiles.level_tiles[zoom_level]

        for col in range(cols):
            for row in range(rows):
                temp_tile = self.slide_tiles.get_tile(zoom_level, (row, col))
                temp_tile = temp_tile.convert('RGB')
                content = self.convert_image_to_base64(temp_tile)
                self.store_slide(zoom_level=zoom_level, row=row+1, col=col+1, content=content)

    def store_slide(self, zoom_level: int, row: int, col: int, content: str):
        """Insere uma nova lâmina no banco de dados, com o mapeamento das imagens."""
        url = API_URL + 'slide/'
        slide_piece_obj = {
            'sheet_idsheet' : self.sheet_idsheet,
            'level' : zoom_level,
            'row' : row,
            'col' : col,
            'content' : content
        }
        result = requests.post(url=url, json=slide_piece_obj)
        status = result.status_code
        if(status == 201):
            print('Piece row = ' + str(row) + ' col = ' + str(col))
        else:
            print(result.content)
            if(status == 500):
                exit()
    
    def convert_image_to_base64(self, image: Image) -> str:
        """Converte um arquivo de imagem em um base64"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_string = str(base64.b64encode(buffer.getvalue()))[1:]
        return image_string

bot = Converter()
bot.open_file()
exit()