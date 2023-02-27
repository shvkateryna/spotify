"""Functions for Spotify"""
import base64
import os
import json
import folium
import pycountry
from dotenv import load_dotenv
import requests
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


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
        print('Не існує такого виконавця')
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
        print('Не існує такої пісні')
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=UA'
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

def available_market_function(artist_name):
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
            available.append(j.name)
    return available


token = get_token()
print('Привіт! Ця програма може допомогти тобі дізнатися таку інформацію про будь-якого виконавця:\n\
ID-виконавця, найпопулярніша його пісня, ID-пісні, мапа з країнами, у якій можуть слухати цю пісню.\n\
Спершу тобі потрібно ввести імʼя виконавця.')
user_input = input('>>> ')
try:
    artist_id = search_for_artist(token, user_input)['id']
    songs = get_songs_by_artist(token, artist_id)
    song_1 = f"{songs[0]['name']}"
    tracks = search_for_track(token, song_1)
    name_artist = search_for_artist(token, user_input)['name']
    id_track = tracks['id']
    while True:
        print('Обери, яку інформацію хочеш дізнатися.\n\
Введи "ID-виконавця", якщо хочеш дізнатися ID-виконавця\n\
Введи "Пісня", якщо хочеш дізнатися найпопулярнішу пісню виконавця\n\
Введи "ID-пісні", якщо хочеш дізнатися ID найпопулярнішої пісні виконавця\n\
Введи "Назва", якщо хочеш дізнатися імʼя виконавця\n\
Введи "Ринок", якщо хочеш дізнатися список країн, у яких можна прослуховувати цю пісню\n\
Введи "Вийти", якщо хочеш вийти з програми')
        user_input2 = input('>>> ')
        if user_input2.lower() == 'id-виконавця':
            print(artist_id)
        elif user_input2.lower() == 'пісня':
            print(song_1)
        elif user_input2.lower() == 'id-пісні':
            print(id_track)
        elif user_input2.lower() == 'ринок':
            print(available_market_function(user_input))
        elif user_input2.lower() == 'назва':
            print(name_artist)
        elif user_input2.lower() == 'вийти':
            break
        else:
            print('можливо, ти помилився, спробуй ще раз')
except (TypeError, IndexError):
    print('Можливо, ти помилився, спробуй ще раз')
