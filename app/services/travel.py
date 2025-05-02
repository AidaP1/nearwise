import os
import requests
from ..models import Location


def get_travel_times(origin, destination):
    """
    Queries the Google Distance Matrix API for travel times across multiple modes.
    Returns a dictionary with travel durations for each mode.
    """
    if not origin or not destination:
        raise ValueError("Both origin and destination must be provided.")

    api_key = os.environ.get("GOOGLE_API_KEY")
    modes = ['driving', 'walking', 'bicycling', 'transit']
    results = {}

    for mode in modes:
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin}&destinations={destination}"
            f"&mode={mode}&key={api_key}"
        )
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'OK':
            try:
                duration = data['rows'][0]['elements'][0]['duration']['text']
                results[mode] = duration
            except (KeyError, IndexError):
                results[mode] = "Unavailable"
        else:
            results[mode] = "API error"

    return results


def compare_locations(new_location_address, saved_location_id, user_id):
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
