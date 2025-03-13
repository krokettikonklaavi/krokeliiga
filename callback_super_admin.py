from os import getenv
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes
import apu
from logg import Logger

logger = Logger(apu.log_path).logger

SUPER_ADMIN = getenv("SUPER_ADMIN")


# -----------------------------------KROKE--------------------------------------
async def kroke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if not user == SUPER_ADMIN:
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia lisätä uusia osakilpailuita."
        )
        return
    names = apu.names(context.args)
    sel = """
        SELECT *
        FROM Kroket
        WHERE pvm = ?
    """
    ins = """
        INSERT INTO Kroket
        VALUES(?, ?)
    """
    if names[0] == "":
        await update.message.reply_text(
            "Anna parametriksi osakilpailun päivämäärä ja osakilpailun "
            "nimi pilkulla erotettuna.",
        )
        return
    if "" in names:
        await update.message.reply_text(
            "Anna toisena parametrinä osakilpailun nimi pilkulla "
            "erotettuna päivämäärästä.",
        )
        return
    if len(names) == 2:
        pvm = names[0].split(".")
        if not len(pvm) == 2:
            await update.message.reply_text(
                "Anna parametriksi päivämäärä, jolle haluat "
                "lisätä osakilpailun, muodossa dd.mm",
            )
            return
        if not pvm[0].isdigit() or not pvm[1].isdigit():
            await update.message.reply_text(
                "Anna parametriksi päivämäärä dd.mm, jolle haluat lisätä "
                "osakilpailun.",
            )
            return
        pv = pvm[0]
        kuu = pvm[1]
        name = names[1]
        pvm = apu.fdate(kuu, pv)
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        cursor.execute(sel, (pvm,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(ins, (pvm, name))
            await update.message.reply_text("Osakilpailu lisätty tietokantaan.")
            conn.commit()
            logger.info(update.effective_user.full_name + " added a new playday.")
        else:
            await update.message.reply_text("Osakilpailu on jo tietokannassa.")
        conn.close()
    else:
        await update.message.reply_text(
            "Anna parametriksi osakilpailun päivämäärä ja osakilpailun "
            "nimi pilkulla erotettuna.",
        )


# -----------------------------------DELETE-------------------------------------
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.id == SUPER_ADMIN:
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia poistaa osakilpailuita."
        )
        return
    names = apu.names(context.args)
    if names[0] == "":
        await update.message.reply_text("Anna parametriksi osakilpailun päivämäärä.")
        return
    if len(names) == 1:
        pvm = names[0].split(".")
        if not len(pvm) == 2:
            await update.message.reply_text(
                "Anna parametriksi päivämäärä dd.mm, jolta haluat poistaa "
                "osakilpailun,",
            )
            return
        if not pvm[0].isdigit() or not pvm[1].isdigit():
            await update.message.reply_text(
                "Anna parametriksi päivämäärä dd.mm, jolta haluat poistaa "
                "osakilpailun,",
            )
            return
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        pv = pvm[0]
        kuu = pvm[1]
        pvm = apu.fdate(kuu, pv)
        sel1 = """
            SELECT *
            FROM Kroket
            WHERE pvm = ?
        """
        del1 = """
            DELETE
            FROM Kroket
            WHERE pvm = ?
        """
        cursor.execute(sel1, (pvm,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            await update.message.reply_text("Osakilpailu ei ole tietokannassa.")
            conn.close()
            return
        cursor.execute(del1, (pvm,))
        conn.commit()
        conn.close()
        logger.info(update.effective_user.full_name + " deleted a competition.")
        await update.message.reply_text("Osakilpailu poistettu tietokannasta.")
    else:
        await update.message.reply_text(
            "Anna parametriksi päivämäärä, jolta haluat "
            "poistaa osakilpailun, muodossa dd.mm",
        )


# -----------------------------------ERROR--------------------------------------
def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
