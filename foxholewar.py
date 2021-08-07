from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import datetime
import enum
import json
import requests


__version__ = '0.1.1'


# api server addresses
API_ADDRESSES: dict = {'live1': "https://war-service-live.foxholeservices.com/api/",
                       'live2': "https://war-service-live-2.foxholeservices.com/api/"}

# map name dictionary
MAPS = {'StonecradleHex': "Stonecradle",
        'AllodsBightHex': "Allod's Bight",
        'GreatMarchHex': "Great March",
        'TempestIslandHex': "Tempest Island",
        'MarbanHollow': "Marban Hallow",
        'ViperPitHex': "Viper Pit",
        'ShackledChasmHex': "Shackled Chasm",
        'DeadLandsHex': "Deadlands",
        'LinnMercyHex': "The Linn of Mercy",
        'HeartlandsHex': "The Heartlands",
        'EndlessShoreHex': "Endless Shore",
        'GodcroftsHex': "Godcrofts",
        'FishermansRowHex': "Fisherman's Row",
        'UmbralWildwoodHex': "Umbral Wildwood",
        'ReachingTrailHex': "Reaching Trail",
        'WestgateHex': "Westgate",
        'CallahansPassageHex': "Callahan's Passage",
        'OarbreakerHex': "The Oarbreaker Isles",
        'DrownedValeHex': "The Drowned Vale",
        'FarranacCoastHex': "Farranac Coast",
        'MooringCountyHex': "Mooring County",
        'WeatheredExpanseHex': "Weathered Expanse",
        'LochMorHex': "Loch Mor"}


def is_valid_map_name(map_name):
    return map_name in MAPS or map_name in MAPS.values()


class Team(enum.Enum):
    """The teams"""
    NONE = 0
    COLONIAL = 1
    WARDENS = 2

    def __str__(self):
        return self.name


class MapMarkerType(enum.Enum):
    """Types of map marker"""
    MAJOR = 0
    MINOR = 1


@dataclass
class War:
    """The information for a war"""
    warId: str
    warNumber: int
    winner: str
    conquestStartTime: int
    conquestEndTime: int
    resistanceStartTime: int
    requiredVictoryTowns: int


@dataclass
class Map:
    """A (hex) map"""
    rawName: str
    prettyName: str
    regionId: int = None
    scorchedVictoryTowns: int = None
    mapItems: list = field(default_factory=list)
    mapTextItems: list = field(default_factory=list)


@dataclass
class MapItem:
    """An item on the map"""
    teamId: str
    iconType: int
    x: float
    y: float
    flags: int


@dataclass
class MapTextItem:
    """A text item on the map"""
    text: str
    x: float
    y: float
    mapMarkerType: str


@dataclass
class Report:
    """A war report for a map"""
    totalEnlistments: int
    colonialCasualties: int
    wardenCasualties: int
    dayOfWar: int
    version: int


class Client:
    api_address: str

    def __init__(self, server: str = 'live1'):
        # create requests session and set active api
        self.session = requests.Session()
        self.set_server(server)

        # declare and build dicts with None values
        self.dynamic_cache: dict = {f'{key}@{self.api_address}': None for key in MAPS.keys()}
        self.last_checks: dict = {f'{key}@{self.api_address}': None for key in MAPS.keys()}

    def set_server(self, server: str = 'live1') -> None:
        """Set api address to either 'live1' or 'live2'."""
        self.api_address = API_ADDRESSES[server]

    def close(self) -> None:
        """Close requests connection to the API"""
        self.session.close()

    def fetch_json(self, endpoint: str) -> dict:
        """Request some JSON data from the given endpoint"""
        request_url = f'{self.api_address}{endpoint}'
        response = self.session.get(request_url)
        text = response.text
        response.close()
        return json.loads(text)

    def fetch_current_war(self) -> War:
        """Get the data for the current war"""
        json_data = self.fetch_json("worldconquest/war")
        return War(**json_data)

    def fetch_report(self, target_map: Map) -> Report:
        """Get a war report for the given map name"""
        report_data = self.fetch_json(f"worldconquest/warReport/{target_map.rawName}")
        return Report(**report_data)

    def fetch_map(self, target_map: str):
        """Get available data for the target_map and return as a Map object"""
        current_map = Map(rawName=target_map, prettyName=MAPS[target_map])

        # get the static map data
        static_map_data = self.fetch_json(f"worldconquest/maps/{current_map.rawName}/static")

        # and the dynamic map data
        target_key = f'{current_map.rawName}@{self.api_address}'
        if self.last_checks[target_key] is None \
                or datetime.datetime.now() - self.last_checks[target_key] >= datetime.timedelta(3.472222e-5):

            # load dynamic map data from api request
            dynamic_map_data = self.fetch_json(f"worldconquest/maps/{current_map.rawName}/dynamic/public")
            self.last_checks[target_key] = datetime.datetime.now()
            self.dynamic_cache[target_key] = dynamic_map_data

        else:
            # load dynamic map data from cache
            dynamic_map_data = self.dynamic_cache[target_key]

        #
        current_map.scorchedVictoryTowns = static_map_data["scorchedVictoryTowns"]
        current_map.regionId = static_map_data["regionId"]

        # It seems as though we only get text items from static data and regular items from dynamic data?
        for item in static_map_data["mapTextItems"]:
            current_map.mapTextItems.append(MapTextItem(**item))

        for item in dynamic_map_data["mapItems"]:
            current_map.mapItems.append(MapItem(**item))

        return current_map

    def fetch_map_list(self) -> list:
        """Get the list of maps"""
        map_data = self.fetch_json("worldconquest/maps")

        # list of maps to return
        maps = []

        # vroom vroom, added threading to map list fetching
        futures = []
        with ThreadPoolExecutor() as executor:
            for map_name in map_data:
                futures.append(executor.submit(self.fetch_map, map_name))

        # cycle through futures and append the results
        for future in futures:
            maps.append(future.result())

        return maps
