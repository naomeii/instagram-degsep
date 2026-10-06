import os

def saveLogin(username, password):
    with open('loginInfo.txt', 'w') as file:
        file.write(f"{username}\n{password}")


def loadSavedLogin():
    if not os.path.exists('loginInfo.txt'):
        return None

    with open('loginInfo.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def loginInfo():
    print('Welcome to viewing Degrees of Separation between users on Instagram.')
    print('Note that you will need to be logged in for the program to work.')

    saved = loadSavedLogin()
    if saved:
        reuse = input(f"Use saved login for '{saved[0]}'? (yes/no): ").strip().lower()
        if reuse == 'yes':
            print("Logging you in...")
            return saved

    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    print("Logging you in...")
    saveLogin(username, password)
    return username, password
