import json as jjson
from enum import Enum
from io import TextIOWrapper
from os import listdir
from os.path import expanduser as userdocs
from pathlib import Path
from platform import system
from typing import Optional, List
from zipfile import ZipFile

import typer
from PIL import Image
from typing_extensions import Annotated

from CWTools import cwformat, cwparse
from generator import generateprovinces
from util import nationalcolour, colourvariant, get_powers, get_players, get_land_provinces

app = typer.Typer()


class Overlays(str, Enum):
    classic = "classic"
    parchment = "parchment"


def extract(save: Path):
    with ZipFile(save, "r") as zipdata:
        with zipdata.open("gamestate", "r") as fid:
            gamedata = TextIOWrapper(fid, encoding='iso-8859-1').read()
            res = cwparse(gamedata)
            print(res)
            res_dict = cwformat(res)
            with open("out.json", 'w', encoding='utf-8') as outf:
                print("Writing results to file...")
                outf.write(jjson.dumps(res_dict, indent=2, ensure_ascii=False))


def read(nation: str, subjects: bool):
    with open('out.json', 'r', encoding="iso-8859-1") as input_file:
        data = input_file.read()
        structure = jjson.loads(data)
        nation_provinces = structure["countries"][nation]["owned_provinces"]
        subjects_provinces = []
        if subjects:
            if "subjects" in structure["countries"][nation]:
                for o in structure["countries"][nation]["subjects"]:
                    subjects_provinces.append(structure["countries"][o]["owned_provinces"])
        input_file.close()
        return nation_provinces, subjects_provinces


def paint_land(province_map, land_provinces):
    im_new = Image.new(mode="RGBA", size=(5632, 2048), color=(96, 123, 156))
    for prov in land_provinces:
        if str(prov) in province_map:
            pixels = province_map[str(prov)]
            for wh in pixels:
                im_new.putpixel(wh, (135, 130, 130))
    return im_new


def map_paint(nation: str, province_map):
    nationl, subjects = read(nation, True)
    nr, ng, nb = nationalcolour(nation)
    im_new = Image.new(mode="RGBA", size=(5632, 2048))
    wee = []
    for prov in nationl:
        if str(prov) in province_map:
            pixels = province_map[str(prov)]
            for wh in pixels:
                wee.append(wh)
                im_new.putpixel(wh, (nr, ng, nb))
            del province_map[str(prov)]
    for subject in subjects:
        for prov in subject:
            if str(prov) in province_map:
                pixels = province_map[str(prov)]
                for wh in pixels:
                    wee.append(wh)
                    sr, sg, sb = colourvariant(nr, ng, nb, brightness_offset=20)
                    im_new.putpixel(wh, (sr, sg, sb))
                del province_map[str(prov)]
    return im_new


def get_map_dir():
    match system():
        case "Linux":
            print("LINUX!")
        case _:
            map_dir = ""
            for i in listdir(userdocs("~/Documents/Paradox Interactive/Europa Universalis IV/mod")):
                if "ugc" in i:
                    file = open(userdocs("~/Documents/Paradox Interactive/Europa Universalis IV/mod/" + i), "r")
                    ugc = file.read().split("\"")
                    map_dir = ""
                    for mods in ugc:
                        if "steamapps" in mods:
                            map_dir = mods[:abs(mods.find("workshop"))] + "common/Europa Universalis IV/map/"
                            break
                    break
            return map_dir


@app.command()
def generate(name: str = "vanilla",
             provinces: Annotated[Optional[Path], typer.Option()] = None,
             definitions: Annotated[Optional[Path], typer.Option()] = None):
    print("Generating " + name + " Provinces")
    if provinces is None:
        provinces = Path(get_map_dir() + "provinces.bmp")
    if definitions is None:
        definitions = Path(get_map_dir() + "definition.csv")
    saveGen = open(name + ".json", "w")
    jjson.dump(generateprovinces(provinces, definitions), saveGen)
    saveGen.close()
    print("Saved Province Gen to filesystem")


@app.command()
def paint(save: Path,
          tag: List[str] = None,
          overlay: Overlays = Overlays.classic,
          provinces: str = "vanilla",
          all_powers: bool = False):
    extract(save)
    print("Painting " + save.name)
    json = jjson.loads(open("out.json", "r", encoding="iso-8859-1").read())
    if all_powers:
        tag.extend(get_powers(json))
    if not tag:
        tag.extend(get_players(json))
    print(tag)
    tag_paints = []
    prov = open(provinces + ".json", "r")
    prov_data = jjson.load(prov)
    land_provinces = get_land_provinces(json)
    for i in tag:
        tag_paints.append(map_paint(i.upper(), prov_data))
    im = paint_land(prov_data, land_provinces)
    for img in tag_paints:
        im = Image.alpha_composite(im, img)
    im.save('end' + '.png')


if __name__ == "__main__":
    app()
