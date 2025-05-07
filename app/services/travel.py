import os
import requests
from ..models import Location
from typing import Union, Dict, Tuple


def format_coordinates(lat: float, lng: float) -> str:
    """
    Formats latitude and longitude into a string format accepted by Google APIs.
    """
    return f"{lat},{lng}"


def get_travel_times(origin: Union[str, Tuple[float, float]], 
                    destination: Union[str, Tuple[float, float]]) -> Dict[str, str]:
    """
    Queries the Google Distance Matrix API for travel times across multiple modes.
    Returns a dictionary with travel durations for each mode.
    
    Args:
        origin: Either a string address or a tuple of (latitude, longitude)
        destination: Either a string address or a tuple of (latitude, longitude)
    """
    if not origin or not destination:
        raise ValueError("Both origin and destination must be provided.")

    api_key = os.environ.get("GOOGLE_API_KEY")
    modes = ['driving', 'walking', 'bicycling', 'transit']
    results = {}

    # Format origin and destination
    origin_str = format_coordinates(*origin) if isinstance(origin, tuple) else origin
    dest_str = format_coordinates(*destination) if isinstance(destination, tuple) else destination

    for mode in modes:
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin_str}&destinations={dest_str}"
            f"&mode={mode}&key={api_key}"
        )
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'OK':
            try:
                duration = data['rows'][0]['elements'][0]['duration']['text']
                distance = data['rows'][0]['elements'][0]['distance']['text']
                results[mode] = {
                    'duration': duration,
                    'distance': distance
                }
            except (KeyError, IndexError):
                results[mode] = {
                    'duration': "Unavailable",
                    'distance': "Unavailable"
                }
        else:
            results[mode] = {
                'duration': "API error",
                'distance': "API error"
            }

    return results


def compare_locations(new_location_address: str, saved_location_id: int, user_id: int) -> Tuple[Location, Dict]:
    """
    Compares travel times between a new address and a saved location for a user.
    Returns a tuple: (saved_location, results dict).
    """
    if not new_location_address or not saved_location_id:
        raise ValueError("Missing new location or saved location ID.")

    saved_location = Location.query.filter_by(id=saved_location_id, user_id=user_id).first()

    if not saved_location:
        raise ValueError("Saved location not found or does not belong to user.")

    results = get_travel_times(new_location_address, saved_location.address)
    return saved_location, results


def compare_locations_by_coordinates(new_location_coords: Tuple[float, float], 
                                   saved_location_id: int, 
                                   user_id: int) -> Tuple[Location, Dict]:
    """
    Compares travel times between a new location (using coordinates) and a saved location.
    Returns a tuple: (saved_location, results dict).
    
    Args:
        new_location_coords: Tuple of (latitude, longitude)
        saved_location_id: ID of the saved location to compare against
        user_id: ID of the user who owns the saved location
    """
    if not new_location_coords or not saved_location_id:
        raise ValueError("Missing coordinates or saved location ID.")

    saved_location = Location.query.filter_by(id=saved_location_id, user_id=user_id).first()

    if not saved_location:
        raise ValueError("Saved location not found or does not belong to user.")

    if not saved_location.latitude or not saved_location.longitude:
        # Fall back to address-based comparison if coordinates aren't available
        return compare_locations(
            new_location_address=format_coordinates(*new_location_coords),
            saved_location_id=saved_location_id,
            user_id=user_id
        )

    # Use coordinates for comparison
    results = get_travel_times(
        new_location_coords,
        (saved_location.latitude, saved_location.longitude)
    )
    return saved_location, results
