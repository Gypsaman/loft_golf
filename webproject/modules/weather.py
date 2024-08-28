import requests
import json

#https://openweathermap.org/api/one-call-3

OpenWeatherAPIKey = '581ca2567f4727d12e7ae8401fb4815f'
kelvin_to_celsius = lambda k: k - 273.15
kelvin_to_faranheit = lambda k: (k - 273.15) * 9/5 + 32

API_key = OpenWeatherAPIKey
lat = 41.1792
lon = 73.1894
part = 'minutely,hourly,daily,alerts'

weather_qry = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_key}'

curr_weather = json.loads(requests.get(weather_qry).content.decode("utf-8"))
description = curr_weather['current']['weather'][0]['description']
faranheit = kelvin_to_faranheit(curr_weather['current']['temp'])
feels_like = kelvin_to_faranheit(curr_weather['current']['feels_like'])

print(f'{faranheit:.0f}F feels like {feels_like:.0f}F. {description} ')
    