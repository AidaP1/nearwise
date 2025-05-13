import os
import requests
from ..models import Location
from typing import Dict, Tuple


def format_coordinates(lat: float, lng: float) -> str:
    """
    Formats latitude and longitude into a string format accepted by Google APIs.
    """
    return f"{lat},{lng}"


def get_travel_times(origin_coords: Tuple[float, float], 
                    destination_coords: Tuple[float, float]) -> Dict[str, Dict[str, str]]:
    """
    Queries the Google Distance Matrix API for travel times across multiple modes.
    Returns a dictionary with travel durations and distances for each mode.
    
    Args:
        origin_coords: Tuple of (latitude, longitude) for the origin
        destination_coords: Tuple of (latitude, longitude) for the destination
        
    Returns:
        Dict containing travel information for each mode:
        {
            'driving': {'duration': '15 mins', 'distance': '5.2 km'},
            'walking': {'duration': '45 mins', 'distance': '4.8 km'},
            ...
        }
    """
    if not origin_coords or not destination_coords:
        raise ValueError("Both origin and destination coordinates must be provided.")

    api_key = os.environ.get("GOOGLE_API_KEY")
    modes = ['driving', 'walking', 'bicycling', 'transit']
    results = {}

    # Format coordinates for API request
    origin_str = format_coordinates(*origin_coords)
    dest_str = format_coordinates(*destination_coords)

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


def compare_locations(new_location_coords: Tuple[float, float], 
                     saved_location_id: int, 
                     user_id: int) -> Tuple[Location, Dict[str, Dict[str, str]]]:
    """
    Compares travel times between a new location and a saved location using coordinates.
    Returns a tuple: (saved_location, results dict).
    
    Args:
        new_location_coords: Tuple of (latitude, longitude) for the new location
        saved_location_id: ID of the saved location to compare against
        user_id: ID of the user who owns the saved location
        
    Returns:
        Tuple containing:
        - The saved Location object
        - Dictionary of travel information for each mode
    """
    if not new_location_coords or not saved_location_id:
        raise ValueError("Missing coordinates or saved location ID.")

    # Validate new location coordinates
    lat, lng = new_location_coords
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        raise ValueError("Invalid coordinates")

    saved_location = Location.query.filter_by(id=saved_location_id, user_id=user_id).first()

    if not saved_location:
        raise ValueError("Saved location not found or does not belong to user.")

    if not saved_location.latitude or not saved_location.longitude:
        raise ValueError("Saved location is missing coordinates.")

    # Validate saved location coordinates
    if not (-90 <= saved_location.latitude <= 90) or not (-180 <= saved_location.longitude <= 180):
        raise ValueError("Invalid coordinates")

    # Use coordinates for comparison
    results = get_travel_times(
        new_location_coords,
        (saved_location.latitude, saved_location.longitude)
    )
    return saved_location, results
