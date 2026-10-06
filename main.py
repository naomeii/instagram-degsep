import os
import sys
from instagrapi import Client
from instagrapi.exceptions import ClientError, UnknownError
from degrees import DegreesOfSeparation
from pathviewer import InstagramPathViewer
from utils.loginInfo import loginInfo

SESSION_FILE = "session.json"

client = Client()
# adds a random delay between 1 and 3 seconds after each request
client.delay_range = [1, 3]

def afterLogin():

    sourceUser = input('Enter the starting person\'s username: ')
    targetUser = input('Enter the target person\'s username: ')
    print('Thanks! Please wait while I compute the degrees of separation for you :)')
    
    # compute results
    calculateSeparation = DegreesOfSeparation(client, sourceUser, targetUser)
    print(f'Computing the degrees of separation between {sourceUser} and {targetUser}...')
    result, path = calculateSeparation.computeDegreesOfSeparation()

    # display results
    DegreesOfSeparation.displayResults(sourceUser, targetUser, result, path)

    askToSeePath = input("Would you like to see the path taken in real time? (yes/no): ").strip().lower()
    if (askToSeePath == 'yes'):
        viewer = InstagramPathViewer(path)
        viewer.showPath()
    restartQuestion = input("Would you like to compute another connection? (yes/no): ").strip().lower()
    if (restartQuestion == 'yes'):
        afterLogin()
    else:
        print('Goodbye!')
        sys.exit(0)

def loginWithSession(username, password):
    """Reuse a saved session when possible to avoid Instagram's login rate limits."""
    if os.path.exists(SESSION_FILE):
        try:
            client.load_settings(SESSION_FILE)
            client.login(username, password)
            client.dump_settings(SESSION_FILE)
            print("Logged in using saved session.")
            return
        except Exception as e:
            print(f"Saved session could not be reused ({e}). Trying a fresh login...")

    try:
        client.login(username, password)
        client.dump_settings(SESSION_FILE)
        print("Logged in successfully.")
    except (UnknownError, ClientError) as e:
        message = str(e)
        if "out of date" in message.lower() or "needs_upgrade" in message.lower():
            print(
                "Instagram rejected the API login (often after too many login attempts).\n"
                "Wait a few minutes, then try again. Once a session.json file is saved, "
                "later runs should reuse it instead of logging in every time."
            )
        raise

def startProgram():
    username, password = loginInfo()
    loginWithSession(username, password)
    afterLogin()

startProgram()