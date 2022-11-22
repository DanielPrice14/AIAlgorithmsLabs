import math, sys, random, time

class AntennaArray:
    def __init__(self, AntennaAmount, SteeringAngle):
        self.antennaAmount = AntennaAmount    # The number of antenna on the array, no cap currently
        self.steeringAngle = SteeringAngle    # The angle of the beam, 0-359
        self.MIN_SPACING = 0.25

    def bounds(self):
        bnds = []
        for i in range(self.antennaAmount):
            bnds.append([0.0, float(self.antennaAmount)/2.0])
        return bnds

    #design must be a list of length antennaAmount
    def is_valid(self, design):
        if len(design) != self.antennaAmount: return False

        #for i in range(len(design)-1):
        #    if design[i] > design[i+1]:
        #        tempValue = design[i]
        #        design[i] = design[i+1]
        #        design[i+1] = tempValue
        design = sorted(design)

        #Checks the aperture size (final placement) is exactly half the number of antenna
        if ((abs(design[len(design)-1] - float(self.antennaAmount)/2.0)) != 0):
            #print("Aperture Size incorrect")
            return False

        #All antennae lie within the problem bounds
        for i in range(len(design)-1):
            if design[i] < self.bounds()[i][0] or design[i] > self.bounds()[i][1]:
                #print("Antennae lies outside valid bounds")
                return False

        #All antennae are separated by at least MIN_SPACING
        for i in range(len(design)-1):
            if design[i+1] - design[i] < self.MIN_SPACING:
                #print("Antennae not seperated by valid spacing")
                return False

        return True

    def evaluate(self, design):
        class PowerPeak:
            def __init__(self, e, p):
                self.elevation = e
                self.power = p
        peaks = []
        prev = PowerPeak(0.0, sys.float_info.min)
        current = PowerPeak(0.0, self.arrayFactor(design,0.0))
        elevation = 0.01
        while elevation <= 180.0:
            next = PowerPeak(elevation, self.arrayFactor(design, elevation))
            if current.power >= prev.power and current.power >= next.power:
                peaks.append(current)
            prev = current
            current = next
            elevation += 0.01
        peaks.append(PowerPeak(180.0, self.arrayFactor(design, 180.0)))
        peaks.sort(key=lambda x: x.power, reverse = True)

        #Code always takes second biggest power peak. Seems correct though
        #Checking
        #print("Sorted power peaks: ")
        #for i in range(len(peaks)):
        #    print(peaks[i].power)
        #print("End of sorted power peaks")
        #Checking
        if len(peaks) < 2: return sys.float_info.min
        distance_from_steering = abs(peaks[0].elevation - self.steeringAngle)
        for i in range(len(peaks)):
            if abs(peaks[i].elevation - self.steeringAngle) < distance_from_steering:
                return peaks[0].power
        return peaks[1].power

    def arrayFactor(self, design, elevation):
        steering = 2.0*math.pi*(self.steeringAngle/360.0)
        elevation = 2.0*math.pi*(elevation/360.0)
        sum = 0.0
        for item in design:
            sum += math.cos(2 * math.pi * item * (math.cos(elevation) - math.cos(steering)));
        return 20*math.log(abs(sum))

#Class to hold a population of particles
class ParticlePopulation:

    #Intialises the population
    def __init__(self, numberOfParticles, antennaAmount, steeringAngle):
        self.particles = []
        self.numberOfParticles = numberOfParticles
        self.globalBestPosition = []
        self.globalBestPositionEvaluated = 100000
        print("All Particles in intilaisation................................")
        #intilaises the particles in the population
        for i in range(numberOfParticles):
            newParticle = ArrayParticle(antennaAmount, steeringAngle, self)
            self.particles.append(newParticle)
            print(self.particles[i].position)
        print("End of particles list....................................................")

    #Function to loop particles until time is up
    def loop(self, timeToTry):
        startClockTime = time.monotonic()
        numberOfLoops = 1
        #While the specified amount of time has not yet passed
        while startClockTime + timeToTry > time.monotonic():
            print("__________________________________________________________________________________")
            print("Beginning of loop: " + str(numberOfLoops))

            #Main function loop for each generation
            self.updateGlobalBest()
            for i in range(len(self.particles)):
                self.particles[i].updateVelocity()
                self.particles[i].updatePosition()
                self.particles[i].evaluateCurrentPosition()
                self.particles[i].checkBestPosition()
            numberOfLoops += 1

        print("loop function has finished\n Lowest peak power achieved was: " + str(self.globalBestPositionEvaluated))
        print(self.globalBestPosition)
        print("List of particle positions: ")
        for i in range(len(self.particles)):
            print(self.particles[i].position)

    #Function to update the global best value found
    def updateGlobalBest(self):
        for i in range(self.numberOfParticles):
            #If a particles position is valid
            if (self.particles[i].validty == True):
                #If the particle has a better position than the current global best
                if self.particles[i].bestPositionEvaluated < self.globalBestPositionEvaluated:
                    #Update the global best
                    self.globalBestPosition = self.particles[i].bestPosition
                    self.globalBestPositionEvaluated = self.particles[i].bestPositionEvaluated
                    print("Global Best updated to: " + str(self.globalBestPositionEvaluated))
                    print(self.globalBestPosition)


class ArrayParticle:

    #Intialises a particle
    def __init__(self, antennaAmount, steeringAngle, population):
        self.array = AntennaArray(antennaAmount, steeringAngle)
        self.position = sorted(generateArray(self.array, antennaAmount))
        self.bestPosition = []
        self.bestPositionEvaluated = 100000
        self.inertia = []    #The previous velocity
        self.impacts = [0.5,1.5,2.0]    #How each attraction is weighed, first for intertia, second for pb and third for gb
        self.population = population
        self.velocity = []
        self.validty = True

        for i in range(len(self.position)-1):    #Intialises inertia and velocity to be the correct size
            self.velocity.append(0.0)
            self.inertia.append(0.0)

        #intialising velocity and best position
        tempPosition = sorted(generateArray(self.array, antennaAmount))
        self.bestPosition = tempPosition
        self.bestPositionEvaluated = self.array.evaluate(self.bestPosition)
        for i in range(len(self.position)-1):
            self.inertia[i] = (self.position[i] - tempPosition[i])/2.0

    #Function to evaluate the current position
    def evaluateCurrentPosition(self):
        return self.array.evaluate(self.position)

    #Function to check if the current position is the best position
    def checkBestPosition(self):
        if (self.validty == True):
            #print("Checking best position")
            if self.array.evaluate(self.position) < self.bestPositionEvaluated:
                self.bestPositionEvaluated = self.array.evaluate(self.position)
                self.bestPosition = []
                for i in range(len(self.position)):
                    self.bestPosition.append(self.position[i])
                #print("New pb found")

    #Function to update the velocity of a particle
    def updateVelocity(self):
        self.velocity = []
        factor1 = random.uniform(0.0, 1.0)
        factor2 = random.uniform(0.0, 1.0)
        #For each array position, excluding the final position, generate a new velocity
        for i in range(len(self.position)-1):
            self.velocity.append( (self.impacts[0] * self.inertia[i])
            + (self.impacts[1] * factor1 * (self.bestPosition[i] - self.position[i]))
            + (self.impacts[2] * factor2 * (self.population.globalBestPosition[i] - self.position[i])))

    #Currently discards the new position if it falls outside the constraits
    #Implementing correction for the particle would be good
    def updatePositionOld(self):
        tempPosition = []
        for i in range(len(self.position)):
            tempPosition.append(self.position[i])
        for i in range((len(tempPosition))-2):
            tempPosition[i] = tempPosition[i] + self.velocity[i]
        if (self.array.is_valid(tempPosition)):
            print("Valid new position found")
            self.validty = True
        else:
            #print("Calculated route wasn't within constaints")
            self.validty = False
            #print(tempPosition)
        #print(tempPosition)
        #print(self.position)
        print(tempPosition[4])
        for i in range(len(self.position)):
            self.position[i] = tempPosition[i]
        #Updates the inertia as the move has taken place
        for i in range(len(self.velocity)):
            self.inertia[i] = self.velocity[i]
        #print(self.position[] - tempPosition)

    #Unused due to malfunctions
    def updatePositionOldNew(self):
        for i in range(len(self.position)-1):
            self.position[i] += self.velocity[i]
            if self.array.is_valid(self.position):
                self.validty = True
                print("Valid new position found")
            else:
                self.validty = False

        for i in range(len(self.velocity)):
            self.inertia[i] = self.velocity[i]

    #Function to update the position of a particle
    def updatePosition(self):
        tempPosition = []
        #Creates a temporary variable to store the new position
        for i in range(len(self.position)):
            tempPosition.append(self.position[i])
        #Adds the velocity to the temporary variable
        for i in range(len(self.position) - 1):
            tempPosition[i] += (self.velocity[i])
        #Prevents issue with values becoming negative
        if tempPosition[i] < 0:
            tempPosition[i] = 0
        #If the temporary variable holds a valid position, update the actual position
        if self.array.is_valid(tempPosition):
            self.position = tempPosition
            self.validty = True
        else:
            self.validty = False

        #Replaces the inertia value with the current velocity ready for the next function call
        for i in range(len(self.velocity)):
            self.inertia[i] = self.velocity[i]


def generateArray(newArray, antennaAmount):
    bounds = newArray.bounds()
    potencialDesign = []
    while not(newArray.is_valid(potencialDesign)):
        potencialDesign = []
        for i in range(antennaAmount-1):
            position = random.uniform(bounds[i][0], bounds[i][1])
            potencialDesign.append(position)
        potencialDesign.append(antennaAmount/2)
    return potencialDesign

def generateRandomArrays(antennaAmount, steeringAngle, timeToTry):
    newArray = AntennaArray(antennaAmount, steeringAngle)
    lowestPeakPower = 10000000000000  # BIG NUMBER
    lowestDesign = []
    startClockTime = time.monotonic()
    while startClockTime + timeToTry > time.monotonic():
        randomArray = generateArray(newArray, antennaAmount)
        peakPower = newArray.evaluate(randomArray)
        if peakPower < lowestPeakPower:
            lowestPeakPower = peakPower
            lowestDesign = randomArray
            print(peakPower)
    print("Best array design was: ")
    print(lowestDesign)
    print("Lowest peak power was: " + str(lowestPeakPower))
    return lowestDesign


#generateRandomArrays(9, 90, 5)
temp = ParticlePopulation(10, 15, 90)
temp.loop(20)

#----------------------5-----------------------
#pop = ParticlePopulation(10, numberOfAntennaToBeProvided, angleOfAntennaToBeProvided)
#pop.loop(15)
#----------------------------------------------


#For some reason code breaks when an antennaAmount greater than single digits is used
