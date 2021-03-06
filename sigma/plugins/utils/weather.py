import requests

from sigma.plugin import Plugin
from sigma.utils import create_logger

from config import OpenWeatherMapKey as owm_key


class Weather(Plugin):
    is_global = True
    log = create_logger('weather')

    async def on_message(self, message, pfx):

        if message.content.startswith(pfx + 'weather' + ' '):
            await self.client.send_typing(message.channel)
            cmd_name = 'Weather'
            try:
                self.log.info('User %s [%s] on server %s [%s], used the ' + cmd_name + ' command on #%s channel',
                              message.author,
                              message.author.id, message.server.name, message.server.id, message.channel)
            except:
                self.log.info('User %s [%s], used the ' + cmd_name + ' command.',
                              message.author,
                              message.author.id)
            owm_input = (str(message.content[len('weather') + 1 + len(pfx):]))
            city, ignore, country = owm_input.partition(', ')
            owm_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city + ',' + country + '&appid=' + owm_key
            owm_json = requests.get(owm_url).json()
            kelvin = 273.16
            print(owm_json)
            try:
                coord_lon = str(owm_json['coord']['lon'])
                coord_lat = str(owm_json['coord']['lat'])
                sys_country = str(owm_json['sys']['country'])
                sys_city = str(owm_json['name'])
                weather = str(owm_json['weather'][0]['main'])
                temp = (str(round(owm_json['main']['temp'] - kelvin)) + '°C')
                temp_f = (str(round((((owm_json['main']['temp'] - kelvin) * 9) / 5) + 32)) + '°F')
                humidity = (str(owm_json['main']['humidity']) + '%')
                pressure = (str(owm_json['main']['pressure']) + ' mb')
                temp_min_c = (str(round(owm_json['main']['temp_min'] - kelvin)) + '°C')
                temp_max_c = (str(round(owm_json['main']['temp_max'] - kelvin)) + '°C')
                temp_min_f = (str(round((((owm_json['main']['temp_min'] - kelvin) * 9) / 5) + 32)) + '°F')
                temp_max_f = (str(round((((owm_json['main']['temp_max'] - kelvin) * 9) / 5) + 32)) + '°F')
                if weather == 'Thunderstorm':
                    icon = ':thunder_cloud_rain:'
                elif weather == 'Drizzle':
                    icon = ':cloud:'
                elif weather == 'Rain':
                    icon = ':cloud_rain:'
                elif weather == 'Snow':
                    icon = ':cloud_snow:'
                elif weather == 'Clear':
                    icon = ':sunny:'
                elif weather == 'Clouds':
                    icon = ':white_sun_cloud:'
                elif weather == 'Extreme':
                    icon = ':cloud_tornado:'
                else:
                    icon = ':earth_americas:'
                weather_message = ('Weather in `' + sys_city + ', ' + sys_country + '` ' +
                                   'Lat: `' + coord_lat + '` | Lon: `' + coord_lon + '`\n\n' +
                                   'Current State: `' + weather + '` ' + icon + '\n\n' +
                                   'Details:\n```Current: ' + temp + ' (' + temp_f + ')\n' +
                                   'High: ' + temp_max_c + ' (' + temp_max_f + ')\n' +
                                   'Low: ' + temp_min_c + ' (' + temp_min_f + ')\n' +
                                   'Humidity: ' + humidity + '\nPressure: ' + pressure + '\n```')
                await self.client.send_message(message.channel, weather_message)
            except:
                try:
                    owm_error_code = str(owm_json['cod'])
                    if owm_error_code == '404':
                        await self.client.send_message(message.channel, 'Error: Requested location not found!')
                except:
                    await self.client.send_message(message.channel, 'Something went wrong, and we don\'t know what!')
