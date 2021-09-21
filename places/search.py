from dataclasses import dataclass
from typing import Optional
from typing import Union
from typing import Type
from typing import Callable
from typing import Any
import googlemaps


@dataclass
class Place:
    name: str
    website: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    rating: float
    ratings_number: int
    place_id: str
    types: Optional[Union[str, list[str]]]
    google_url: Optional[str]
    status: str


class SearchBadResponse(Exception):
    """Raise for a bad response when performing an operation on the Places API"""


class MassSearch:
    def __init__(self, query: str, key: Union[str, Callable[..., str]]):
        self.key = key if isinstance(key, str) else key()
        self.client = googlemaps.Client(self.key)
        self.query = query

    def places(self, fetch_additional: bool = False) -> list[Type[Place]]:
        raw_response = self.client.places(self.query)
        self.check_status(raw_response['status'], raise_on_bad=True)
        results = raw_response['results']
        _places = self.parse_places(results)
        if fetch_additional:
            self.update_details(_places)
        return _places

    @staticmethod
    def parse_places(places_results_response: dict[Any]) -> list[Type[Place]]:
        places = []
        for result in places_results_response:
            name = result['name']
            address = result['formatted_address']
            rating = result['rating']
            ratings_number = result['user_ratings_total']
            place_id = result['place_id']
            types = result['types']
            status = result['business_status']
            website = None
            phone = None
            google_url = None
            p = Place(
                name,
                website,
                address,
                phone,
                rating,
                ratings_number,
                place_id,
                types,
                google_url,
                status,
            )
            places.append(p)

        return places

    def update_details(self, places_list: list[Type[Place]]):
        for place in places_list:
            details = self.details(place.place_id)
            place.website = details['website']
            place.phone = details['phone']
            place.google_url = details['google_url']

    @staticmethod
    def check_status(status: str, raise_on_bad: bool = True):
        if status == 'OK' or status == 'ZERO_RESULTS':
            return True
        else:
            if status == 'OVER_QUERY_LIMIT':
                err = '{} error from service. Billing might not be enabled in your account or you might have exceeded QPS limit'.format(
                    status)
            elif status == 'INVALID_REQUEST':
                err = '{} error from service. The API request is likely malformed'.format(status)
            elif status == 'REQUEST_DENIED':
                err = '{} error from service. Your API key or client information might be invalid'.format(status)
            elif status == 'UNKNOWN_ERROR':
                err = '{} error from service'.format(status)
            else:
                err = '{} error from service. Something is really wrong'.format(status)

        if raise_on_bad:
            raise SearchBadResponse(err)

        return False

    def details(self, place_id: str) -> dict[Any]:
        raw_response = self.client.place(place_id)
        self.check_status(raw_response['status'], raise_on_bad=True)
        result = raw_response['result']
        details = self.parse_details(result)
        return details

    @staticmethod
    def parse_details(place_result_response: dict[Any]) -> dict[Any]:
        details = {
            'website': place_result_response.get('website'),
            'phone': place_result_response.get('formatted_phone_number'),
            'google_url': place_result_response.get('url'),
        }
        return details

    def filter(self, params: dict[Any]):
        pass

    def handle_next_page(self):
        pass
