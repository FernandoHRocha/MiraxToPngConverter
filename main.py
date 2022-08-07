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
import mysql.connector
import base64
from io import BytesIO
import requests

SQL_INSERT = " "
class database():

    def connectDatabase(self):
        return mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="123",
            database="histologia",
            charset='utf8',
            use_unicode=True,
            get_warnings=True
            )

    def storeImage(self, level, row, col, content):
        database_histologia = self.connectDatabase()
        cursor = database_histologia.cursor()
        query = "INSERT INTO histologia.slide (lamina_idlamina, level, row, col, content) VALUES ('1', " + str(level) + ", " + str(row) + ", " + str(col) + ", " + str(content) + ')'
        cursor.execute( query )
        database_histologia.commit()

class converter():

    def openFile(self, level):
        self.level = level
        root = tk.Tk()
        root.withdraw()

        path = filedialog.askopenfilename()

        self.file_folder = os.path.dirname(path)
        self.file_path = path
        self.file_name = os.path.split(self.file_path)[1]

        self.openSlide()
        return

    def openSlide(self):

        slide = open_slide(self.file_path)
        name = self.file_name.replace('.mrxs', '')
        thumbnail = slide.get_thumbnail(size=(400,400))
        buffer = BytesIO()
        thumbnail.save(buffer, format='PNG')
        img = str(base64.b64encode(buffer.getvalue()))[1:]
        self.storeSheet(img, name)
        
        #tiles = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=False)
        #print(tiles.level_count)
        #for level in range(12,13):
        #self.convertToImages(self.level, tiles)
        #self.convertToImages(15, tiles)

    def storeSheet(self, slide, name):
        url = 'http://127.0.0.1:8084/sheet'
        obj = {
            'name' : name,
            'description' : name,
            'thumbnail' : slide
        }
        result = requests.post(url=url, json=obj)
        print(result.content)
        exit()

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
