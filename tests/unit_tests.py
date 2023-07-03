import unittest

from geopy.point import Point
from geopy.location import Location


class TestDataClasses(unittest.TestCase):
    def test_from_nominatim(self):
        from navigation_api.data_classes import MapLocation
        test_lat = 47.8219924
        test_lon = -122.2953334
        test_location = Location(
            address='Fred Meyer, 194th Street Southwest, '
                    'Lynnwood, Snohomish County, '
                    'Washington, 98036, United States',
            point=Point(test_lat, test_lon),
            raw={'place_id': 21362466,
                 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                 'osm_type': 'node',
                 'osm_id': 2409491863,
                 'boundingbox': ['47.8219424', '47.8220424', '-122.2953834', '-122.2952834'],
                 'lat': '47.8219924', 'lon': '-122.2953334',
                 'display_name': 'Fred Meyer, 194th Street Southwest, '
                                 'Lynnwood, Snohomish County, Washington, '
                                 '98036, United States',
                 'class': 'shop',
                 'type': 'supermarket',
                 'importance': 0.2001,
                 'icon': 'https://nominatim.openstreetmap.org/ui/mapicons/shopping_supermarket.p.20.png'})
        map_location = MapLocation.from_nominatim(test_location)
        self.assertEqual(map_location.lat, test_lat)
        self.assertEqual(map_location.lon, test_lon)
        self.assertEqual(map_location.city, "Lynnwood")
        self.assertEqual(map_location.state, "Washington")
        self.assertEqual(map_location.post_code, "98036")
        self.assertEqual(map_location.county, "Snohomish County")
        self.assertEqual(map_location.country, "United States")
        self.assertEqual(map_location.name, "Fred Meyer")
        self.assertEqual(map_location.type, "supermarket")
        self.assertIsInstance(map_location.icon, str)


class TestLocationSearch(unittest.TestCase):
    def test_search_destination(self):
        from navigation_api.location import LocationSearch
        from navigation_api.data_classes import MapLocation
        anchor = Point(47.6769, -122.2060)
        search = LocationSearch(anchor)
        results = search.search_destination("Fred Meyer")
        self.assertIsInstance(results, set)
        self.assertGreaterEqual(len(results), 1)
        for result in results:
            self.assertIsInstance(result, MapLocation)
            # TODO: Test lat/lng in bounding box
        results = search.search_destination("123 5th Ave")
        self.assertIsInstance(results, set)
        self.assertGreaterEqual(len(results), 1)
        for result in results:
            self.assertIsInstance(result, MapLocation)
            # TODO: Test lat/lng in bounding box

    def test_search_address(self):
        from navigation_api.location import LocationSearch
        from navigation_api.data_classes import MapLocation
        anchor = Point(47.6769, -122.2060)
        search = LocationSearch(anchor)
        result = search.search_address("123 5th Ave", "Kirkland", "King County",
                                       "Washington", "United States")
        self.assertIsInstance(result, MapLocation)

        # Less precise location
        result_2 = search.search_address("123 5th Ave", "Kirkland")
        self.assertEqual(result, result_2)

        # Test location far from anchor
        result_3 = search.search_address("123 5th Ave", "New York")
        self.assertIsInstance(result_3, MapLocation)
        self.assertNotEqual(result_3, result)


class TestNavigation(unittest.TestCase):
    def test_get_routes(self):
        from navigation_api.navigation import NavigationSearch
        from navigation_api.data_classes import MapLocation, Route
        origin = MapLocation(lat=47.678177399999996, lon=-122.2073148196275)
        destination = MapLocation(lat=47.4797, lon=-122.2079)
        search = NavigationSearch(origin, destination)
        routes = search.get_routes()
        self.assertIsInstance(routes, list)
        for route in routes:
            self.assertIsInstance(route, Route)

        # Get Shortest
        shortest = search.get_shortest_route()
        for route in routes:
            self.assertLessEqual(shortest.distance_meters,
                                 route.distance_meters)

        # Get Fastest
        fastest = search.get_fastest_route()
        for route in routes:
            self.assertLessEqual(fastest.duration_seconds,
                                 route.duration_seconds)
