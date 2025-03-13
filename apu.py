import sqlite3
from os import getenv, path

pa = path.join(path.dirname(path.abspath(__file__)), "data")
db_path = path.join(pa, "kroke.db")
log_path = path.join(pa, "krokebot.log")

ADMINS = getenv("ADMINS").split(",")


def permit(id: int):
    if str(id) in ADMINS:
        return True
    return False


def tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Maksut (
        nimi CHAR(64),
        maksu INT DEFAULT 0,
        PRIMARY KEY (nimi)
    )"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Tapahtumat (
        ukko CHAR(64),
        pvm CHAR(4),
        pisteet INT,
        PRIMARY KEY (ukko, pvm)
    )"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Kroket (
        pvm CHAR(4),
        nimi CHAR(64),
        PRIMARY KEY (pvm)
    )"""
    )
    conn.commit()
    conn.close()


def names(args: list):
    joined = " ".join(args)
    names = joined.split(",")
    for i in range(len(names)):
        names[i] = names[i].strip()
    return names


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
