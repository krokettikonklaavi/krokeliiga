from telegram import ReplyKeyboardMarkup
import sqlite3

db_path = r"C:\Users\veikk\projektit\krokeliiga\tilastot.db"
token_path = r'C:\Users\veikk\projektit\krokeliiga\token.txt'
perm_path = r'C:\Users\veikk\projektit\krokeliiga\luvat.txt'
customKeyboard = [['Ensimmäinen', 'Toinen'], ['Kolmas', 'Pääsi maaliin'], ['Peruuta']]
markup = ReplyKeyboardMarkup(customKeyboard, one_time_keyboard=True,
                             resize_keyboard=True)
SCORES = range(1)


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
        pv INT,
        kuu INT,
        pisteet INT,
        PRIMARY KEY (ukko, pv, kuu)
    )""")
    conn.commit()
    conn.close()
