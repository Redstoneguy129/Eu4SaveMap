from pathlib import Path

from PIL import Image


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def generate(provinces: Path, definitions: Path):
    definitions_fs = open(definitions, "r", encoding="iso-8859-1")
    definitions_all = definitions_fs.readlines()[1:]
    provinces_img = Image.open(provinces)
    provinces_rgba = provinces_img.convert('RGBA')
    pixel_map = {}
    for w in range(0, provinces_rgba.size[0]):
        for h in range(0, provinces_rgba.size[1]):
            pixel_rgba = provinces_rgba.getpixel((w, h))
            pixel_rgb = pixel_rgba[:-1]
            prgb = str(pixel_rgb[0]) + ":" + str(pixel_rgb[1]) + ":" + str(pixel_rgb[2])
            old_pixel_group = []
            if prgb in pixel_map:
                old_pixel_group = pixel_map[prgb]
                del pixel_map[prgb]
            old_pixel_group.append((w, h))
            pixel_map[prgb] = old_pixel_group
    for i in definitions_all:
        entries = i.split(";")
        entry_name, entry_r, entry_g, entry_b = entries[0], entries[1], entries[2], entries[3]
        entry_rgb = str(entry_r) + ":" + str(entry_g) + ":" + str(entry_b)
        if entry_rgb in pixel_map:
            pixel_group = pixel_map[entry_rgb]
            del pixel_map[entry_rgb]
            pixel_map[entry_name] = pixel_group
    definitions_fs.close()
    return pixel_map
