import typer
from zipfile import ZipFile
from io import TextIOWrapper
import json
from PIL import Image, ImageDraw, ImageColor
import numpy as np

from CWTools import cwformat, cwparse


def extract(save: str):
    with ZipFile(save, "r") as zipdata:
        with zipdata.open("gamestate", "r") as fid:
            gamedata = TextIOWrapper(fid, encoding='iso-8859-1').read()
            res = cwparse(gamedata)
            res_dict = cwformat(res)
            with open("out.json", 'w', encoding='utf-8') as outf:
                print("Writing results to file...")
                outf.write(json.dumps(res_dict, indent=2, ensure_ascii=False))


def read(nation: str, subjects: bool):
    with open('out.json', 'r', encoding="iso-8859-1") as input_file:
        data = input_file.read()
        structure = json.loads(data)
        nation_provinces = structure["countries"][nation]["owned_provinces"]
        subjects_provinces = []
        if subjects:
            if "subjects" in structure["countries"][nation]:
                for o in structure["countries"][nation]["subjects"]:
                    subjects_provinces.append(structure["countries"][o]["owned_provinces"])
        input_file.close()
        return nation_provinces, subjects_provinces


def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex2rgb(hexcode):
    return ImageColor.getcolor(hexcode, "RGB")


def color_variant(r, g, b, brightness_offset=1):
    hex_color = rgb2hex(r, g, b)
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]  # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return hex2rgb("#" + "".join([hex(i)[2:] for i in new_rgb_int]))


def get_nation_colour(nation: str):
    with open('out.json', 'r', encoding="iso-8859-1") as input_file:
        data = input_file.read()
        structure = json.loads(data)
        return tuple(structure["countries"][nation]["colors"]["country_color"])


def map_paint(nation: str):
    nationl, subject = read(nation, True)
    nr, ng, nb = get_nation_colour(nation)
    im = Image.open('provinces.bmp')
    rgb_im = im.convert('RGBA')
    im_new = Image.new(mode="RGBA", size=(rgb_im.size[0], rgb_im.size[1]))
    with open("definition.csv", "r") as defi:
        for i in defi:
            if ";x;x" not in i:
                prov_id = i.split(";")[0]
                if int(prov_id) in nationl:
                    print("preparing to add province " + prov_id + " to " + nation)
                    prov = i.replace("\n", "")
                    split_prov = prov.split(";")
                    r, g, b = int(split_prov[1]), int(split_prov[2]), int(split_prov[3])
                    rgb_n = rgb_im.copy()
                    for w in range(0, rgb_im.size[0]):
                        for h in range(0, rgb_im.size[1]):
                            data = rgb_n.getpixel((w, h))
                            if data[0] == r and data[1] == g and data[2] == b:
                                print("Found nation colour of " + str(nr) + " " + str(ng) + " " + str(nb) + " at location W:" + str(w) + "-H:" + str(h) + "-PROV:" + str(prov_id))
                                rgb_n.putpixel((w, h), (nr, ng, nb))
                            else:
                                rgb_n.putpixel((w, h), (255, 255, 255, 0))
                    rgb_n.save('provs/' + split_prov[4] + '.png')
                    im_new = Image.alpha_composite(im_new, rgb_n)
                    print("added province " + prov_id + " to " + nation)
                for subnat in subject:
                    if int(prov_id) in subnat:
                        print("preparing to add SUBJECT province " + prov_id + " to " + nation)
                        prov = i.replace("\n", "")
                        split_prov = prov.split(";")
                        r, g, b = int(split_prov[1]), int(split_prov[2]), int(split_prov[3])
                        rgb_n = rgb_im.copy()
                        for w in range(0, rgb_im.size[0]):
                            for h in range(0, rgb_im.size[1]):
                                data = rgb_n.getpixel((w, h))
                                if data[0] == r and data[1] == g and data[2] == b:
                                    sr, sg, sb = color_variant(nr, ng, nb, brightness_offset=40)
                                    print("Found subject colour of " + str(sr) + " " + str(sg) + " " + str(sb) + " at location W:" + str(w) + "-H:" + str(h) + "-PROV:" + str(prov_id))
                                    rgb_n.putpixel((w, h), (sr, sg, sb))
                                else:
                                    rgb_n.putpixel((w, h), (255, 255, 255, 0))
                        rgb_n.save('provs/' + split_prov[4] + '.png')
                        im_new = Image.alpha_composite(im_new, rgb_n)
                        print("added SUBJECT province " + prov_id + " to " + nation)
    im_new.save('provs/' + nation + '.png')


def main(save: str, nation: str, subjects: bool, provinces: str):
    map_paint(nation)


if __name__ == "__main__":
    typer.run(main)
