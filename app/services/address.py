import os
import requests
from typing import Dict, Optional, Tuple
from ..models import Location, db


def verify_address(address: str) -> Tuple[bool, Dict]:
    """
    Verifies an address using the Google Maps Geocoding API.
    Returns a tuple of (is_valid, details) where details contains the formatted address
    and coordinates if valid, or error information if invalid.
    
    Args:
        address (str): The address to verify
        
    Returns:
        Tuple[bool, Dict]: (is_valid, details)
            - is_valid: Boolean indicating if the address is valid
            - details: Dictionary containing either:
                - For valid addresses: formatted_address, lat, lng
                - For invalid addresses: error message
    """
    if not address:
        return False, {"error": "No address provided"}

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return False, {"error": "Google Maps API key not configured"}

    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={address}&key={api_key}"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            location = result['geometry']['location']
            
            # Get the formatted address from Google's response
            formatted_address = result.get('formatted_address', address)
            
            return True, {
                "formatted_address": formatted_address,
                "lat": location['lat'],
                "lng": location['lng'],
                "place_id": result.get('place_id'),  # Adding place_id for future reference
                "types": result.get('types', [])  # Adding types for additional context
            }
        else:
            return False, {
                "error": f"Address not found: {data.get('status', 'Unknown error')}"
            }

    except requests.RequestException as e:
        return False, {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}


def create_location_with_verified_address(user_id: int, name: str, address: str) -> Tuple[bool, Optional[Location]]:
    """
    Creates a new location with a verified address.
    
    Args:
        user_id (int): The ID of the user creating the location
        name (str): The name of the location
        address (str): The address to verify and save
        
    Returns:
        Tuple[bool, Optional[Location]]: (success, location)
            - success: Boolean indicating if the location was created successfully
            - location: The created Location object if successful, None if failed
    """
    is_valid, details = verify_address(address)
    
    if not is_valid:
        return False, None
        
    try:
        # Create new location with the formatted address and coordinates
        location = Location(
            user_id=user_id,
            name=name,
            address=details['formatted_address'],  # Use the formatted address from Google
            latitude=details['lat'],  # Save the latitude
            longitude=details['lng']  # Save the longitude
        )
        
        db.session.add(location)
        db.session.commit()
        
        return True, location
        
    except Exception as e:
        db.session.rollback()
        return False, None


def get_address_components(address: str) -> Optional[Dict]:
    """
    Gets detailed address components (street, city, state, etc.) for a given address.
    
    Args:
        address (str): The address to analyze
        
    Returns:
        Optional[Dict]: Dictionary containing address components if successful,
                       None if the address is invalid
    """
    is_valid, result = verify_address(address)
    
    if not is_valid:
        return None
        
    api_key = os.environ.get("GOOGLE_API_KEY")
    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={address}&key={api_key}"
    )
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            components = {}
            for component in data['results'][0]['address_components']:
                types = component['types']
                if 'street_number' in types:
                    components['street_number'] = component['long_name']
                elif 'route' in types:
                    components['street'] = component['long_name']
                elif 'locality' in types:
                    components['city'] = component['long_name']
                elif 'administrative_area_level_1' in types:
                    components['state'] = component['long_name']
                elif 'postal_code' in types:
                    components['postal_code'] = component['long_name']
                elif 'country' in types:
                    components['country'] = component['long_name']
            
            return components
            
    except Exception:
        return None
    
    return None 