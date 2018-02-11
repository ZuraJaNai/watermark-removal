import os
import os.path
from PIL import Image
from collections import Counter
from datetime import datetime
import cv2


def find_water_pixel(img_rgb, w, h):
    water_pixel = []
    for y in range(1, h - 2):
        for x in range(1, w - 2):
            neighbours = img_rgb.getpixel((x - 1, y - 1)) + \
                         img_rgb.getpixel((x, y - 1)) + \
                         img_rgb.getpixel((x + 1, y - 1)) + \
                         img_rgb.getpixel((x - 1, y)) + \
                         img_rgb.getpixel((x + 1, y)) + \
                         img_rgb.getpixel((x - 1, y + 1)) + \
                         img_rgb.getpixel((x, y + 1)) + \
                         img_rgb.getpixel((x + 1, y + 1))
                         # img_rgb.getpixel((x - 2, y - 2)) + \
                         # img_rgb.getpixel((x - 1, y - 2)) + \
                         # img_rgb.getpixel((x, y - 2)) + \
                         # img_rgb.getpixel((x + 1, y - 2)) + \
                         # img_rgb.getpixel((x + 2, y - 2)) + \
                         # img_rgb.getpixel((x - 2, y - 1)) + \
                         # img_rgb.getpixel((x + 2, y - 1)) + \
                         # img_rgb.getpixel((x - 2, y)) + \
                         # img_rgb.getpixel((x + 2, y)) + \
                         # img_rgb.getpixel((x - 2, y + 1)) + \
                         # img_rgb.getpixel((x + 2, y + 1)) + \
                         # img_rgb.getpixel((x - 2, y + 2)) + \
                         # img_rgb.getpixel((x - 1, y + 2)) + \
                         # img_rgb.getpixel((x, y + 2)) + \
                         # img_rgb.getpixel((x + 1, y + 2)) + \
                         # img_rgb.getpixel((x + 2, y + 2))
            sum_neighbours = 0

            for i in neighbours:
                sum_neighbours = sum_neighbours + i

            sum_current_pixel = 0
            for j in img_rgb.getpixel((x, y)):
                sum_current_pixel = sum_current_pixel + j

            # detected watermark symbols
            if abs(sum_neighbours - 8 * sum_current_pixel) > 300:
                water_pixel.append((x, y))
    return water_pixel


def find_water_rows(water_pixel, h):
    counter = Counter(pixel[1] for pixel in water_pixel)
    water_rows = []
    for i in range(0, len(counter)):
        if counter[i] > 120 and (i > round(h*0.8)):
            water_rows.append(i)
    if(len(water_rows)==0):
        return water_rows
    min_row = min(water_rows)
    max_row = max(water_rows)
    for i in range(min_row-5, min_row):
        water_rows.append(i)
    for i in range(max_row, max_row + 5):
        water_rows.append(i)

    return water_rows


def find_normal_pixels(water_pixels, water_rows, width, img_rgb):
    pixels = []
    for row in water_rows:
        for x in range(0, width-1):
            ri, gi, bi = img_rgb.getpixel((x, row))
            if ((x, row) not in water_pixels) and (ri < 170) and (gi < 140) and (bi < 140):
                pixels.append((x, row))
    return pixels


def clearing():
    basePath = os.getcwd()
    currentPath = basePath + "/images"
    images = os.listdir(currentPath)
    for image in images:
        print("\nImage  " + image)
        start = datetime.now()
        img_path = currentPath + "/" + image
        img = Image.open(img_path)
        w, h = img.size
        img_rgb = img.convert('RGB')

        water_pixel = find_water_pixel(img_rgb, w, h)
        print("\n\nWater pixels  ")
        water_rows = find_water_rows(water_pixel, h)
        print("\n\nWater rows  ")
        if len(water_rows) != 0:
            bad_pixels = [pixel for pixel in water_pixel if pixel[1] in water_rows]
            print("\n\nBad pixels  ")

            new_img = img_rgb.copy()

            mask_img = Image.new('RGB', (w, h))
            for pixel in bad_pixels:
                if pixel[1] in water_rows:
                    mask_img.putpixel(pixel, (255, 255, 255))

            mask_img.save(currentPath + "mask_" + image)
            new_img.save(currentPath + "new_" + image)

            img = cv2.imread(basePath + "/" + "imagesnew_" + image)
            mask = cv2.imread(basePath + "/" + "imagesmask_" + image, 0)

            dst = cv2.inpaint(img, mask, 10, cv2.INPAINT_TELEA)
            cv2.imwrite("new" + image, dst)
            os.rename(basePath + "/new" + image, basePath + "/new_images/new" + image)

            #os.remove(currentPath + "mask_" + image)
            #os.remove(currentPath + "new_" + image)

            print("\nTIME:  " + str(datetime.now() - start))


if __name__ == '__main__':
    clearing()
