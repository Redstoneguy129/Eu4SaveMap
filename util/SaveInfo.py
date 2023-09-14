def get_overlord(json, tag: str):
    if "overlord" in json["countries"][tag]:
        return json["countries"][tag]["overlord"]
    return None


def get_subjects(json, tag: str):
    if "subjects" in json["countries"][tag]:
        return json["countries"][tag]["subjects"]
    return []


def get_colour(json, tag: str):
    return json["countries"][tag]["colors"]["country_color"]


def get_powers(json):
    powers = []
    for i in json["great_powers"]["original"]:
        powers.append(i["country"])
    return powers


def get_players(json):
    return json["players_countries"][1::2]
