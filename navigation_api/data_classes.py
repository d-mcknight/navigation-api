import json
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from geopy import Nominatim
from geopy.location import Location


class ModeOfTransportation(Enum):
    """
    Enum representing modes of transportation available for directions.
    """
    CAR = "driving-car"
    TRUCK = "driving-hgv"
    WALKING = "foot-walking"
    HIKING = "foot-hiking"
    CYCLE = "cycling-regular"
    CYCLE_ROAD = "cycling-road"
    CYCLE_MOUNTAIN = "cycling-mountain"
    EBIKE = "cycling-electric"


@dataclass
class MapLocation:
    """
    Dataclass representing a physical location
    """
    lat: float
    lon: float
    street_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    post_code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None

    def __eq__(self, other):
        """
        Override default behavior to account for lat/lon rounding errors since
        equal street addresses represent the same location.
        :param other: MapLocation to compare to this object
        :return: True if the `MapLocation`s are equivalent
        """
        if self.lat == other.lat and self.lon == other.lon:
            return True
        elif all((self.name == other.name,
                  self.street_number == other.street_number,
                  self.street == other.street,
                  self.city == other.city,
                  self.state == other.state,
                  self.country == other.country)):
            return True
        return False

    def __hash__(self) -> int:
        """
        Override hash for equality checks, i.e. when casting a list of results
        to a set.
        """
        if all((self.street_number, self.street, self.city,
                self.state, self.country)):
            hash_dict = {k: v for k, v in self.as_dict().items()
                         if k in ('street_number',
                                  'street',
                                  'city',
                                  'state',
                                  'country')}
        else:
            hash_dict = {'lat': self.lat,
                         'lon': self.lon}
        return hash(json.dumps(hash_dict))

    def __str__(self) -> str:
        """
        Get a human-readable string location name, address, and coordinates if
        available.
        """
        if all((self.street_number, self.street, self.city,
                self.state, self.country)):
            return f"{self.name}|{self.street_number} {self.street}|" \
                   f"{self.city}, {self.state} {self.post_code}, " \
                   f"{self.country}|({self.lat}, {self.lon})"
        else:
            return f"{self.lat}, {self.lon}"

    def as_dict(self) -> dict:
        """
        Get a dict representation of this MapLocation
        """
        return {'lat': self.lat,
                'lon': self.lon,
                'street_number': self.street_number,
                'street': self.street,
                'city': self.city,
                'county': self.county,
                'state': self.state,
                'country': self.country,
                'post_code': self.post_code,
                'name': self.name,
                'type': self.type,
                'icon': self.icon}

    @staticmethod
    def from_dict(location_dict: dict):
        """
        Create a `MapLocation` from a dict as returned by `MapLocation.as_dict`.
        :param location_dict:
        :return:
        """
        return MapLocation(**location_dict)

    @staticmethod
    def from_nominatim(location: Location):
        address = location.raw.get('address')
        if not address:
            # TODO: user_agent and URL from configuration or deprecate handling
            #   and just raise a ValueError here?
            address = Nominatim().reverse((location.latitude,
                                           location.longitude))
            address = address.raw.get('address')

        return MapLocation(location.latitude, location.longitude,
                           street_number=address.get('house_number'),
                           street=address.get('road'),
                           city=address.get('city',
                                            address.get('town',
                                                        address.get('village'))),
                           county=address.get('county'),
                           post_code=address.get('postcode'),
                           state=address.get('state'),
                           country=address.get('country'),
                           name=address.get('shop'),
                           type=location.raw.get('type'),
                           icon=location.raw.get('icon'))


@dataclass
class Route:
    """
    Dataclass representing a route between two locations
    """
    distance_meters: float
    duration_seconds: int
    num_waypoints: int
    bounding_box: List[float]
    steps: List[dict]
    geometry: str
