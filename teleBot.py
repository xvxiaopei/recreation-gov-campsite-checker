#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import camping
import argparse
from datetime import date, datetime, timedelta
from dateutil import rrule
import time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

INPUT_DATE_FORMAT = "%Y-%m-%d"
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    arglist = update.message.text.split(" ")
    campsite_type = None
    nights = None

    if len(arglist) >= 3:
        start_date, end_date, parks = arglist[0], arglist[1], arglist[2]
        if valid_date(start_date):
            start_date = datetime.strptime(start_date, INPUT_DATE_FORMAT)
        if valid_date(end_date):
            end_date = datetime.strptime(end_date, INPUT_DATE_FORMAT)
        parks = [int(park_id) for park_id in str(parks).split(" ")]

        if len(arglist) == 4:
            campsite_type = arglist[3]
        if len(arglist) == 5:
            campsite_type = arglist[3]
            nights = arglist[4]
        update.message.reply_text("Start checking availabilities every minute with " 
        + "start_date: " + str(start_date)
        + " end_date: " + str(end_date)
        + " parks: " + str(parks)
        + " campsite_type: " + str(campsite_type)
        + " nights: " + str(nights))

        avail = camping.execute_check_every_min(start_date, end_date, parks, campsite_type, nights)
    else:
        update.message.reply_text("Invalid checking args, use default"
        + "start_date: " + str(args.start_date)
        + " end_date: " + str(args.end_date)
        + " parks: " + str(args.parks)
        + " campsite_type: " + str(args.campsite_type)
        + " nights: " + str(args.nights))
        avail = camping.execute_check_every_min(args.start_date, args.end_date, args.parks, args.campsite_type, args.nights)
    if avail:
        update.message.reply_text(avail)
    


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1588125267:AAFGb3YcOyVHKrzU7iBLNUlNujMvEXzQGQI", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def valid_date(s):
    try:
        return datetime.strptime(s, INPUT_DATE_FORMAT)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def positive_int(i):
    i = int(i)
    if i <= 0:
        msg = "Not a valid number of nights: {0}".format(i)
        raise argparse.ArgumentTypeError(msg)
    return i

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true", help="Debug log level")
    parser.add_argument(
        "--start-date", required=True, help="Start date [YYYY-MM-DD]", type=valid_date
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="End date [YYYY-MM-DD]. You expect to leave this day, not stay the night.",
        type=valid_date,
    )
    parser.add_argument(
        "--nights",
        help="Number of consecutive nights (default is all nights in the given range).",
        type=positive_int,
    )
    parser.add_argument(
        "--campsite-type",
        help=(
            'If you want to filter by a type of campsite. For example '
            '"STANDARD NONELECTRIC" or TODO'
        ),
    )
    parks_group = parser.add_mutually_exclusive_group(required=True)
    parks_group.add_argument(
        "--parks",
        dest="parks",
        metavar="park",
        nargs="+",
        help="Park ID(s)",
        type=int,
    )
    parks_group.add_argument(
        "--stdin",
        "-",
        action="store_true",
        help="Read list of park ID(s) from stdin instead",
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    parks = args.parks or [p.strip() for p in sys.stdin]
    main()
