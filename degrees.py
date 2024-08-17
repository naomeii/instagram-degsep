from collections import deque
from instagrapi import Client

class DegreesOfSeparation:
    def __init__(self, client: Client, sourceUser: str, targetUser: str):
        self.client = client
        self.sourceUser = sourceUser
        self.targetUser = targetUser
        self.pathFollowerToPerson = {}

    def convertPathUserIDtoUsername(self, path):
        return [self.client.username_from_user_id(userID) for userID in path]

    def tracePath(self, targetPersonID):
        path = []
        currentPerson = targetPersonID
        while currentPerson is not None:
            path.insert(0, currentPerson)
            if self.pathFollowerToPerson[currentPerson] is None:
                break
            currentPerson = self.pathFollowerToPerson[currentPerson]
        return path

    def computeDegreesOfSeparation(self):
        if self.sourceUser == self.targetUser:
            sourceUserID = self.client.user_id_from_username(self.sourceUser)
            return 0, [sourceUserID]

        # convert username to id
        sourceUserID = self.client.user_id_from_username(self.sourceUser)
        targetPersonID = self.client.user_id_from_username(self.targetUser)

        # BFS
        queue = deque([(sourceUserID, 0)])
        visited = set()
        self.pathFollowerToPerson[sourceUserID] = None

        while queue:
            currentUserID, currentLayer = queue.popleft()

            if currentUserID in visited:
                continue

            visited.add(currentUserID)
            userInfo = self.client.user_info(currentUserID).dict()
            # skip private accounts or accounts following no one
            if userInfo['is_private'] or userInfo['following_count'] == 0:
                continue

            # get following list of current user
            followingInfo = self.client.user_following(currentUserID, 0)
            
            for personID in followingInfo:
                if personID not in visited and personID != sourceUserID: # make sure we don't unecessarily loop back to beginning followers
                    # update the path map before adding the user to the queue
                    self.pathFollowerToPerson[personID] = currentUserID
                    queue.append((personID, currentLayer + 1))

                    if personID == targetPersonID:
                        # trace path, then convert IDs to actual usernames
                        path = self.tracePath(targetPersonID)
                        pathOfUsernames = self.convertPathUserIDtoUsername(path)
                        return currentLayer + 1, pathOfUsernames
        
        return -1, []

    @staticmethod
    def pathFormatter(path):
        return '->'.join(path)

    @staticmethod
    def displayResults(sourceUser, targetUser, result, path):
        if result == 0:
            print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are the same person!")
        elif result == 1:
            print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are directly following each other.")
            print(DegreesOfSeparation.pathFormatter(path))
        elif result == -1:
            print(f"The separation between {sourceUser} and {targetUser} is: {result}")
            print(f"I was unable to find any connection of followers between these users.")
        else:
            print(f"The separation between {sourceUser} and {targetUser} is: {result} ! They are {result} followings apart.")
            print(DegreesOfSeparation.pathFormatter(path))
