#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# File: trabalho2.py
# Created Date: Friday January 3rd 2020
# Author: Debora Antunes
# -----
# Last Modified: Saturday, January 4th 2020, 8:10:26 pm
# -----
'''
import random, operator, math, sys

class Algorithm:

    def __init__(self, path, popSize=20, eliteSize=10, generations=100, probCross=0.5, probMut=0.1, forceMut=False):
        self.coord=self.readDataset(path) #Tuple list with each city's coordinates
        self.popSize=popSize  #Desired population size
        self.size=len(self.coord)  #Number of cities
        self.eliteSize=eliteSize    #Desired number of best fitted route
        self.generations=generations  #Number of generations
        self.probCross=probCross    #Crossing Over's Probability
        self.probMut=probMut    #Mutation probability
        self.forceMut=forceMut  #Force the algorithm to produce a successful mutation

        self.geneticAlgorithm()

    def readDataset(self, path):
        '''
        Function for loading the data file
        :param path: Path to file
        :return: Tuples list with different city's coordinates
        '''
        data=open(path,'r')
        coord=[]
        for i in data:
            l=i.split(' ')
            try:
                coord.append((float(l[1]),float(l[2])))
            except:
                pass
        return coord

    def fitnessPop(self, population):
        '''
        Test for the population's fitness
        :param population: A set of routes
        :return: A list of routes
        '''
        popFitness={}
        for k in range(len(population)):
            popFitness[k]=self.fitnessRoute(population[k])
            inds=sorted(popFitness.items(), key = operator.itemgetter(1))
        return inds

    def fitnessRoute(self, route):
        '''
        Calculates the fitness of a route
        :param route: List of cities
        :return: Route length
        '''
        pathfitness = 0
        for i in range(len(route)-1):
            ind1=route[i]
            ind2=route[i+1]
            pathfitness+=self.distance(ind1,ind2)
        pathfitness+=self.distance(route[0],route[len(route)-1])
        return pathfitness

    def distance(self,ind1,ind2):
        '''
        Calculates the distance
        :param ind1: From this city
        :param ind2: To this city
        :return: Euclidean distance between the two cities
        '''
        x1=self.coord[ind1][0]
        x2=self.coord[ind2][0]
        y1=self.coord[ind1][1]
        y2=self.coord[ind2][1]
        return (math.sqrt(((abs(x1-x2))**2)+((abs(y1-y2))**2)))

    def createRandomRoute(self,popSize):
        '''
        Uses all of the cities to generate a random route
        :param popSize: Number of routes
        :return: List of routes
        '''
        popInitial=[]
        k=popSize
        while k!=0:
            res = random.sample(range(self.size), self.size)
            popInitial.append(res)
            k-=1
        return popInitial 
    
    def createGreedyRoute(self, popSize):
        '''
        Starts by selecting one city. Calculates all lengths from this city to others and creates
        a route based on these lengths
        :param popSize: Number of routes
        :return: List of routes
        '''
        popInitial=[]
        k=popSize
        while k!=0:
            ind=[]
            dic={}
            pick=random.randint(0, self.size-1)
            ind.append(pick)
            for i in range(self.size):
                dic[i]=self.distance(pick, i)
            inds=sorted(dic.items(), key = operator.itemgetter(1)) 
            for j in range(1,self.size):
                ind.append(inds[j][0])
            popInitial.append(ind)
            k-=1
        return popInitial

    def orderSelection(self, pop):
        '''
        Selects the first 'parents' based on the best fitness
        :param pop: List of Routes
        :return: List of elite routes
        '''
        selection=[]
        for i in range(self.eliteSize):
            selection.append(pop[i][0])
        return selection

    def rouletteWheelSelection(self, selection, pop): #Wasn't used for it worsened our final results
        '''
        Selects a population based on a probability. Best fitted 'parents' have a higher chance of being selected
        :param selection: List of previously selected parents
        :param pop: List of Routes
        :return: The complete list of Parents
        '''
        cumsum=0
        CumSum=[]
        CumPerc=[]

        for i in range(self.popSize):
            cumsum+=pop[i][1]
            CumSum.append(cumsum)
        for i in range(self.popSize):
            cumperc=((CumSum[i]/CumSum[self.popSize-1])*100)
            CumPerc.append(cumperc)
        for i in range(self.eliteSize,self.popSize):
            pick=random.randint(1,100)
            for j in range(self.popSize):
                if pick <= CumPerc[j]:
                    selection.append(pop[j][0])
                    break
        return selection

    def tournamentSelection(self, selection, pop):
        '''
        Selects a population based on a fitness comparison. Best fitted 'parents' have a higher chance of being selected
        :param selection: List of previously selected parents
        :param pop: List of Routes
        :return: The complete list of Parents
        '''
        i=0
        while i<(self.popSize-self.eliteSize):
            p1=random.randint(0, self.popSize-1)
            p2=random.randint(0, self.popSize-1)
            if pop[p1][1]==pop[p2][1]:
                continue  
            elif pop[p1][1] < pop[p2][1]:
                selection.append(pop[p1][0])
                i+=1
            elif pop[p1][1] > pop[p2][1]:
                selection.append(pop[p2][0])
                i+=1
        return selection  

    def matingPool(self, pop, selection):
        '''
        Uses the index provided by the selection to filter the population
        :param pop: List of Routes
        :param selection: List of chosen 'parents'
        :return: List with the chosen parent's routes
        '''
        matingpool = []
        for i in range(self.popSize):
            j = selection[i]
            matingpool.append(pop[j])
        return matingpool
    
    def crossover(self, ind1, ind2):
        '''
        Selects a crossover type, under a given probability.
        :param ind1: First route
        :param ind2: Second route
        :return: Two 'child' routes
        '''
        if random.random()<=self.probCross:
            if random.random()<=0.5:
                cross=self.onePointCrossover(ind1,ind2) 
            else:
                cross=self.twoPointCrossover(ind1,ind2)
            return cross
        else: 
            return ind1, ind2

    def onePointCrossover(self, ind1, ind2):
        '''
        Combines the information between two 'parent' routes based on only one breaking point
        :param ind1: First route
        :param ind2: Second route
        :return: Two 'child' routes
        '''
        stop = int(random.random() * self.size)
        p1i=ind1[:stop]
        p1f=ind1[stop:]
        p2i=[]
        p2f=[]
        for i in ind2:
            if i in p1i:
                p2i.append(i)
            else:
                p2f.append(i)
        p1i.extend(p2f)
        p2i.extend(p1f)
        return p1i,p2i

    def twoPointCrossover(self, ind1, ind2):
        '''
        Combines the information between two 'parent' routes based on two breaking points
        :param ind1: First route
        :param ind2: Second route
        :return: Two 'child' routes
        '''
        s1 = int(random.random() * self.size)
        s2 = int(random.random() * self.size)
        stop1=min(s1,s2)
        stop2=max(s1,s2)
        p1i=ind1[:stop1]
        p1m=ind1[stop1:stop2]
        p1f=ind1[stop2:]
        p2i=[]
        p2m=[]
        p2f=[]
        for i in ind2:
            if i in p1m:
                p2m.append(i)
            elif len(p2i)==len(p1i):
                p2f.append(i)
            else:
                p2i.append(i)
        p1i.extend(p2m)
        p1i.extend(p1f)
        p2i.extend(p1m)
        p2i.extend(p2f)
        return p1i,p2i

    def uniformCrossover(self, ind1, ind2): #Not used in the final algorithm - It worsened the overall distance
        '''
        Combines the information between two 'parent' routes based on single permutations
        :param ind1: First route
        :param ind2: Second route
        :return: Two 'child' routes
        '''
        perm=random.randint(int(self.size*0.02), int(self.size*0.05))
        C1=ind1
        C2=ind2
        while perm!=0:
            pos=random.randint(0, self.size-1)
            num1=ind1[pos]
            num2=ind2[pos]
            C2.remove(num1)
            C2.insert(pos, num1)
            C1.remove(num2)
            C1.insert(pos, num2)
            perm-=1
        return C1, C2     

    def breed(self, pool):
        '''
        Creates new routes based on the parent's
        :param pool: Parent's route
        :return: Child's route
        '''
        cross = []
        p = random.sample(pool, len(pool))
        for i in range(len(p)//2):
            child = self.crossover(p[i], p[len(pool)-i-1])
            if child is not None:
                for c in child:
                    cross.append(c)
            else:
                cross.append(p[i])
                cross.append(p[len(pool)-i-1])        
        return cross
        
    def mutateInsert(self,ind):
        '''
        Changes the placement of a city inside the route
        :param ind: Route
        :return: Mutated route
        '''
        mutInd=ind.copy()
        pos=random.randint(0, self.size-1)
        base=random.randint(0, self.size-1)

        p=mutInd[base]
        mutInd.remove(p)
        mutInd.insert(pos, p)

        f1=self.fitnessRoute(ind)
        f2=self.fitnessRoute(mutInd)
        if f1 < f2:
            if self.forceMut==True:
                return self.mutateInsert(ind)
            else:
                return ind
        elif f2 < f1:
            return mutInd

    def mutate2SWAP(self,ind):
        '''
        Permutes the placement of two cities inside the route
        :param ind: Route
        :return: Mutated route
        '''
        mutInd=ind.copy()
        i,j=(0,0)
        while i==j:
            i=random.randint(0, self.size-1)
            j=random.randint(0, self.size-1)

        G1=mutInd[i]
        G2=mutInd[j]
        mutInd[i] = G2
        mutInd[j] = G1

        f1=self.fitnessRoute(ind)
        f2=self.fitnessRoute(mutInd)
        if f1 < f2:
            if self.forceMut==True:
                return self.mutateInsert(ind)
            else:
                return ind
        elif f2 < f1:
            return mutInd

    def mutate3SWAP(self,ind):
        '''
        Permutes the placement of three cities inside the route
        :param ind: Route
        :return: Mutated route
        '''
        mutInd=ind.copy()
        i,j,k=(0,0,0)
        while i==j or j==k or k==i:
            i=random.randint(0, self.size-1)
            j=random.randint(0, self.size-1)
            k=random.randint(0, self.size-1)

        G1=mutInd[i]
        G2=mutInd[j]
        G3=mutInd[k]
        if random.random()>=0.5:
            mutInd[i]=G2
            mutInd[j]=G3
            mutInd[k]=G1
        else:
            mutInd[i]=G3
            mutInd[j]=G1
            mutInd[k]=G2
        
        f1=self.fitnessRoute(ind)
        f2=self.fitnessRoute(mutInd)
        if f1 < f2:
            if self.forceMut==True:
                return self.mutateInsert(ind)
            else:
                return ind
        elif f2 < f1:
            return mutInd

    def mutate(self,pop):
        '''
        Selects a mutation type, under a given probability.
        :param pop: List of routes
        :return: List of mutated routes
        '''
        if random.random()<=self.probMut:
            mutPop = []
            for ind in range(0, len(pop)):
                pick=random.random()
                if pick<=1/3:
                    mutInd= self.mutateInsert(pop[ind])
                elif pick>=2/3:
                    mutInd = self.mutate2SWAP(pop[ind])
                else:
                    mutInd = self.mutate3SWAP(pop[ind]) 
            mutPop.append(mutInd)
        else: mutPop=pop    
        return mutPop

    def nextGeneration(self, currentGen):
        '''
        Tests the fitness, selects the parents, breeds the children and creates a new generation
        :param currentGen: Current Generation
        :return: Next Generation
        '''
        pop = self.fitnessPop(currentGen)
        firstSelection = self.orderSelection(pop)
        secondSelection = self.tournamentSelection(firstSelection,pop)
        matingpool = self.matingPool(currentGen, secondSelection)
        crossover = self.breed(matingpool)
        nextGen = self.mutate(crossover)
        return nextGen
    
    def initialization(self):
        '''
        Creates an initial generation based on a Greedy and Random initialization.
        :return: The initial population
        '''
        k=7
        k1=(self.popSize//k)*(k-1)
        k2=(self.popSize//k)*1
        if (k1+k2) != self.popSize:
            k2+= self.popSize-(k1+k2)
        pop=self.createGreedyRoute(k1)
        pop.extend(self.createRandomRoute(k2))
        return pop

    def geneticAlgorithm(self):
        '''
        Uses a genetic algorithm to find the best route
        '''
        pop=self.initialization()
        initial=str(self.fitnessPop(pop)[0][1])
        
        count=0
        while count != self.generations:
            new_pop = self.nextGeneration(pop)
            sys.stdout.write('\r')
            to_finish=100*count/(self.generations)
            sys.stdout.write("%.2f" % to_finish + '%')
            sys.stdout.flush()
            sys.stdout.write('\r')
            count+=1
            
        print("Initial distance: " + initial)
        bestRoute=self.fitnessPop(new_pop)
        print("Final distance: " + str(bestRoute[0][1]))
        print(pop[bestRoute[0][0]])

data=Algorithm(r'qa194.tsp.txt', popSize=100, eliteSize=20, generations=500, probCross=0.75, probMut=0.5, forceMut=True)
