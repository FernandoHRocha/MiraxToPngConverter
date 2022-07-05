from openslide import open_slide
import openslide
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from openslide.deepzoom import DeepZoomGenerator
import os
import tkinter as tk
from tkinter import filedialog

class converter():

    def openFile(self):
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
        tiles = DeepZoomGenerator(slide, tile_size=512, overlap=0, limit_bounds=False)

        #print(tiles.level_count)
        for level in range(12,16):
            self.convertToImages(level, tiles)
        #self.convertToImages(15, tiles)

    def convertToImages(self, resolution_level, tiles):

        rows, cols = tiles.level_tiles[resolution_level];
        destinationPath = self.file_name.replace('.mrxs', '')+'_converted_'+str(resolution_level)
        
        for col in range(cols):
            for row in range(rows):
                tile_name = os.path.join(destinationPath, 'l%d_c%d' % (col, row))
                print("Salvando arquivo nomeado como: ", tile_name)
                temp_tile = tiles.get_tile(resolution_level, (row, col))
                temp_tile_RGB = temp_tile.convert('RGB')
                temp_tile_np = np.array(temp_tile_RGB)
                try:
                    plt.imsave(tile_name + ".png", temp_tile_np)
                except:
                    os.mkdir(destinationPath, 0o666)
                    plt.imsave(tile_name + ".png", temp_tile_np)

bot = converter()
bot.openFile()
exit()

    # print(os.path.split(file_path)[1])♣
    # print(len(slide.level_dimensions))
    # print(slide.level_dimensions)
    #slide.get_thumbnail(size=(6828, 14444)).show()
# slide_props = slide.properties

# slide_thumb_600 = slide.get_thumbnail(size=(600,600))
# slide_thumb_600.show()

# slide_thumb_600_np = np.array(slide_thumb_600)
# plt.figure(figsize=(8,8))
# plt.imshow(slide_thumb_600_np)

# dimensions = slide.level_dimensions
# n_levels = len(dimensions)
# factors = slide.level_downsamples

# level6_dimension = dimensions[6]
# level6_img = slide.read_region((0,0), 6, level6_dimension)
# img6 = level6_img.convert('RGB')

# tiles = DeepZoomGenerator(slide, tile_size=256, overlap=0, limit_bounds=False)
# print("Número de níveis que o slide pode ter com as configurações aplicadas acima: ", tiles.level_count)
# print("Quantas imagens cada níveis terá: ", tiles.level_dimensions)
# print("Número total de imagens geradas: ", tiles.tile_count)


# level_num = 11
# print("O nível ", level_num, " possui imagens: ", tiles.level_tiles[level_num])
# print("Neste nível são ", tiles.level_tiles[level_num][0]*tiles.level_tiles[level_num][1], " imagens no total.")



