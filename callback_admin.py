import sqlite3
import apu
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from logg import Logger

logger = Logger(apu.log_path).logger


# -----------------------------------UUSI---------------------------------------
async def uusi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan",
        )
        return
    names = apu.names(context.args)
    if "" in names:
        await update.message.reply_text(
            "Anna parametriksi pelaajan nimi, jonka haluat lisätä "
            "tietokantaan. Jos haluat lisätä useamman pelaajan kerralla, "
            "erota nimet pilkulla.",
        )
        return
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    ins = """
        INSERT INTO Maksut
        VALUES (?, ?)
    """
    added = []
    notadded = []
    for name in names:
        name = name.lower()
        cursor.execute(sel, (name,))
        rows = cursor.fetchall()
        if len(rows) == 1:
            added.append(name)
        else:
            notadded.append(name)
            cursor.execute(ins, (name, 0))
    logger.info(update.effective_user.full_name + " added a new player.")
    if len(added) == 0:
        conn.commit()
        await update.message.reply_text("Henkilö(t) lisätty onnistuneesti tietokantaan")
    elif len(notadded) == 0:
        await update.message.reply_text(
            "Kaikki parametriksi annetut pelaajat ovat jo valmiiksi lisätty "
            "tietokantaan.",
        )
    else:
        conn.commit()
        await update.message.reply_text(
            "Henkilö(t) {} lisätty tietokantaan. Loput pelaajista olivat jo "
            "valmiiksi tietokannassa.".format(notadded),
        )
    conn.close()


# -----------------------------------MAKSU--------------------------------------
async def maksu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia muuttaa pelaajien liigamaksun tilaa.",
        )
        return
    names = apu.names(context.args)
    if "" in names:
        await update.message.reply_text(
            "Anna argumentiksi vähintään yksi pelaaja, jonka haluat "
            "merkitä maksaneeksi. Jos haluat merkitä useamman pelaajan "
            "kerralla, erota nimet pilkulla.",
        )
        return
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    added = []
    notadded = []
    for name in names:
        name = name.lower()
        cursor.execute(sel, (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            notadded.append(name)
        else:
            added.append(name)
    upd = """
        UPDATE Maksut
        SET maksu = 1
        WHERE nimi = ?
    """
    for name in added:
        cursor.execute(upd, (name,))
    conn.commit()
    conn.close()
    logger.info(
        update.effective_user.full_name + " updated the payment status " "of a player."
    )
    if len(notadded) == 0:
        await update.message.reply_text("Maksu päivitetty onnistuneesti pelaajille.")
    elif len(added) == 0:
        await update.message.reply_text(
            "Ketään kyseisistä pelaajista ei ole vielä lisätty "
            "tietokantaan. Lisää pelaajat ensin komennolla /uusi.",
        )
    else:
        await update.message.reply_text(
            "Maksu päivitetty pelaajille {}. Pelaajia"
            " {} ei ole vielä lisätty tietokantaan. "
            "Lisää pelaajat ensin komennolla /uusi."
            "".format(added, notadded),
        )


# -----------------------------------SIJOITUS-----------------------------------
async def pisteet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia lisätä pisteitä " "tietokantaan."
        )
        return
    names = apu.names(context.args)
    if len(names) < 2 or not names[0].isdigit() or not int(names[0]) in range(1, 6):
        await update.message.reply_text(
            "Anna ensimmäisenä parametrinä pisteet ja tämän jälkeen "
            "henkilöt jotka saivat kyseiset pisteet. Erota parametrit "
            "pilkulla. Pisteiden tulee olla välillä [1,5].",
        )
        return
    if "" in names:
        await update.message.reply_text("Syöte on viallinen.")
        return
    points = int(names[0])
    names = names[1:]
    now = datetime.now()
    pvm = now.strftime("%m%d")
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel1 = """
        SELECT *
        FROM Tapahtumat
        WHERE ukko = ? AND pvm = ?
    """
    sel2 = """
        SELECT *
        FROM Kroket
        WHERE pvm = ?
    """
    sel3 = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    cursor.execute(sel2, (pvm,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        await update.message.reply_text(
            "Tälle päivälle ei ole tallennettu osakilpailua. Komennolla "
            "/kroke voit lisätä tälle päivälle osakilpailun.",
        )
        conn.close()
        return
    notin = []
    for name in names:
        name = name.lower()
        cursor.execute(sel3, (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            notin.append(name)
    if len(notin) > 0:
        await update.message.reply_text(
            "Pelaajia {} ei ole lisätty tietokantaan. Lisää heidät ensin "
            "komennolla /uusi.".format(notin),
        )
        conn.close()
        return
    added = []
    notadded = []
    for name in names:
        name = name.lower()
        cursor.execute(sel1, (name, pvm))
        rows = cursor.fetchall()
        if len(rows) == 0:
            apu.piste(update, context, name, points, pvm)
            added.append(name)
        else:
            notadded.append(name)
    logger.info(update.effective_user.full_name + " added points to players.")
    conn.close()
    if len(notadded) == 0:
        await update.message.reply_text("Pisteet lisätty onnistuneesti pelaajille.")
    elif len(added) == 0:
        await update.message.reply_text("Kaikille pelaajille oli jo lisätty pisteet.")
    else:
        await update.message.reply_text(
            "Pelaajille {} lisätty pisteet. Pelaajille"
            " {} oli jo lisätty pisteet.".format(added, notadded),
        )


# -----------------------------------POISTA-------------------------------------
async def poista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia poistaa henkilöitä tietokannasta"
        )
        return
    names = apu.names(context.args)
    if names[0] == "" or len(names) > 1:
        await update.message.reply_text(
            "Anna argumentiksi yhden pelaajan nimi, jonka haluat poistaa "
            "tietokannasta. Tämä komento poistaa myös kaikki pelaajan"
            "sijoitukset osakilpailuista.",
        )
    else:
        name = names[0].lower()
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        sel1 = """
            SELECT *
            FROM Maksut
            WHERE nimi = ?
        """
        del1 = """
            DELETE
            FROM Maksut
            WHERE nimi = ?
        """
        del2 = """
            DELETE
            FROM Tapahtumat
            WHERE ukko = ?
        """
        cursor.execute(sel1, (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            await update.message.reply_text(
                "Kyseinen pelaaja ei ole tietokannassa, joten häntä ei "
                "voitu poistaa.",
            )
            conn.close()
            return
        cursor.execute(del1, (name,))
        cursor.execute(del2, (name,))
        conn.commit()
        conn.close()
        logger.info(update.effective_user.full_name + " deleted a player.")
        await update.message.reply_text("Pelaaja poistettu tietokannasta.")


# -----------------------------------NIMI---------------------------------------
async def nimi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia muuttaapelaajien nimiä."
        )
        return
    names = apu.names(context.args)
    if "" in names or not len(names) == 2:
        await update.message.reply_text(
            "Anna 1. argumentiksi yhden pelaajan nimi, jonka haluat "
            "muuttaa ja 2. argumentiksi uusi nimi.",
        )
        return
    name0 = names[0].lower()
    name1 = names[1].lower()
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel1 = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    upd1 = """
        UPDATE Maksut
        SET nimi = ?
        WHERE nimi = ?
    """
    upd2 = """
        UPDATE Tapahtumat
        SET ukko = ?
        WHERE ukko = ?
    """
    cursor.execute(sel1, (name0,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        await update.message.reply_text(
            "Kyseinen pelaaja ei ole tietokannassa, joten hänen nimeä ei "
            "voitu muuttaa.",
        )
        conn.close()
        return
    cursor.execute(sel1, (name1,))
    rows = cursor.fetchall()
    if not len(rows) == 0:
        await update.message.reply_text(
            "Tietokannassa on jo henkilö, jonka nimi on sama kuin "
            "parametriksi annettu uusi nimi. Nimeä ei muutettu.",
        )
        conn.close()
        return
    cursor.execute(upd1, (name1, name0))
    cursor.execute(upd2, (name1, name0))
    conn.commit()
    conn.close()
    logger.info(update.effective_user.full_name + " changed the name of a " "player.")
    await update.message.reply_text("Pelaajan nimi muutettu.")


# -----------------------------------PISTE--------------------------------------
async def piste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not apu.permit(update.effective_user.id):
        await update.message.reply_text(
            "Sinulla ei ole oikeuksia muuttaa tai lisätä tuloksia " "tietokantaan.",
        )
        return
    names = apu.names(context.args)
    if "" in names or not len(names) == 3:
        await update.message.reply_text(
            "Anna ensimmäiseksi parametriksi päivämäärä, jolle haluat "
            "lisätä tai muuttaa pisteet ja toiseksi paramatriksi henkilön, "
            "jolle tämä muutos tehdään. Anna kolmanneksi parametriksi "
            "uusi pistemäärä.",
        )
        return
    pvm = names[0].split(".")
    if not len(pvm) == 2:
        await update.message.reply_text(
            "Anna ensimmäiseksi parametriksi päivämäärä, jolle haluat "
            "lisätä tai muuttaa pisteet, muodossa dd.mm",
        )
        return
    if not pvm[0].isdigit() or not pvm[1].isdigit() or not names[2].isdigit():
        await update.message.reply_text(
            "Anna ensimmäiseksi parametriksi päivämäärä dd.mm, jolle haluat "
            "lisätä tai muuttaa pisteet. Anna kolmanneksi parametriksi "
            "uudet pisteet.",
        )
        return
    if int(names[2]) not in range(1, 6):
        await update.message.reply_text("Anna pisteet, jotka ovat välillä [1,5].")
        return
    pv = pvm[0]
    kuu = pvm[1]
    pvm = apu.fdate(kuu, pv)
    name = names[1].lower()
    p = int(names[2])
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel1 = """
        SELECT *
        FROM Tapahtumat
        WHERE ukko = ? AND pvm = ?
    """
    sel2 = """
        SELECT *
        FROM Kroket
        WHERE pvm = ?
    """
    upd1 = """
        UPDATE Tapahtumat
        SET pisteet = ?
        WHERE ukko = ? AND pvm = ?
    """
    ins1 = """
        INSERT INTO Tapahtumat
        VALUES(?, ?, ?)
    """
    cursor.execute(sel1, (name, pvm))
    rows1 = cursor.fetchall()
    cursor.execute(sel2, (pvm,))
    rows2 = cursor.fetchall()
    if len(rows1) == 0 and len(rows2) == 1:
        cursor.execute(ins1, (name, pvm, p))
        conn.commit()
        logger.info(
            update.effective_user.full_name + " added a placement for a "
            "player in a competition."
        )
        await update.message.reply_text(
            "Henkilöllä ei ollut vielä merkintää kyseisen päivän "
            "osakilpailusta, joten se lisättiin.",
        )
    elif len(rows1) > 0 and len(rows2) == 1:
        cursor.execute(upd1, (p, name, pvm))
        conn.commit()
        logger.info(
            update.effective_user.full_name + " changed the result of a "
            "player in a single competition."
        )
        await update.message.reply_text(
            "Henkilön sijoitus osakilpailussa muutettu onnistuneesti"
        )
    else:
        await update.message.reply_text(
            "Kyseiselle päivälle ei ole lisätty osakilpailua. Komennolla "
            "/kroke dd.mm voit lisätä osakilpailun tietylle päivälle.",
        )
        return
    conn.close()
