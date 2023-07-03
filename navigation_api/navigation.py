from typing import List

from openrouteservice import Client
from openrouteservice.directions import directions

from navigation_api.data_classes import MapLocation, ModeOfTransportation, Route


class NavigationSearch:
    def __init__(self, origin_location: MapLocation,
                 destination_location: MapLocation,
                 ors_api_key: str,
                 mot: ModeOfTransportation = ModeOfTransportation.CAR):
        """
        Get navigation routes between 2 locations
        :param origin_location: Origin MapLocation
        :param destination_location: Destination MapLocation
        :param ors_api_key: OpenRouteService API Key
        :param mot: mode of transportation to get directions for
        """
        self.origin = origin_location
        self.destination = destination_location
        self._routes = None
        # TODO: ORS URL from configuration
        self.client = Client(key=ors_api_key)
        self.mode_of_transportation = mot

    @property
    def routes(self) -> List[Route]:
        if not self._routes:
            self.get_routes()
        return self._routes

    def get_routes(self) -> List[Route]:
        """
        Get routes from this object's origin to the destination
        :return: List of valid `Route` objects
        """
        routes = directions(self.client,
                            ((self.origin.lon, self.origin.lat),
                             (self.destination.lon, self.destination.lat)),
                            profile=self.mode_of_transportation.value,
                            units='m',
                            alternative_routes={"target_count": 3})
        routes = [Route(r['summary']['distance'],
                        round(r['summary']['duration']),
                        int(r['way_points'][1]),
                        r['bbox'],
                        r['segments'][0]['steps'],
                        r["geometry"]) for r in routes['routes']]
        self._routes = routes
        return routes

    def get_shortest_route(self) -> Route:
        self.routes.sort(key=lambda r: r.distance_meters)
        return self.routes[0]

    def get_fastest_route(self) -> Route:
        self.routes.sort(key=lambda r: r.duration_seconds)
        return self.routes[0]
