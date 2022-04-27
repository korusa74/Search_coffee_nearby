import json
import requests
import folium
import os
from flask import Flask
from geopy import distance


API_KEY = os.environ['MY_API_KEY']


def open_coffee_file():
    with open("coffee.json", "r", encoding='CP1251') as my_file:
        return my_file.read()


def fetch_coordinates(API_KEY, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    plcs = response.json()['response']['GeoObjectCollection']['featureMember']

    if not plcs:
        return None

    most_relevant = plcs[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_user_posts(coffe):
    return coffe['distance']


def hello_world():
    with open('index.html') as file:
        return file.read()


def main():
    list_coffee = []
    loc_my = list(fetch_coordinates(API_KEY, input('Где Вы находитесь? ')))
    coffee_list = json.loads(open_coffee_file())
    for coffee in coffee_list:
        coffee_name = coffee["Name"]
        crdnts_coffee = coffee["geoData"]['coordinates']
        crdnts_coffee[0], crdnts_coffee[1] = crdnts_coffee[1], crdnts_coffee[0]
        latitude = crdnts_coffee[0]
        longitude = crdnts_coffee[1]
        distance_coffee = distance.distance(loc_my, crdnts_coffee).km
        coffee_dict = {
            'title': coffee_name,
            'distance': distance_coffee,
            'latitude': latitude,
            'longitude': longitude
        }
        list_coffee.append(coffee_dict)
    five_coffee = sorted(list_coffee, key=get_user_posts)[0:5]
    m = folium.Map(
        location=[loc_my[0], loc_my[1]],
        zoom_start=15)
    for coffee in five_coffee:
        folium.Marker(
            location=[coffee['latitude'], coffee['longitude']],
            tooltip=coffee['title']).add_to(m)
    m.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
