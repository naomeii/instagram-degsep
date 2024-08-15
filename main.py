import time
from instagrapi import Client
from collections import deque

client = Client()

pathOfFollowersToPerson = {}

def convertPathUserIDtoUsername(path):
    return [client.username_from_user_id(userID) for userID in path]

def tracePath(targetPersonID, pathOfFollowersToPerson):
    path = []
    current_node = targetPersonID
    while current_node is not None:
        path.insert(0, current_node)
        if pathOfFollowersToPerson[current_node] is None:
            break
        current_node = pathOfFollowersToPerson[current_node]
    return path


def degrees_of_separation(sourcePerson, targetPerson):
    if sourcePerson == targetPerson:
        return 0, [sourcePersonID]
    
    # convert username to id
    sourcePersonID = client.user_id_from_username(sourcePerson)
    targetPersonID = client.user_id_from_username(targetPerson)

    # perform BFS
    queue = deque([(sourcePersonID, 0)]) # start with (sourceID, currentLayer)
    visited = set()
    pathOfFollowersToPerson[sourcePersonID] = None

    while queue:
        currentUserID, currentLayer = queue.popleft()

        if currentUserID in visited:
            continue

        visited.add(currentUserID)
        userInfo = client.user_info(currentUserID).dict()
        # skip priv accts/ accts following no one
        if userInfo['is_private'] or userInfo['following_count'] == 0:
            continue

        # get following list of curr user
        followingInfo = client.user_following(currentUserID, 0)
        
        for personID in followingInfo:
            if personID not in visited:
                # update the path map before adding the user to the queue
                pathOfFollowersToPerson[personID] = currentUserID
                queue.append((personID, currentLayer + 1))

                if personID == targetPersonID:
                    # path trace, then convert IDs to actual usernames
                    path = tracePath(targetPersonID, pathOfFollowersToPerson)
                    path_usernames = convertPathUserIDtoUsername(path)
                    return currentLayer + 1, path_usernames
        
    return -1, []

def pathFormatter(path):
    # join the strings with '->'
    return '->'.join(path)

def computeResults(sourceUser, targetUser):
    print(f'Computing the degrees of separation between {sourceUser} and {targetUser}...')
    result, path = degrees_of_separation(sourceUser, targetUser)

    if result == 0:
        print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are the same person!")
        return
    if result == 1:
        print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are directly following each other.")
        print(pathFormatter(path))
        return
    if result == -1:
        print(f"The separation between {sourceUser} and {targetUser} is: {result}")
        print(f"I was unable to find any connection of followers between these users.")
        return
    else:
        print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are {result} followings apart.")
        print(pathFormatter(path))
        return

def afterLogin():
    sourceUser = input('Enter the starting person\'s username: ')
    targetUser = input('Enter the target person\'s username: ')

    print('Thanks! Please wait while I compute the degrees of separation for you :)')

    computeResults(sourceUser, targetUser)

    restartQuestion = input("Would you like to compute another connection? (yes/no): ").strip().lower()
    if (restartQuestion == 'yes'):
        afterLogin()
    else:
        print('Goodbye!')
        return

def startProgram():
    print('Welcome to viewing Degrees of Separation between users on Instagram.')
    time.sleep(1)
    print('Note that you will need to be logged in for the program to work.')
    
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    client.login(username, password)

    afterLogin()

startProgram()