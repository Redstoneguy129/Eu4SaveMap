from PIL import ImageColor
import json


def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex2rgb(hex):
    return ImageColor.getcolor(hex, "RGB")


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
