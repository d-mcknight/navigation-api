from typing import Set, Optional

from geopy import Point
from geopy.geocoders.nominatim import Nominatim

from navigation_api.data_classes import MapLocation


class LocationSearch:
    def __init__(self, anchor_location: Point,
                 search_radius_degrees: float = 0.17):
        """
        Class representing a search session
        :param anchor_location: Anchor point (lat/lon) for search results
        :param search_radius_degrees: search area around `anchor_location`,
            specified in degrees
        """
        self.viewbox = ((anchor_location.latitude - search_radius_degrees,
                         anchor_location.longitude - search_radius_degrees),
                        (anchor_location.latitude + search_radius_degrees,
                         anchor_location.longitude + search_radius_degrees))
        # TODO: user_agent and URL from configuration
        self.api = Nominatim()

    def search_destination(self, query: str) -> Set[MapLocation]:
        """
        Search a destination by name or address within the specified `viewbox`
        :param query:
        :return:
        """
        search_results = self.api.geocode(query=query,
                                          exactly_one=False,
                                          addressdetails=True,
                                          bounded=True,
                                          viewbox=self.viewbox)
        search_results = set([MapLocation.from_nominatim(place)
                              for place in search_results])
        return search_results

    def search_address(self, street_address: str, city: str,
                       county: Optional[str] = None,
                       state: Optional[str] = None,
                       country: Optional[str] = None) -> Optional[MapLocation]:
        """
        Get a destination by street address
        :param street_address: street number and street name
        :param city: city name
        :param county: optional county name
        :param state: optional state name
        :param country: optional country name
        :return: MapLocation for the given address (if it exists
        """
        query = {'street': street_address,
                 'city': city,
                 'county': county,
                 'state': state,
                 'country': country}
        for key in set(query.keys()):
            if not query[key]:
                query.pop(key)
        search_result = self.api.geocode(query=query,
                                         exactly_one=True,
                                         addressdetails=True)
        if search_result:
            return MapLocation.from_nominatim(search_result)
