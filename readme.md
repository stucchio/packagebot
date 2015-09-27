# Telegram tracking bot

I felt like playing with telegram, and I had some packages on the way, so I made a bot.

To use: Send a telegram message to `Incoming_pkg_bot` which contains the tracking code of your package. Currently USPS only.
You'll receive updates via telegram as the package moves.

Just type `stop` to stop receiving messages.

To run this bot, do the following:

1. Create a telegram bot, instructions [here](https://core.telegram.org/bots).
2. Get an API token from the USPS [here](https://www.usps.com/business/web-tools-apis/welcome.htm).
3. Put the assorted tokens into [config.py](packagebot/config.py).
4. Set up a postgres, and put the credentials into [config.py](packagebot/config.py).
5. `python scripts/bot.py`
