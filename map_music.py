"""Functions for Spotify"""
import base64
import json
import folium
import pycountry
from dotenv import load_dotenv
import requests
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim

load_dotenv()

client_id = '256f50561c9440cabffa7e004e4de104'
client_secret = 'c2b3c093d96e4df080a67e3747929546'


def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type':'client_credentials'}
    result = requests.post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token


def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}


def search_for_artist(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={artist_name}&type=artist&limit=1'

    query_url = url + query
    result = requests.get(query_url, headers = headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        print('No artist with this name exists...')
        return None
    return json_result[0]


def search_for_track(token, track_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={track_name}&type=track&limit=1'
    query_url = url + query
    result = requests.get(query_url, headers = headers)
    json_result = json.loads(result.content)['tracks']['items']
    if len(json_result) == 0:
        print('No tracks with this name exists...')
        return None
    return json_result[0]


def get_songs_by_artist(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=UA'
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result


def location(name: str) -> tuple:
    '''
    The function returns latitude and longtitude of the place
    >>> location('Новий Яричів')
    (49.9071883, 24.3026191)
    >>> location('Los Angeles')
    (34.0536909, -118.242766)
    '''
    geolocator = Nominatim(user_agent="nominatim.openstreetmap.org")
    location1 = geolocator.geocode(name)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    return (location1.latitude, location1.longitude)


def map_creator(artist_name):
    html = """<h4>Country: {}</h4>"""
    token = get_token()
    result = search_for_artist(token, artist_name)
    artist_id = result['id']
    songs = get_songs_by_artist(token, artist_id)
    song_1 = f"{songs[0]['name']}"
    tracks = search_for_track(token, song_1)
    available_markets = tracks['available_markets']
    available_markets_locations = [pycountry.countries.get(alpha_2 = i) for i in available_markets]
    available = []
    for j in available_markets_locations:
        if j is not None:
            try:
                available.append((j.name, location(j.name)))
            except GeocoderUnavailable:
                continue

    my_map = folium.Map(zoom_start = 100)
    figure = folium.FeatureGroup(name = 'available market')

    for markers_counter, _ in enumerate(available):
        iframe = folium.IFrame(html=html.format(available[markers_counter][0]),
                          width=200,
                          height=25)
        figure.add_child(folium.Marker(location=[available[markers_counter][1][0],
        available[markers_counter][1][1]],
                popup=folium.Popup(iframe),
                icon=folium.Icon(color = "black",
                icon = "fa-sharp fa-solid fa-volume-high", prefix = 'fa')))
        my_map.add_child(figure)
    my_map.save('map2.html')