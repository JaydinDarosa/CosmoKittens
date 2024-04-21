import os
from PIL import Image

catPatterns = os.listdir('cats')

for patternLoop in range (len(catPatterns)):
    targetPattern = catPatterns[patternLoop]
    pattern = Image.open("cats/" + targetPattern)
    width, height = pattern.size 

    colors = {
        '1': (255, 160, 15, 255),
        '2': (0, 0, 0, 255),
        '3': (255, 255, 255, 255),
        '4': (100, 60, 32, 255),
        '5': (0, 105, 62, 255),
        '6': (155, 200, 235, 255),
        '7': (245, 220, 105, 255),
        '8': (200, 188, 208, 255)
    }

    loopCount = len(colors)

    for primaryLoop in range (loopCount):
        colorName = list(colors.keys())[primaryLoop]
        colorValue = list(colors.values())[primaryLoop]
        newCat = pattern.copy()
        for y in range(height): 
            for x in range(width):
                pixel = newCat.getpixel((x, y))
                if pixel == (63, 63, 63, 255):
                    newCat.putpixel((x, y), colorValue)
                elif not ((191, 109, 181, 255) < pixel < (201, 119, 191, 255) or pixel < (5, 5, 5, 255)):
                    newCat.putpixel((x, y), (0, 0, 0, 0))

        newCat.save("coloredPatterns/" + "pp_" + colorName + "_" + targetPattern)
            
    for accentLoop in range(loopCount):
        colorName = list(colors.keys())[accentLoop]
        colorValue = list(colors.values())[accentLoop]
        newCat = pattern.copy()
        for y in range(height): 
            for x in range(width):
                pixel = pattern.getpixel((x, y))
                if (122, 122, 122, 255) < pixel < (132, 132, 132, 255):
                    newCat.putpixel((x, y), colorValue)
                else:
                    newCat.putpixel((x, y), (0, 0, 0, 0))
        newCat.save("coloredPatterns/" + "sp_" + colorName + "_" + targetPattern)

