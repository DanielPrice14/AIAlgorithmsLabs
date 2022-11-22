import sys, math, random, csv, time

#-----------------Intialisation-------------------------

cityLocations = [[0, 0, 0],[1, 20, 0],[2, 0, 42],[3, 42, 12]]    # Test list
route1 = [0,1,2,3,0]    # Test route
newCitys = [] # Variable used by the csv Reader to store the city locations

#Reads csv file into program
with open('cities15_13.csv', newline='') as csvfile:
    CReader = csv.reader(csvfile)
    #Skips the first two lines as they lack data
    next(CReader)
    next(CReader)
    #for each row adds them to the list newCitys with the correct data types
    for row in CReader:
        row[1] = float(row[1])
        row[2] = float(row[2])
        newCitys.append(row)

#-----------------End Of Intialisation-------------------------

#Function to get the cost of a given route
def getCostOfRoute(route, cityLocations):
    prevNode = -1
    curNode = -1
    distance = 0
    #Loops through all locations in a given route
    for i in range(len(route)):
        #If there is no previous node set it
        if prevNode == -1:
            prevNode = route[0]
        #Else find the distance between the current node and the previous node
        else:
            curNode = route[i]
            distance += math.sqrt((cityLocations[curNode][1] - cityLocations[prevNode][1])**2 + (cityLocations[curNode][2] - cityLocations[prevNode][2])**2)
            prevNode = curNode
    return distance

#Function to create a random route through a given list of locations
def generateRandomRoute(cityLocations):
    randomRoute = []
    startNode = -1
    numOfLocations = len(cityLocations)
    flag = False

    #Generate a random starting node, this node will be returned to at the end
    startNode = random.randint(0, numOfLocations-1)
    randomRoute.append(startNode)

    #While all locations have not been visited
    while len(randomRoute) < numOfLocations:
        flag = False
        node = random.randint(0, numOfLocations-1)
        #Loops through the currently visited nodes
        for i in range(len(randomRoute)):
            #If a node has already been visited sets a flag so it won't be added again
            if node == randomRoute[i]:
                flag = True
        #If a node doesn't exist in the route append it to the route
        if flag == False:
            randomRoute.append(node)

    randomRoute.append(startNode)
    return randomRoute

#Function that returns the list with the lowest cost after set time has passed
def generateRepeatedRandom(timeToTry):
    lowestCost = sys.maxsize   #BIG NUMBER
    lowestRoute = []
    startClockTime = time.monotonic()
    #Loops through the generation and comparison of new random routes until the specified amount of time has passed
    while startClockTime + timeToTry > time.monotonic():
        randomRoute = generateRandomRoute(newCitys)
        cost = getCostOfRoute(randomRoute, newCitys)
        #If new route is more efficent than the previous best route
        if cost < lowestCost:
            lowestCost = cost
            lowestRoute = randomRoute
            print(cost)
    print(lowestRoute)
    print("Lowest cost was: " + str(lowestCost))
    return lowestRoute

#Function to generate and return all possible 2OptSwaps for given route
def twoOptSwap(route):
    best = route
    swappedRoutes = []
    #Loops through the route checking whether a twooptswap can be performed
    for i in range(1, len(route) - 2):
        for j in range(i + 1, len(route)):
            if j - i == 1: continue  # changes nothing, skip then
            newRoute = route[:]
            newRoute[i:j] = route[j - 1:i - 1:-1]  # this is the 2woptSwap
            swappedRoutes.append(newRoute)
    return swappedRoutes

#Function that returns the shortest route out of the inputs given
def twoOptSwapCalc(routes, cityLocations):
    minCost = 100000
    shortestRoute = []
    #Checks the length of every route given
    for i in range(len(routes)):
        currentCost = getCostOfRoute(routes[i], cityLocations)
        #If the current route is better updates the shortest route to it
        if currentCost < minCost:
            minCost = currentCost
            shortestRoute = routes[i]
    return shortestRoute

#Function to perform optimisation for a set time and then print the shortest route it found
def repeatedOptimisation(timeToTry, cityLocations):
    lowestCost = sys.maxsize    #BIG NUMBER
    lowestRoute = []
    startClockTime = time.monotonic()
    #Loops through the optimaisation and comparison of new random routes until the specified amount of time has passed
    while startClockTime + timeToTry > time.monotonic():

        #Generates a random route to start from
        randomRoute = generateRandomRoute(cityLocations)
        currentMin = sys.maxsize    #BIG NUMBER
        currentCost = 0
        currentShortRoute = []
        flag = True

        while flag:    #While an improvement to the currentMinimum occurs
            flag = False
            localImprovements = twoOptSwap(randomRoute)    #Performs twoOptSwap
            shortRoute = twoOptSwapCalc(localImprovements, cityLocations)    #Finds the best of the generated routes
            currentCost = getCostOfRoute(shortRoute, cityLocations)    #Saves the cost of the best route
            if currentCost < currentMin:    #If the new route is better than the previous loops route
                currentMin = currentCost
                currentShortRoute = shortRoute
                flag = True    #Continues the while loop as an improvement was made

        if currentMin < lowestCost:    #If a new overall shortest route found then update accordingly
            lowestCost = currentMin
            lowestRoute = currentShortRoute
            print("New Lowest Cost: " + str(lowestCost))
            print(lowestRoute)
            print("\n")

    #Outputs the shortest route and its cost
    print("Lowest Cost at termination: " + str(lowestCost))
    print(lowestRoute)

class evolutionAlgorithm:

    #Size is how many members each generation will have
    def __init__(self, size, cityLocations):    # size must be an even number
        self.size = size
        self.oldGeneration = []
        self.newGeneration = []
        self.locations = cityLocations
        self.couples = []
        self.currentShortest = [[], 10000]
        self.shortest = [[], 10000]
        for i in range(self.size):
            newItem = []
            newItem.append(generateRandomRoute(self.locations))
            newItem.append(getCostOfRoute(newItem[0], self.locations))
            self.oldGeneration.append(newItem)
        self.routeLength = len(self.oldGeneration[0][0])
        print("RouteLength: " + str(self.routeLength))
        print(self.oldGeneration)

    def tournamentParentSelection(self):
        usedParents = []
        unusedParents = []
        self.couples = []
        for i in range(self.size):
            unusedParents.append(i)
        for i in range(int(self.size/2)):
            combat = []
            randomIndex = random.randint(0, len(unusedParents) - 1)
            parent1 = unusedParents.pop(randomIndex)
            randomIndex = random.randint(0, len(unusedParents) - 1)
            parent2 = unusedParents.pop(randomIndex)
            if self.locations[parent1][1] > self.locations[parent2][1]:    #If parent1 is better take it otherwise...
                usedParents.append(parent1)
            else:    #... use parent2 even if two arents are equal
                usedParents.append(parent2)
        for i in range(int(len(usedParents)/2)):      #Add this back in to get multiple sets of parents
            self.couples.append([usedParents.pop(0),usedParents.pop(0)])

    def rouletteParentSelection(self, desiredParents):
        self.couples = []
        if desiredParents%2 == 1:
            desiredParents -= 1
            print("Desired Parents set to: " + str(desiredParents))
        odds = []
        costs = []
        for i in range(self.size):
            costs.append(self.oldGeneration[i][1])
        for j in range(self.size):
            minimum = 0
            for i in range(self.size):
                if costs[minimum] > costs[i]:
                    minimum = i
            for i in range(len(self.oldGeneration)-j):
                costs[minimum] = 10000
                odds.append(minimum)
        usedItems = []
        for j in range(int(desiredParents/2)):
            couple = []
            for i in range(2):
                flag = True
                while flag:
                    flag = False
                    randomIndex = random.randint(0, len(odds)-1)
                    value = odds[randomIndex]
                    for x in range(len(usedItems)):
                        if value == usedItems[x]:
                            flag = True

                usedItems.append(value)
                couple.append(value)
            self.couples.append(couple)

    def survivorSelection(self):    #Simply overwrites old generation with newGeneration
        self.oldGeneration = self.newGeneration
        self.newGeneration = []

    def mutation(self):
        while True:
            for i in range(len(self.couples)):    #Every couple has one parent create a mutation
                randomIndex = random.randint(0, 1)
                mutations = twoOptSwap(self.oldGeneration[self.couples[i][randomIndex]][0])
                randomIndex = random.randint(0, len(mutations)-1)
                self.newGeneration.append([mutations[randomIndex],getCostOfRoute(mutations[randomIndex], self.locations)])
                if len(self.oldGeneration) == len(self.newGeneration):
                    break
            if len(self.oldGeneration) == len(self.newGeneration):
                break

    def crossOver(self):
        for j in range(len(self.couples)):    #For every couple
            for z in range(2):
                if z == 0:
                    parent1 = self.oldGeneration[self.couples[j][0]][0]
                    parent2 = self.oldGeneration[self.couples[j][1]][0]
                else:
                    parent1 = self.oldGeneration[self.couples[j][1]][0]
                    parent2 = self.oldGeneration[self.couples[j][0]][0]
                childList = []
                i = int(self.routeLength/2)
                for x in range(int(self.routeLength/2)):    #Appends the first half of parent1 to the child
                    childList.append(parent1[x])
                while len(childList) < self.routeLength:    #While the list doesn't contain all the values
                    if i >= self.routeLength - 1:
                        i = 0
                    else:
                        i += 1
                    flag = False
                    for l in range(len(childList)):
                        if childList[l] == parent2[i]:
                            flag = True
                    if flag == False:
                        childList.append(parent2[i])
                    if len(childList) == self.routeLength - 1:
                        childList.append(childList[0])
                self.newGeneration.append([childList,getCostOfRoute(childList,self.locations)])

    def findMinimum(self):
        for i in range(len(self.oldGeneration)):
            if self.oldGeneration[i][1] < self.currentShortest[1]:
                self.currentShortest = self.oldGeneration[i]
        if self.currentShortest[1] < self.shortest[1]:
            self.shortest = self.currentShortest
            print("New Minimum: ")
            print(self.shortest)
            print("\n")


    def evolutionLoop(self, timeToTry):
        startClockTime = time.monotonic()
        while startClockTime + timeToTry > time.monotonic():  # While there is still time left
            self.rouletteParentSelection(8)
            self.crossOver()
            self.mutation()
            self.survivorSelection()
            self.findMinimum()



#-----------------1-----------------
#print(getCostOfRoute([3,0,2,1,4,5,6,7,8,9,10,11,12,3],newCitys))
#-----------------2-----------------
#generateRepeatedRandom(10)
#-----------------3-----------------
#repeatedOptimisation(10, newCitys)
#-----------------4-----------------
pop = evolutionAlgorithm(20, newCitys)
pop.evolutionLoop(10)