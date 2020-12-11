import random
import sqlite3


class User:

    def __init__(self, card_number=None, pin=None, balance=0):
        self.pin = pin
        self.card_number = card_number
        self.balance = balance

    def __str__(self):
        return f"Your card number:\n{self.card_number}\nYour card PIN:\n{self.pin:4}"


class Session:
    def __init__(self):
        self.user = None
        self.is_authorized = False
        self.db_connection = sqlite3.connect('card.s3db')
        self.cursor = self.db_connection.cursor()
        self.cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type = "table" AND name = "card"')
        if self.cursor.fetchone()[0] != 1:
            self.cursor.execute(
                'CREATE TABLE card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);'
            )
            self.db_connection.commit()

    def select_unauthorized(self):
        select = input("1. Create an account\n2. Log into account\n0. Exit\n")
        if select == "1":
            self.create_account()
        elif select == "2":
            self.authorize_user()
        elif select == "0":
            print("Bye!")
            exit()
        print()

    def select_authorized(self):
        select = input("1. Balance"
                       "\n2. Add income"
                       "\n3. Do transfer"
                       "\n4. Close account"
                       "\n5. Log out"
                       "\n0. Exit\n")
        if select == "1":  # Balance
            print("Balance: {}".format(self.user.balance))

        elif select == "2":  # Add income
            self.user.balance += int(input("Enter income:\n"))
            self.cursor.execute(
                "UPDATE card SET balance = ? WHERE number = ?",
                (self.user.balance, self.user.card_number))
            self.db_connection.commit()
            print("Income was added!")

        elif select == "3":  # Do transfer
            recipient_card_number = input("Transfer\nEnter card number:\n")
            if not self.is_number_valid(recipient_card_number):
                print("Probably you made a mistake in the card number. Please try again!")
            elif recipient_card_number == self.user.card_number:
                print("You can't transfer money to the same account!")
            else:
                self.cursor.execute(
                    "SELECT balance FROM card WHERE number = ?", (recipient_card_number,)
                )
                query_result = self.cursor.fetchone()
                if query_result is None:
                    print("Such a card does not exist.")
                else:
                    recipient_balance = query_result[0]
                    amount = int(input("Enter how much money you want to transfer:\n"))
                    if self.user.balance < amount:
                        print("Not enough money!")
                    else:
                        self.user.balance -= amount
                        recipient_balance += amount
                        self.cursor.execute(
                            "UPDATE card SET balance = ? WHERE number = ?",
                            (self.user.balance, self.user.card_number))
                        self.cursor.execute(
                            "UPDATE card SET balance = ? WHERE number = ?",
                            (recipient_balance, recipient_card_number))
                        self.db_connection.commit()

        elif select == "4":  # Close account
            self.cursor.execute(
                "DELETE FROM card WHERE number = ?",
                (self.user.card_number, )
            )
            self.db_connection.commit()
            self.user = None
            self.is_authorized = False
            print("The account has been closed!!")

        elif select == "5":  # Exit
            self.user = None
            self.is_authorized = False
            print("You have successfully logged out!")

        elif select == "0":
            print("Bye!")
            exit()
        print()

    def create_account(self):
        card_number = self.generate_card_number()
        pin = '%04d' % random.randint(0, 9999)
        new_user = User(card_number, pin)
        self.cursor.execute('INSERT INTO card (number, pin, balance) VALUES(?,?,?)',
                            (new_user.card_number, new_user.pin, new_user.balance))
        self.db_connection.commit()
        print("Your card has been created")
        print(new_user)

    def authorize_user(self):
        card_number = input("Enter your card number:\n")
        pin = input("Enter your PIN:\n")
        self.cursor.execute('SELECT balance FROM card WHERE number = ? AND pin = ?', (card_number, pin))
        balance = self.cursor.fetchone()
        if balance is not None:
            self.user = User(card_number, pin, balance[0])
            self.is_authorized = True
            print("You have successfully logged in!")
        else:
            print("Wrong card number or PIN!")

    def generate_card_number(self):
        initial_digits = "400000" + "%09d" % random.randint(0, 999999999)
        return initial_digits + self.lunh_checksum(initial_digits)

    def lunh_checksum(self, initial_digits):
        sum_of_digits = 0
        number = 1
        for i in initial_digits:
            digit = int(i)
            if number % 2 == 1:
                digit *= 2
            if digit > 9:
                digit -= 9
            sum_of_digits += digit
            number += 1
        return str(10 - sum_of_digits % 10)[-1]

    def is_number_valid(self, card_number):
        return self.lunh_checksum(card_number[0:-1]) == card_number[-1]


session = Session()
# print(session.lunh_checksum("400000844943340"))
while True:
    session.select_unauthorized()
    while session.is_authorized:
        session.select_authorized()
