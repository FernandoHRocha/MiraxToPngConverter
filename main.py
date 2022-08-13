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

class converter():

    def openFile(self, level):
        """Extrai as informações necessárias a respeito do arquivo mirax desejado."""
        self.level = level
        root = tk.Tk()
        root.withdraw()

        path = filedialog.askopenfilename()

        self.file_folder = os.path.dirname(path)
        self.file_path = path
        self.file_name = os.path.split(self.file_path)[1]
        self.slide_name = self.file_name.replace('.mrxs', '')

        self.openSlide()

    def openSlide(self):
        """Converte o arquivo da lamina para futura manipulação."""
        slide = open_slide(self.file_path)
        thumbnail = slide.get_thumbnail(size=(400,400))
        buffer = BytesIO()
        thumbnail.save(buffer, format='PNG')
        img = str(base64.b64encode(buffer.getvalue()))[1:]
        self.storeSheet(img)
        
        #tiles = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=False)
        #print(tiles.level_count)
        #for level in range(12,13):
        #self.convertToImages(self.level, tiles)
        #self.convertToImages(15, tiles)

    def storeSheet(self, slide: str):
        """Insere uma nova lâmina no banco de dados, caso ela já exista nada é feito."""
        url = API_URL + 'sheet'
        slide_obj = {
            'name' : self.slide_name,
            'description' : self.slide_name,
            'thumbnail' : slide
        }
        result = requests.post(url=url, json=obj)
        status = result.status_code
        print(result.elapsed)
        if(status == 201 or status == 200):
            self.sheet_idsheet = result.json()[1]
            # CONVERTER A IMAGEM PARA O MAPEAMENTO EM ZOOM
        exit()
    
    def storeSlides(self, slide: openSlide):
        """Insere uma nova lâmina no banco de dados, com o mapeamento das imagens."""
        url = API_URL + 'slide/'
        slide_piece_obj = {
            'sheet_idsheet' : self.sheet_idsheet,
            'level' : 1,
            'row' : '',
            'column' : 1,
            'content' : ''
        }

    def convertToImages(self, resolution_level, tiles):

        rows, cols = tiles.level_tiles[resolution_level];
        destination_path = self.file_name.replace('.mrxs', '')+'_converted_'+str(resolution_level)

        for col in range(cols):
            for row in range(rows):
                tile_name = os.path.join(destination_path, 'l%d_c%d' % ((col+1), (row+1)))
                print("Salvando arquivo nomeado como: ", tile_name)
                temp_tile = tiles.get_tile(resolution_level, (row, col))
                temp_tile_RGB = temp_tile.convert('RGB')
                self.storeLocalImage(destination_path, tile_name, temp_tile_RGB)

    def storeLocalImage(self, destination_path, tile_name, temp_tile_RGB):
        temp_tile_np = np.array(temp_tile_RGB)
        try:
            plt.imsave(tile_name + ".png", temp_tile_np)
        except:
            os.mkdir(destination_path, 0o666)
            plt.imsave(tile_name + ".png", temp_tile_np)

class databaseStore():
    def readFiles(self, level):
        dir_path = './Adrenal 5_converted_'+str(level)
        for(paths, names, files) in os.walk(dir_path):
            for file in files:
                img = str(base64.b64encode(open(dir_path + '/' + file, "rb").read()))[1:]
                coordinates = file.replace('.png','').split('_')
                row = coordinates[0].replace('l','')
                col = coordinates[1].replace('c','')
                connection = database()
                connection.storeImage(level=2, row=row, col=col, content=img)


level = 12
bot = converter()
bot.openFile(level)
exit()

main = databaseStore()
main.readFiles(level)
exit()
