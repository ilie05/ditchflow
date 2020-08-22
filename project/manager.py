import getpass
from sys import argv
from werkzeug.security import generate_password_hash, check_password_hash
from database import cursor, conn
from utils import check_email


def change_password(email):
    user = cursor.execute(f'SELECT * FROM USER WHERE EMAIL="{email}";').fetchone()
    if not user:
        print(f"***The user with '{email}' email address does not exist***")
        return

    user_old_pass = user[2]
    old_pass_valid = False
    while True:
        if not old_pass_valid:
            old_password = getpass.getpass(prompt="Old password: ")
            if not check_password_hash(user_old_pass, old_password):
                print("***Invalid old password***")
                continue
            else:
                old_pass_valid = True

        new_password = getpass.getpass(prompt='New password:')
        if len(new_password) < 6:
            print("***Password must have min 6 characters***")
            continue

        confirm_new_pass = getpass.getpass(prompt="Confirm new password: ")
        if new_password != confirm_new_pass:
            print("***Passwords do not match***")
            continue

        cursor.execute(f"UPDATE USER SET password='{generate_password_hash(new_password)}' WHERE email='{email}';")
        conn.commit()
        print("Password has been changed successfully!***")
        break


def create_user():
    email_valid = False
    while True:
        if not email_valid:
            email = input("Email: ")
            email_valid = check_email(email)
            if not email_valid:
                print("***Invalid email address***")
                continue

            user = cursor.execute(f'SELECT * FROM USER WHERE EMAIL="{email}";').fetchone()
            if user:
                print("***Email address already exists***")
                email_valid = False
                continue
            email_valid = True

        password = getpass.getpass()
        if len(password) < 6:
            print("***Password must have min 6 characters***")
            continue
        confirm_pass = getpass.getpass(prompt="Confirm password: ")

        if password != confirm_pass:
            print("***Passwords do not match***")
            continue

        cursor.execute(
            f"Insert Into USER ('EMAIL','PASSWORD') Values ('{email}', '{generate_password_hash(password)}');")
        conn.commit()
        print("User has been created successfully!***")
        break


class HELP:
    CREATE_USER = '--create-user'
    CHANGE_USER_PASSWORD = '--change-password'
    CHANGE_USER_PASSWORD_ARG = 'user-email-address'

    def __str__(self):
        return f'{self.CREATE_USER}\t\t\t\t\tCreate a new user\n{self.CHANGE_USER_PASSWORD} ' + \
               f'"{self.CHANGE_USER_PASSWORD_ARG}"\t\tChange user password'


if __name__ == '__main__':
    helper = HELP()
    ERROR_MESSAGE = 'Invalid arguments!'

    if len(argv) < 2:
        print(ERROR_MESSAGE)
        exit(1)

    arg1 = argv[1]
    if arg1 == helper.CREATE_USER:
        create_user()
    elif arg1 == helper.CHANGE_USER_PASSWORD:
        if len(argv) < 3:
            print(ERROR_MESSAGE)
            exit(1)
        email = argv[2]
        change_password(email)
    elif arg1 == '-h' or arg1 == '--help':
        print(helper)
    else:
        print(ERROR_MESSAGE)
