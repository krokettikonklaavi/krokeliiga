from telegram.ext import Application, CommandHandler
import apu
from callback import start, help, tulokset, pelaajat, joukkueet, osakilpailut
from callback_admin import uusi, maksu, pisteet, poista, nimi, piste
from callback_super_admin import kroke, error, delete
from os import getenv
from logg import Logger

TOKEN = getenv("TOKEN")

logger = Logger(apu.log_path).logger


async def post_init(app: Application):
    apu.tables()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("uusi", uusi))
    app.add_handler(CommandHandler("maksu", maksu))
    app.add_handler(CommandHandler("kroke", kroke))
    app.add_handler(CommandHandler("pisteet", pisteet))
    app.add_handler(CommandHandler("tulokset", tulokset))
    app.add_handler(CommandHandler("pelaajat", pelaajat))
    app.add_handler(CommandHandler("poista", poista))
    app.add_handler(CommandHandler("joukkueet", joukkueet))
    app.add_handler(CommandHandler("nimi", nimi))
    app.add_handler(CommandHandler("piste", piste))
    app.add_handler(CommandHandler("osakilpailut", osakilpailut))
    app.add_handler(CommandHandler("delete", delete))

    # Set error handler
    app.add_error_handler(error)

    logger.info("Post init done.")


def main():
    app = Application.builder().token(TOKEN).concurrent_updates(False).build()
    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
