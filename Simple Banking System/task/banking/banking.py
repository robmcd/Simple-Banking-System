# Write your code here
import contextlib
import sqlite3
import random
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Dict
from typing_extensions import Self
import luhn

IIN = '400000'

DB_FILENAME = 'card.s3db'

CREATE_TABLE_STATEMENT = """
CREATE TABLE IF NOT EXISTS card ( 
    id INTEGER NOT NULL PRIMARY KEY,
    number TEXT UNIQUE,
    pin TEXT,
    balance INTEGER DEFAULT 0
);
"""

INSERT_ACCOUNT_STATEMENT = """
INSERT INTO card (number, pin) values (?, ?); 
"""

UPDATE_ACCOUNT_STATEMENT = """
UPDATE card SET pin = ?, balance = ? WHERE number = ?;
"""

SELECT_ACCOUNT_QUERY = """
SELECT id, number, pin, balance FROM card WHERE number = ?; 
"""


conn: Connection = None


def generate_pin():
    return f'{random.randint(0, 9999):04}'


def derive_card_number(account_number):
    card_number_prefix = f'{IIN}{account_number}'
    check_digit = luhn.generate(card_number_prefix)
    return f'{card_number_prefix}{check_digit}'


def derive_account_number(card_number):
    return card_number[6:-1]


def generate_account_number():
    account_number = f'{random.randint(0, 999999999):09}'
    while Account.get_account_from_db(derive_card_number(account_number)):
        account_number = f'{random.randint(0, 999999999):09}'
    return account_number


def calculate_check_digit(card_number_prefix):
    return


class Account:
    def __init__(self, account_number=None, pin=None, balance=0, persist=True):
        self.pin = pin
        self.account_number = account_number
        self.balance = balance
        if persist:
            self.save_to_db()

    @property
    def card_number(self):
        return derive_card_number(self.account_number)

    @classmethod
    def generate_new_account(cls) -> Self:
        return cls(account_number=generate_account_number(), pin=generate_pin())

    @classmethod
    def get_account_from_db(cls, card_number) -> Self:
        """
        Return the account data from the database. If the account is not found it will return None.

        :param card_number:
        :return: Account
        """
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute(SELECT_ACCOUNT_QUERY, (str(card_number),))
            res = cur.fetchone()
            if res:
                return cls(account_number=derive_account_number(res[1]), pin=res[2], balance=res[3], persist=False)
            else:
                return None

    def save_to_db(self):
        with contextlib.closing(conn.cursor()) as cur:
            if self.get_account_from_db(self.account_number):
                cur.execute(UPDATE_ACCOUNT_STATEMENT, (self.pin, self.balance, self.card_number))
            else:
                cur.execute(INSERT_ACCOUNT_STATEMENT, (self.card_number, self.pin))
            conn.commit()


def is_valid(card_number_input):
    return luhn.verify(card_number_input)


def login() -> Account:
    card_number_input = input('Enter your card number:')
    pin_input = input('Enter your PIN:')
    found_account = Account.get_account_from_db(card_number_input)
    if not is_valid(card_number_input) or not found_account or pin_input != found_account.pin:
        print('Wrong card number or PIN!')
        return None

    print('You have successfully logged in!')
    return found_account


def start():
    global conn
    conn = sqlite3.connect(DB_FILENAME)
    with contextlib.closing(conn.cursor()) as cur:
        cur.execute(CREATE_TABLE_STATEMENT)
        conn.commit()


    while True:
        print("""
1. Create an account
2. Log into account
0. Exit
""")
        user_input = input()
        if user_input == '1':
            account = Account.generate_new_account()
            print(f"""Your card has been created
Your card number:
{account.card_number}
Your card PIN:
{account.pin}
""")
        elif user_input == '2':
            account = login()
            while account:
                print("""1. Balance
2. Log out
0. Exit
""")
                user_input = input()
                if user_input == '1':
                    print(f'Balance: {account.balance}')
                elif user_input == '2':
                    print('You have successfully logged out!')
                    break
                elif user_input == '0':
                    return
                else:
                    print('Input not valid. Must be 1 (balance), 2 (log out) or 0 (exit)')
                    continue
        elif user_input == '0':
            return
        else:
            print('Input not valid. Must be 1 (create account), 2 (login) or 0 (exit)')
            continue


if __name__ == '__main__':
    start()
    print('Bye!')
