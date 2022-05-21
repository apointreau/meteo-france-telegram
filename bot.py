from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from get_forecast import *
from environment import *
from get_observation import *
from get_city_from_gps import *

city_per_chat_id = {}
client_per_chat_id = {}


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def is_user_allowed(update):
    return update.message.from_user.id in allowed_user_id


def start(update, context):
    """Send a message when the command /start is issued."""

    assert(is_user_allowed(update))
    update.message.reply_text('Bonjour ! Commencez en utilisant /set' +
                              ' nom de la ville \U0001F5FA. Ensuite, faites /24h pour' +
                              ' les prévisions dans les 24 heures ou bien' +
                              ' /get n pour les previsions dans n jours !\U0001F324\n\n' +
                              "Vous pouvez m'envoyer votre localisation depuis le" +
                              " menu pièce jointe pour que je l'utilise !\U0001F4CD")


def set_city(update, context):
    """Set the current city with /set city_name to later display weather."""

    assert(is_user_allowed(update))

    if len(context.args) == 0:
        update.message.reply_text("Trop peu d'arguments ont été donnés.")
    else:
        city_str = ""
        for e in context.args:
            city_str += e+' '
        city_str = city_str[:-1]

        city, client = look_for_city(str(city_str))
        if city == None:
            update.message.reply_text(
                "Désolé, je n'ai pas trouvé votre ville ! \U0000274C")
            return

        city_per_chat_id[str(update.message.chat_id)] = city
        client_per_chat_id[str(update.message.chat_id)] = client
        update.message.reply_text(
            'Ville choisie : ' + str(city) + ' \U0001F9ED.')


def set_GPS_location(update, context):
    """Set the location of interest thanks to GPS location."""
    assert(is_user_allowed(update))

    latitude = latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    city_str = get_current_city_from_gps(latitude, longitude)

    city, client = look_for_city(city_str, latitude=latitude,
                                 longitude=longitude)

    if city == None:
        update.message.reply_text(
            "Désolé, je n'ai pas trouvé votre ville ! \U0000274C")
        return

    city_per_chat_id[str(update.message.chat_id)] = city
    client_per_chat_id[str(update.message.chat_id)] = client
    update.message.reply_text('Ville choisie : ' + str(city) + ' \U0001F9ED.')


def get_precise_date_forecast(update, context):
    """Get weather forecast on a specified day."""

    assert(is_user_allowed(update))
    pretty_printed_results = ""

    if city_per_chat_id.get(str(update.message.chat_id)) == None:
        update.message.reply_text('Merci de spécifier la ville avec '
                                  + '/set "nom de la ville"')
        return
    if len(context.args) == 0:
        context.args.append('0')

    if len(context.args) > 1:
        update.message.reply_text('Utilisation : /get nombre_de_jours')
        return
    if int(context.args[0]) > 9 or int(context.args[0]) < 0:
        update.message.reply_text('Prédictions à 9 jours maximum !')
        return

    chat_id = str(update.message.chat_id)
    results, last_update = get24h_forecast(city_per_chat_id.get(chat_id),
                                           client_per_chat_id.get(chat_id),
                                           datetime.now() + timedelta(days=int(context.args[0])))

    pretty_printed_results = ("Voici les previsions pour : " +
                              str(city_per_chat_id.get(chat_id)) +
                              ' à ' + datetime.now().strftime('%H:%M')
                              + '.\n\nDernière mise à jour le '+last_update.strftime('%d/%m @ %Hh%M')+'.\n\n')

    if context.args[0] == '0':
        current_weather = get_current_observation(city_per_chat_id.get(str(
            update.message.chat_id)))

        pretty_printed_results += pretty_print_current_observation(
            current_weather)

    pretty_printed_results += pretty_print_results(results)
    update.message.reply_text(pretty_printed_results)


def get_24h_forecast(update, context):
    """Get weather forecast for the rest of the day."""
    context.args.append('0')
    get_precise_date_forecast(update, context)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.location, set_GPS_location))

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set", set_city, pass_args=True))
    dp.add_handler(CommandHandler("24h", get_24h_forecast))
    dp.add_handler(CommandHandler(
        "get", get_precise_date_forecast, pass_args=True))
    #dp.add_handler(CommandHandler("gps", set_GPS_location))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
