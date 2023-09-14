import typer
from typing import Optional, List
from typing_extensions import Annotated
from zipfile import ZipFile
from io import TextIOWrapper
from pathlib import Path
from enum import Enum
import json as jjson
from PIL import Image
from platform import system
from os.path import expanduser as userdocs
import shutil
from os import listdir

from util import nationalcolour, colourvariant, get_subjects, get_powers, get_players
from CWTools import cwformat, cwparse

app = typer.Typer()


class Overlays(str, Enum):
    classic = "classic"
    parchment = "parchment"


def extract(save: str):
    with ZipFile(save, "r") as zipdata:
        with zipdata.open("gamestate", "r") as fid:
            gamedata = TextIOWrapper(fid, encoding='iso-8859-1').read()
            res = cwparse(gamedata)
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


def map_paint(nation: str):
    nationl, subject = read(nation, True)
    nr, ng, nb = nationalcolour(nation)
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
                                print("Found nation colour of " + str(nr) + " " + str(ng) + " " + str(
                                    nb) + " at location W:" + str(w) + "-H:" + str(h) + "-PROV:" + str(prov_id))
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
                                    sr, sg, sb = colourvariant(nr, ng, nb, brightness_offset=40)
                                    print("Found subject colour of " + str(sr) + " " + str(sg) + " " + str(
                                        sb) + " at location W:" + str(w) + "-H:" + str(h) + "-PROV:" + str(prov_id))
                                    rgb_n.putpixel((w, h), (sr, sg, sb))
                                else:
                                    rgb_n.putpixel((w, h), (255, 255, 255, 0))
                        rgb_n.save('provs/' + split_prov[4] + '.png')
                        im_new = Image.alpha_composite(im_new, rgb_n)
                        print("added SUBJECT province " + prov_id + " to " + nation)
    im_new.save('provs/' + nation + '.png')


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
    im = Image.open(provinces)
    rgb_im = im.convert('RGBA')
    rgb_im.save('provs/provinces.png')
    shutil.copyfile(definitions, 'provs/definition.txt')


@app.command()
def paint(save: Path,
          tag: List[str] = None,
          overlay: Overlays = Overlays.classic,
          provinces: str = "vanilla",
          all_powers: bool = False):
    print("Painting " + save.name)
    json = jjson.loads(open("out.json", "r", encoding="iso-8859-1").read())
    if all_powers:
        tag.extend(get_powers(json))
    if not tag:
        tag.extend(get_players(json))
    print(tag)


if __name__ == "__main__":
    app()
