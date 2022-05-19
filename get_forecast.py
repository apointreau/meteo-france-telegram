from meteofrance_api import MeteoFranceClient
from datetime import datetime, timedelta
from pytz import utc, timezone

french_days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
               "Dimanche"]

icon_to_emoji = {
    "p26j": '\U000026C8',
    "p26n": '\U000026C8',
    "p12bisn": '\U0001F326',
    "p12bisj": '\U0001F326',
    "p13bisn": '\U0001F326',
    "p13bisj": '\U0001F326',
    "p3n": '\U00002601', #éclaircies
    "p3j": '\U00002601', #nuit éclairée
    "p2j": '\U0001F324', #ciel voilé
    "p2n": '\U0001F324', #nuit voilée
    "p4n" : '\U00002600', # Très nuageux
    "p4j" : '\U00002600', # Très nuageux
    "p1j": '\U00002600\U00002600', #grand soleil
    "p1n": '\U0001F311\U0001F311', #grande lune
    "p5n": '\U0001F32B', 
    "p5j": '\U0001F32B',
    "p24n": '\U0001F9CA',
    "p24j": '\U0001F9CA',
    "p16bisj": '\U000026C8',
    "p16bisn": '\U000026C8',
    "p14bisn" : '\U0001F327', # Averses
    "p14bisj" : '\U0001F327', # Averses
}

def look_for_city(city: str) :
    client = MeteoFranceClient()
    list_places = client.search_places(city)
    
    if len(list_places)>0:
        return list_places[0], client

    return None, None

def get24h_forecast(city, client, date) :
    """Test classical workflow usage with the Python library."""
    
    
    forecast_results=[]
    local_tz = timezone('Europe/PARIS')
    # Fetch weather forecast for the location
    my_place_weather_forecast = client.get_forecast_for_place(city)
    last_update = utc.localize(datetime.utcfromtimestamp(
                                    my_place_weather_forecast.updated_on))
    last_update = last_update.astimezone(local_tz)
    
    # Get the daily forecast
    my_place_daily_forecast = my_place_weather_forecast.forecast
    
    # print(my_place_daily_forecast)
    date = local_tz.localize(date)
        
    # now.astimezone(timezone('Europe/Paris'))
    
    for e in my_place_daily_forecast:
        
        forecast_date = utc.localize(datetime.utcfromtimestamp(e['dt']))
        forecast_date = forecast_date.astimezone(local_tz)

        if forecast_date.day < date.day:
            pass
        elif forecast_date.day > date.day:
            break
        else : 
            if ((date.day == datetime.now().day and forecast_date >= date)
                    or  date.day != datetime.now().day ):
                    
                    forecast_results.append((forecast_date, e['weather']['desc'],
                                            e['weather']['icon'], e['T']['value'], 
                                            e['rain'].get('1h'), e['clouds']))
        
    
    return forecast_results, last_update

def pretty_print_results(results):
    pretty_printed_results = ""
    last_day = ""
    for e in results:
        forecast_date = e[0]
        if last_day != french_days[forecast_date.weekday()]:
            if last_day != "":
                pretty_printed_results += ('\n-------------------'+
                                            '--------------\n\n')
            last_day = french_days[forecast_date.weekday()]
            pretty_printed_results += (french_days[forecast_date.weekday()]+' ' +
                                       forecast_date.strftime('%d') + ' :\n\n')

        pretty_printed_results += ('- ' +
                                   forecast_date.strftime('%Hh : ') + e[1])
        
        if e[4] !=None and e[4] > 0:  # rain announced
            pretty_printed_results += (' (' + str('%.0f'%(e[4]*100))+'%)')

        if icon_to_emoji.get(e[2]) != None:
            pretty_printed_results += (' '+icon_to_emoji.get(e[2]))
        else:
            pretty_printed_results += (' '+e[2])

        pretty_printed_results += (', '+str(int(e[3]))+'°C, ')
        pretty_printed_results += ('nuages : '+str(e[5])+'\n')
    
    return pretty_printed_results