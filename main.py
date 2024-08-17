import sys
from instagrapi import Client
from degrees import DegreesOfSeparation
from pathviewer import InstagramPathViewer
from utils.loginInfo import loginInfo

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

def startProgram():
    username, password = loginInfo()
    client.login(username, password)
    afterLogin()

startProgram()