""" Author: Michael Munson
    Date: 9/18/2015
    CSSE 413
"""
import argparse
import time
    
class Sudoku:
    def __init__(self, puzzle, boxWidth):
        self.puzzle = puzzle 
        self.boxWidth = boxWidth                          
        self.width = self.boxWidth * self.boxWidth
        
        self.nValuesTried = 0
        self.startTime = time.clock()
        

class Assignment:
    
    def __init__(self, puzzle, sudoku):
        
        self.unassignedVariables = []
        self.currAssignment = puzzle
        
        for i in range(sudoku.width):
            for j in range(sudoku.width):
                
                if puzzle[i][j] == 0:
                        self.unassignedVariables.append( [ (i,j) , range(1,sudoku.width+1) ] )   # all values in {1,9} are allowable initially
                    
                        #self.unassignedVariables.mrvInsert(self, [ (i,j) , range(1,sudoku.width+1) ])
        
    def initialDomainReduction(self, sudoku):
        i=0
        
        iCorrection = False
        
        nextLoc = (-1,-1)
        
        while i < len(self.unassignedVariables):
            
            if iCorrection:
                j=0
                while j < len(self.unassignedVariables):
                    if nextLoc == self.unassignedVariables[j][0]:
                        i = j
                        break;
                    j += 1
            iCorrection = False
                   
            if i < len(self.unassignedVariables) - 1:
                nextLoc = self.unassignedVariables[i+1][0]
            
            var = self.unassignedVariables[i]
            
            [(row, col), domain] = var
#             if not i%5 or i > 25 and i < 30: 
#                 print i
#             #if i == 28 or (row, col) == (5,0):
#                 print "Let's take a look"

            var = self.rowUpdate(var, sudoku.width)
            var = self.colUpdate(var, sudoku.width)
            var = self.boxUpdate(var, sudoku.boxWidth)
 
            #self.unassignedVariables[i] = var    #update domain
            
            if len(domain) == 1:
                
                self.currAssignment[row][col] = domain[0]
                
                self.unassignedVariables.pop(i)
                
                inferences = []
                
                result = doInference((row, col), domain[0], sudoku, self, inferences)
                iCorrection = True
                
                if result == 'failure':
                    return 'failure'
                
            elif len(domain) == 0:
                # Error: no solution exists for this puzzle   <---------------   IMPLEMENT
                # should exit program; basically return failure
                return 'failure'    #modify                    <------
                
            i += 1

    def rowUpdate(self, var, width):
    # update domain, and possibly assignment
    # self.currentAssignment
        [(row, col), domain] = var
        
        for j in range(width):
            value = self.currAssignment[row][j] 
            if not value == 0:
                if domain.count(value) != 0:
                    domain.remove(value)
        
        var = [(row, col), domain]
        return var
    
    def colUpdate(self, var, width):
    # update domain, and possibly assignment
    # self.currentAssignment
        [(row, col), domain] = var
        
        for i in range(width):
            value = self.currAssignment[i][col] 
            if not value == 0:
                if domain.count(value) != 0:
                    domain.remove(value)
        
        var = [(row, col), domain]
        return var
    
    def boxUpdate(self, var, boxWidth):
        [(row, col), domain] = var
        
        boxUpperLeft = ( (row/boxWidth) * boxWidth, (col/boxWidth) * boxWidth  )
        
        for i in range(boxWidth):
            for j in range(boxWidth):
                value = self.currAssignment[boxUpperLeft[0] + i][boxUpperLeft[1] + j]
                if not value == 0:
                    if domain.count(value) != 0:
                        domain.remove(value)
                    
        var = [(row, col), domain]
        
        return var
    
    
    

def parseAndInitialize(boxWidth):
    parser = argparse.ArgumentParser(description='Solve a sudoku puzzle')
    parser.add_argument('puzzleFile', metavar='p', type=argparse.FileType('r'),help='the file containing the puzzle')
    parser.add_argument('idrFlag', metavar='i', type=int,default=0, help='initial domain reduction flag (default=0: no pre-processing, 1: pre-process domains to ensure consistency with binary constraints)')
    parser.add_argument('suvFlag', metavar='s', type=int,default=0, help='select unassigned variable flag (default=0: index ordering, 1: minimum remaining values heuristic)')
    parser.add_argument('odvFlag', metavar='o', type=int,default=0, help='order domain values flag (default=0: index ordering, 1: least constraining values heuristic)')
    
    """
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                   const=sum, default=max,
                   help='sum the integers (default: find the max)')          
    """
    args = parser.parse_args()

    puzzle = readPuzzleFile(args.puzzleFile, boxWidth)
    
    print "Puzzle:"
    for row in puzzle:
        print row
    
    sudoku = Sudoku(puzzle, boxWidth)
    assignment = Assignment(puzzle, sudoku)   
     
    idrFlag = args.idrFlag
    
    if idrFlag:
        result = assignment.initialDomainReduction(sudoku)        
        if result == 'failure':
            print '\nThere is no solution for this puzzle\n'
            return
        
    flags = (args.suvFlag,args.odvFlag)  
    
    result = backtrackingSearch(sudoku, assignment, flags)

    if result == 'failure':
        print '\nThere is no solution for this puzzle\n'
    else:
        displaySolution(sudoku, assignment)


def readPuzzleFile(puzzleFile, boxWidth):
    puzzle = []
    
    nValsInLine = boxWidth * boxWidth
    
    for line in puzzleFile:
        lineEntries = []
        for i in range(nValsInLine):    #(len(line) - 1):    # strip final '/n' character, except in final line
            lineEntries.append(int(line[i]))
        puzzle.append(lineEntries)

    #puzzle[len(puzzle) - 1].append(lastEntry)               # last line has no terminal '/n' character  
     
    return puzzle



def backtrackingSearch(sudoku, assignment, flags=(0,0)):
    """
    flags = (suvFlag, odvFlag, consFlag, infFlag) 
    suvFlag: select unassigned variable flag
        0: select variables in index order
        1: minimum remaining values (MRV) heuristic
    odvFlag: order domain values flag
        0: selected values in index order
        1: least constraining values heuristic
    consFlag:
        0: consistency checking directly against currentAssignment
        1: consistency checking by checking domain         
    infFlag: inference Flag
        0: no inference
        1: forward checking
    """
    
    return backtrack(sudoku, assignment, flags)
                        

def backtrack(sudoku, assignment, flags):      
    if isComplete(assignment):
        
        return assignment
    
    var = selectUnassignedVariable(assignment, sudoku, flags[0])

    
    for value in orderDomainValues(var, assignment, sudoku, flags[1]):
        
        sudoku.nValuesTried += 1
        (row, col) = var[0]
        
        if isConsistentWithAssignment((row,col), value, assignment, sudoku):
            assignment.currAssignment[row][col] = value
            inferences = []

            btResult = backtrack(sudoku, assignment, flags)
            if btResult != 'failure':
                return btResult
                #removeInferencesFromAssignment(inferences, assignment)  
            #else:
                #removeInferencesFromAssignment(inferences, assignment)
            
        assignment.currAssignment[row][col] = 0              #remove var = value from assignment: not consistent, either in assignment or inference fails
    
    index = findReinsertIndex(assignment.unassignedVariables, var[0])
    assignment.unassignedVariables.insert(index, var)
    return 'failure'

                
def isComplete(assignment):
    return len(assignment.unassignedVariables) == 0

def selectUnassignedVariable(assignment, sudoku, method=0):
    if method == 0:   # select variables in index order
        var = assignment.unassignedVariables.pop(0)
    if method == 1:
        minDomSize = sudoku.width + 1
        minDomVar = []
        minDomIndex = -1
        i=0
        for var in assignment.unassignedVariables:
            
            domain = var[1]
            
            if len(domain) == 1:
                assignment.unassignedVariables.pop(i)
                
                #print "len(domain) == 1"
                
                return var
            elif len(domain) < minDomSize:
                minDomSize = len(domain)
                minDomVar = var
                minDomIndex = i
            i += 1
            
        var = minDomVar
        assignment.unassignedVariables.pop(minDomIndex)
        
        
    return var

def orderDomainValues(var, assignment, sudoku, method=0):
    [location, domain] = var
    
    if method == 0:
        orderedDomain = domain
    if method == 1:    #Least Constraining Value   (LCV)
        orderedDomain = []
        
        neighbors = findUnassignedNeighbors(location, sudoku, assignment)
        
        penaltySize = 0
        
        for value in domain:
            for square in neighbors:
                index = square[1]
                thisDomain = assignment.unassignedVariables[index][1] 
                if thisDomain.count(value) != 0:
                    penaltySize += 1
                    if len(thisDomain) == 1: 
                        penaltySize += 999999
            i = findLCVInsertLocation(orderedDomain, penaltySize)
            orderedDomain.insert(i, (value, penaltySize))   
        
        for i in range(len(orderedDomain)):
            orderedDomain[i] = orderedDomain[i][0]   # remove penaltySize field before returning
                    
    return orderedDomain


def findLCVInsertLocation(orderedDomain, penaltySize):
    i=0
    for i in range(len(orderedDomain)):
        if(penaltySize >= orderedDomain[i][1]):
            i += 1    
    return i
    
def findUnassignedNeighbors(location, sudoku, assignment):
    neighbors = []
    width = sudoku.width 
    boxWidth = sudoku.boxWidth
    
    findUnassignedRowNeighbors(location, assignment, neighbors, width)
    findUnassignedColNeighbors(location, assignment, neighbors, width)
    findUnassignedBoxNeighbors(location, assignment, neighbors, boxWidth)
    
    return neighbors


def findUnassignedRowNeighbors(location, assignment, neighbors, width):
    
    (row, col) = location
    
    for j in range(width):
        if assignment.currAssignment[row][j] == 0 and j != col:
            k=0
            for var in assignment.unassignedVariables:
                if var[0] ==(row, j):
                    neighbors.append((var, k))     # include index k for easier look-up        
                k += 1
    

    
def findUnassignedColNeighbors(location, assignment, neighbors, width):
    
    (row, col) = location
    
    for i in range(width):
        if assignment.currAssignment[i][col] == 0 and row != i:
            k=0
            for var in assignment.unassignedVariables:
                if var[0] ==(i, col):
                    neighbors.append((var, k)) 
                k += 1
    return neighbors

   
def findUnassignedBoxNeighbors(location, assignment, neighbors, boxWidth):
    
    (row, col) = location
    
    boxUpperLeft = ( (row/boxWidth) * boxWidth, (col/boxWidth) * boxWidth  )
        
    for i in range(boxWidth):
        for j in range(boxWidth):
            thisRow = boxUpperLeft[0] + i
            thisCol = boxUpperLeft[1] + j
            if assignment.currAssignment[thisRow][thisCol] ==0 and not (thisRow ==row and thisCol ==col):
                k = 0
                for var in assignment.unassignedVariables:
                    if var[0] ==(boxUpperLeft[0] + i, boxUpperLeft[1] + j):
                        neighbors.append((var, k)) 
                    k += 1


def isConsistentWithAssignment(location, value, assignment, sudoku):    #could have a flag for checking directly against domain, if this is properly updated
    #isConsistent = True
    
    #if flag ==0:
        if not isRowConsistent(location, value, assignment):
            return False
        if not isColConsistent(location, value, assignment, sudoku):
            return False
        if not isBoxConsistent(location, value, assignment, sudoku):
            return False
        return True
#     if flag ==1:
#         domain = var[1]
#         return not domain.count(value) == 0



def isRowConsistent(location, value, assignment):
        
        (row, col) = location
        rowVals = assignment.currAssignment[row] 
        return rowVals.count(value) == 0

def isColConsistent(location, value, assignment, sudoku):
    #update domain, and possibly assignment
    # self.currentAssignment
        (row, col) = location
        
        for i in range(sudoku.width):
            puzzVal = assignment.currAssignment[i][col] 
            if puzzVal == value:
                return False
        return True
    
    

def isBoxConsistent(location, value, assignment, sudoku):
    (row, col)  = location
        
    boxWidth = sudoku.boxWidth
        
    boxUpperLeft = ( (row/boxWidth) * boxWidth, (col/boxWidth) * boxWidth  )
        
    for i in range(boxWidth):
        for j in range(boxWidth):
            puzzVal = assignment.currAssignment[boxUpperLeft[0] + i][boxUpperLeft[1] + j]
            if puzzVal == value:
                return False
        return True

def areNeighbors(loc1, loc2, sudoku):
    width = sudoku.width 
    boxWidth = sudoku.boxWidth
    if areRowNeighbors(loc1, loc2, width) or areColNeighbors(loc1, loc2, width) or areBoxNeighbors(loc1, loc2, boxWidth):
        return True
    return False
    
def areRowNeighbors(loc1, loc2, width):    
    return loc1[0] == loc2[0]

def areColNeighbors(loc1, loc2, width):
    return loc1[1] == loc2[1]
    
def areBoxNeighbors(loc1, loc2, boxWidth):
    return loc1[0]/boxWidth == loc2[0]/boxWidth and loc1[1]/boxWidth == loc2[1]/boxWidth
       

def doInference(location, value, sudoku, assignment, inferences):
    # each entry in inferences is [unassignedVarsIndex, oneValueRemainingFlag]
    #if flag == 0:
    
    neighbors = findUnassignedNeighbors(location, sudoku, assignment)
    
    variableAssignedFlag = 1
    variableNotAssignedFlag = 0
    
    numToAssign = 0
    
    for square in neighbors:
        uavIndex = square[1]    #unassignedVariables index
        location = square[0]
        
        thisDomain = assignment.unassignedVariables[uavIndex][1] 
        if thisDomain.count(value) != 0:
            if len(thisDomain) == 1:
                return 'failure'
            if len(thisDomain) == 2:
                inferences.insert(0, (uavIndex, variableAssignedFlag, location, value))    # we will assign these variables to the single remaining value 
                numToAssign += 1
            else:
                inferences.append((uavIndex, variableNotAssignedFlag, location, value))   # we will not assign these variables yet; they have multiple remaining values
            assignment.unassignedVariables[uavIndex][1].remove(value)      # remove value from domain
            
    locationsAndValues = []
    for i in range(numToAssign):
        assignmentVal = inferences[i][2][1][0]
        assignmentLoc = inferences[i][2][0]
        
#         duplicates = [(3,4),(4,5),(4,6),(5,1),(5,7),(0,3),(8,3),(2,6),(3,7),(6,7)]
#         if duplicates.count(assignmentLoc) == 1:

        
        for locVal in locationsAndValues:
            alreadyAssignedLoc = locVal[0]
            alreadyAssignedVal = locVal[1]
                            
            if alreadyAssignedVal == assignmentVal and areNeighbors(alreadyAssignedLoc, assignmentLoc, sudoku) or not isConsistentWithAssignment(assignmentLoc, assignmentVal, assignment, sudoku):
                return 'failure'
             
        (thisLocation, assignmentValue) = assignThisInferenceVarAndValue(assignment, inferences, i)   
        locationsAndValues.append((thisLocation, assignmentValue))
    
    for i in range(numToAssign): 
        thisLocation = locationsAndValues[i][0]
        assignmentValue = locationsAndValues[i][1]                                        # we separate these two steps so that we don't fail on a variable we were about to assign
        result = doInference(thisLocation, assignmentValue, sudoku, assignment, inferences)
    
        if result == 'failure':
            return 'failure'
            
    return inferences


        
def removeInferencesFromAssignment(inferences, assignment):
    #inf: [unassignedVarsIndex, variableAssigned flag (2 denotes already assigned), [squareLocation, assignmentValue], inconsistentValue]
    alreadyAssignedFlag = 2
    notAssignedFlag = 0
    
    for inf in inferences:  
        varAssignedFlag = inf[1]  
        [(row, col), thisDomain] = inf[2]
        eliminatedValue = inf[3]
         
        if varAssignedFlag == alreadyAssignedFlag:            # if a square appears in inferences with both a vA flag of 0 and of 2, we are guaranteed that it appears first with a flag of 2; thus, we create the unassignedVars entry before augmenting its domain (when the flag is 0) 
            assignment.currAssignment[row][col] = 0
            assignedValue = thisDomain[0]
            index = findReinsertIndex(assignment.unassignedVariables, (row, col))
            var = [(row, col), [assignedValue, eliminatedValue]]
            assignment.unassignedVariables.insert(index, var)
        
        if varAssignedFlag == notAssignedFlag:
            i=0
            while assignment.unassignedVariables[i][0] != (row, col):                     # FIXME: domain should belong to square, not uaVars entry
                i += 1
            assignment.unassignedVariables[i][1].append(eliminatedValue)    # add value back to domain
        
            
            
def assignThisInferenceVarAndValue(assignment, inferences, i):
    
    alreadyAssignedFlag = 2
    [thisLocation, thisDomain] = inferences[i][2]
    eliminatedValue = inferences[i][3]
    j=0
    while assignment.unassignedVariables[j][0] != thisLocation:                     # FIXME: domain should belong to square, not uaVars entry
        j += 1
    thisVar = assignment.unassignedVariables.pop(j)
    assignmentValue = thisDomain[0]
    (row, col) = thisLocation
    
    assignment.currAssignment[row][col] = assignmentValue
        
    inferences[i] = ( inferences[i][0], alreadyAssignedFlag, thisVar, eliminatedValue)     # MAY NEED TO CHANGE WHERE THIS IS STORED
    
    return ((row, col), assignmentValue)

        
def findReinsertIndex(unassignedVars, location):
    #assume location not represented in unassignedVars; and uaVars is in sorted order by (row,col) of location
    row = location[0]
    col = location[1]
    i=0
    
    while i<len(unassignedVars) and row >= unassignedVars[0][0] and col > unassignedVars[0][1]:
        i+=1
        
    return i

def displaySolution(sudoku, assignment):
    elapsedTime = time.clock() - sudoku.startTime
    print 'Solved puzzle: '
    for row in assignment.currAssignment:
        print str(row)
    print 'Number of values tried: '
    print sudoku.nValuesTried
    print 'Elapsed Time:'
    print elapsedTime


if __name__ == "__main__":
  boxWidth = 3
  parseAndInitialize(boxWidth)
