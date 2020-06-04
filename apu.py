import sqlite3
from os import path


pa = path.dirname(path.abspath(__file__))
token_path = path.join(pa, "token.txt")
perm_path = path.join(pa, "luvat.txt")
db_path = path.join(pa, "tilastot.db")


def permit(id: int):
    with open(perm_path, 'r') as permissions:
        if str(id) in permissions.read():
            return True
        else:
            return False


def get_token():
    with open(token_path, 'r') as token_file:
        token = token_file.readlines()[0].strip(" \n")
    return token


def tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Maksut (
        nimi CHAR(64),
        maksu INT DEFAULT 0,
        PRIMARY KEY (nimi)
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tapahtumat (
        ukko CHAR(64),
        pvm CHAR(4),
        pisteet INT,
        PRIMARY KEY (ukko, pvm)
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kroket (
        pvm CHAR(4),
        PRIMARY KEY (pvm)
    )""")
    conn.commit()
    conn.close()


def names(args: list):
    joined = ' '.join(args)
    names = joined.split(",")
    for i in range(len(names)):
        names[i] = names[i].strip()
    return names


def switch(placement: int):
    switcher = {
        1: 4,
        2: 3,
        3: 2,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
    }
    return switcher.get(placement)


def botM(update, context, message: str):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def piste(update, context, name: str, pisteet: int, pvm: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Tapahtumat
        VALUES (?, ?, ?)
    """
    cursor.execute(ins, (name, pvm, pisteet))
    conn.commit()
    conn.close()


def fdate(kuu: str, pv: str):
    if len(pv) == 1:
        pv = "0" + pv
    if len(kuu) == 1:
        kuu = "0" + kuu
    return kuu + pv
