# Write your code here
import random
from typing import Dict
from typing_extensions import Self

IIN = '400000'


def generate_pin():
    return f'{random.randint(0, 9999):04}'


def generate_account_number():
    account_number = random.randint(0, 999999999)
    while account_exists(account_number):
        account_number = random.randint(0, 999999999)
    return f'{account_number:09}'


def account_exists(account_number) -> bool:
    return account_number in Account.all_accounts


def calculate_checksum(card_number_prefix):
    return 4


class Account:
    # account_number -> account
    all_accounts: Dict[str, Self] = dict()

    balance = 0

    def __init__(self):
        self.pin = generate_pin()
        self.account_number = generate_account_number()
        Account.all_accounts[self.account_number] = self

    @property
    def card_number(self):
        card_number_prefix = f'{IIN}{self.account_number}'
        checksum = calculate_checksum(card_number_prefix)
        return f'{card_number_prefix}{checksum}'

    def __eq__(self, other):
        return isinstance(other, Account) and self.account_number == other.account_number

    def __hash__(self):
        return hash(self.account_number)


def create_account() -> Account:
    return Account()


def is_valid(card_number_input):
    # todo implement card number validation
    return True


def login() -> Account:
    card_number_input = input('Enter your card number:')
    pin_input = input('Enter your PIN:')
    account_number_input = card_number_input[6:15]
    found_account = Account.all_accounts.get(account_number_input, False)
    if not is_valid(card_number_input) or not found_account or pin_input != found_account.pin:
        print('Wrong card number or PIN!')
        return None

    print('You have successfully logged in!')

    return found_account


def start():
    while True:
        print("""
1. Create an account
2. Log into account
0. Exit
""")
        user_input = input()
        if user_input == '1':
            account = create_account()
            print(f"""Your card has been created
Your card number:
{account.card_number}
Your card PIN:
{account.pin}
""")
        elif user_input == '2':
            account_found = login()
            while account_found:
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
