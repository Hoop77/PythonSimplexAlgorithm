from fractions import Fraction
import numpy
import math

class LinearProgram:
    
    def __init__( self, targetFunction, restrictions, baseVariables, nonBaseVariables, lexicographic ):
        """
        targetFunction: Array of numbers having the form: [ b, c_1, ..., c_n ]
        representing the function: b + c_1*x_1 + ... + c_n*x_n

        restrictions: Array of restrictions. A restriction has the form: [ b, a_1, ..., a_n ]
        representing the equation a_1*x_1 + ... + a_n*x_n <= b.

        baseVariables: Array of strings representing the variable names for base-variables.

        nonBaseVariables: Array of string representing the variable names for non-base-variables.

        lexicographic: Boolean which states whether the lexicographic version of the algorithm is used.
        """
        self.targetFunction = targetFunction
        self.restrictions = restrictions
        self.baseVariables = baseVariables
        self.nonBaseVariables = nonBaseVariables
        self.lexicographic = lexicographic
        self.prepareTableau()
        self.numGeneratedVariables = 0

    def printTableau( self ):
        print( "\t", end = "" )
        for c in range( len( self.colVariables ) ):
            print( self.colVariables[ c ], end = "\t" )

        print( "" )

        for r in range( self.numRows ):
            for c in range( self.numCols ):
                if( c == 0 ):
                    print( self.rowVariables[ r ], end = "\t" )
                fraction = Fraction.from_float( self.tableau[ r ][ c ] ).limit_denominator()
                print( fraction, end = "\t" )
            print( "" )
        print( "" )

    def maximize( self ):
        self.printTableau()
        pivotCol = self.findPivotCol()
        while pivotCol != -1:
            pivotRow = self.findPivotRow( pivotCol )
            if pivotRow == -1:
                print( "The linear program is not solvable!" )
                return False

            # output pivot row and column
            print( "pivot-row: " + self.rowVariables[ pivotRow ] )
            print( "pivot-column: " + self.colVariables[ pivotCol ] )

            self.createNewTableau( pivotCol, pivotRow )
            self.printTableau()
            pivotCol = self.findPivotCol()

        return True

    def maximizeInteger( self ):
        print( "Calculate relaxation" )
        print( "====================" )
        self.maximize()
        nonIntegerRow = self.findNonIntegerRow()
        while nonIntegerRow != -1:
            self.addGomorySchmittRow( nonIntegerRow )

            print( "Minimize" )
            print( "========" )
            if not self.minimize():
                return False

            nonIntegerRow = self.findNonIntegerRow()

        return True

    def findNonIntegerRow( self ):
        for r in range( self.numRows ):
            if not self.isInteger( self.tableau[ r ][ 0 ] ):
                return r
        return -1

    def isInteger( self, floatVal ):
        fraction = Fraction.from_float( floatVal ).limit_denominator()
        if fraction.denominator == 1:
            return True
        else:
            return False

    def addGomorySchmittRow( self, targetRow ):
        newRow = []
        for val in self.tableau[ targetRow ]:
            gomorySchmittVal = -(val - math.floor( val ))
            newRow.append( gomorySchmittVal )
            
        self.addRows( [ newRow ] )

        self.numGeneratedVariables += 1
        genVariable = "g" + str( self.numGeneratedVariables )
        self.addRowVariables( [ genVariable ] )

    def remaximize( self, additionalRestrictions, additionalBaseVariables ):
        """
        Only non-lexicographic way supported!
        """
        self.addRows( additionalRestrictions )
        self.addRowVariables( additionalBaseVariables )
        self.minimize()

    def minimize( self ):
        """
        Only non-lexicographic way supported!
        """
        self.printTableau()
        pivotRow = self.findPivotRowDual()
        while pivotRow != -1:
            pivotCol = self.findPivotColDual( pivotRow )
            if pivotCol == -1:
                print( "The linear program is not solvable!" )
                return False

            # output pivot row and column
            print( "pivot-row: " + self.rowVariables[ pivotRow ] )
            print( "pivot-column: " + self.colVariables[ pivotCol ] )

            self.createNewTableau( pivotCol, pivotRow )
            self.printTableau()
            pivotRow = self.findPivotRowDual()

        return True

    def addRows( self, rows ):
        for row in rows:
            self.tableau.append( row )
            self.numRows += 1

    def addRowVariables( self, additionalBaseVariables ):
        for baseVariable in additionalBaseVariables:
            self.rowVariables.append( baseVariable )

    def prepareTableau( self ):
        self.numRows = self.getNumRows()
        self.numCols = self.getNumCols()
        self.rowVariables = self.getRowVariables()
        self.colVariables = self.getColVariables()

        self.tableau = []
        self.createFirstRowOfTableau()
        self.createBodyOfTableau()

    def createFirstRowOfTableau( self ):
        # first row = target function
        row = []
        row.append( self.targetFunction[ 0 ] )

        if self.lexicographic:
            for b in self.baseVariables:
                row.append( 0 )

        for c in range( 1, len( self.targetFunction ) ):
            row.append( -self.targetFunction[ c ] )

        self.tableau.append( row )

    def createBodyOfTableau( self ):
        for r in range( 0, self.numRows - 1 ):
            row = []
            row.append( self.restrictions[ r ][ 0 ] )

            if self.lexicographic:
                for c in range( len( self.baseVariables ) ):
                    if r == c:
                        row.append( 1 )
                    else:
                        row.append( 0 )
                
            for c in range( len( self.nonBaseVariables ) ):
                row.append( self.restrictions[ r ][ c + 1 ] )

            self.tableau.append( row )

    def findPivotCol( self ):
        for c in range( 1, self.numCols ):
            val = self.tableau[ 0 ][ c ]
            if val < 0:
                return c
        return -1

    def findPivotColDual( self, pivotRow ):
        possiblePivotCols = self.getColsWherePivotElementIsSmallerThanZero( pivotRow )
        if len( possiblePivotCols ) == 0:
            return -1

        tuples = self.getTuplesFromRow( 0, pivotRow, possiblePivotCols )
        return self.extractPossiblePivotColsFromTuplesInLexicographicOrder( tuples )[ 0 ]

    def findPivotRow( self, pivotCol ):
        if self.lexicographic:
            return self.findPivotRowByLexicographicSearch( pivotCol )

        return self.findPivotRowByNormalSearch( pivotCol )

    def findPivotRowDual( self ):
        for r in range( 1, self.numRows ):
            val = self.tableau[ r ][ 0 ]
            if val < 0:
                return r
        return -1
            
    def findPivotRowByLexicographicSearch( self, pivotCol ):
        possiblePivotRows = self.getRowsWherePivotElementIsGreaterThanZero( pivotCol )
        tuples = self.getTuplesFromCol( 0, pivotCol, possiblePivotRows )
        for c in range( self.numCols ):
            possiblePivotRows = self.extractPossiblePivotRowsFromTuplesInLexicographicOrder( tuples )
            if len( possiblePivotRows ) == 1:
                break
            tuples = self.getTuplesFromCol( c, pivotCol, possiblePivotRows )
        
        if len( possiblePivotRows ) == 0:
            return -1

        return possiblePivotRows[ 0 ]

    def findPivotRowByNormalSearch( self, pivotCol ):
        possiblePivotRows = self.getRowsWherePivotElementIsGreaterThanZero( pivotCol )
        if len( possiblePivotRows ) == 0:
            return -1

        tuples = self.getTuplesFromCol( 0, pivotCol, possiblePivotRows )
        return self.extractPossiblePivotRowsFromTuplesInLexicographicOrder( tuples )[ 0 ]

    def getRowsWherePivotElementIsGreaterThanZero( self, pivotCol ):
        rows = []
        for r in range( 1, self.numRows ):
            pivotElement = self.tableau[ r ][ pivotCol ]
            if pivotElement > 0:
                rows.append( r )
        return rows

    def getColsWherePivotElementIsSmallerThanZero( self, pivotRow ):
        cols = []
        for c in range( 1, self.numCols ):
            pivotElement = self.tableau[ pivotRow ][ c ]
            if pivotElement < 0:
                cols.append( c )
        return cols

    def getTuplesFromCol( self, currCol, pivotCol, possiblePivotRows ):
        """
        currCol, pivotCol are indices
        returns a list of tuples where each tuple represents:
        (lexicographic value, row)
        """
        tuples = []
        for r in possiblePivotRows:
            val = self.tableau[ r ][ currCol ] / self.tableau[ r ][ pivotCol ]
            t = ( val, r )
            tuples.append( t )
        return tuples

    def getTuplesFromRow( self, currRow, pivotRow, possiblePivotCols ):
        """
        currRow, pivotRow are indices
        returns a list of tuples where each tuple represents:
        (lexicographic value, column)
        """
        tuples = []
        for c in possiblePivotCols:
            val = self.tableau[ currRow ][ c ] / abs( self.tableau[ pivotRow ][ c ] )
            t = ( val, c )
            tuples.append( t )
        return tuples

    def extractPossiblePivotRowsFromTuplesInLexicographicOrder( self, tuples ):
        tuples.sort()
        possiblePivotRows = []
        firstTuple = tuples[ 0 ]
        firstVal = firstTuple[ 0 ]
        for t in tuples:
            val = t[ 0 ]
            row = t[ 1 ]
            if val != firstVal:
                break
            possiblePivotRows.append( row )

        return possiblePivotRows

    def extractPossiblePivotColsFromTuplesInLexicographicOrder( self, tuples ):
        tuples.sort()
        possiblePivotRows = []
        firstTuple = tuples[ 0 ]
        firstVal = firstTuple[ 0 ]
        for t in tuples:
            val = t[ 0 ]
            col = t[ 1 ]
            if val != firstVal:
                break
            possiblePivotRows.append( col )

        return possiblePivotRows

    def createNewTableau( self, pivotCol, pivotRow ):
        newTableau = self.createEmptyTable()

        # mind the swap of column in lexicographic mode
        pivotRowVariable = self.rowVariables[ pivotRow ]
        swappedCol = 0
        if self.lexicographic:
            swappedCol = self.colVariables.index( pivotRowVariable )
        else:
            swappedCol = pivotCol

        self.swapBase( pivotCol, pivotRow )
        pivotElement = self.tableau[ pivotRow ][ pivotCol ]
        
        for r in range( self.numRows ):
            for c in range( self.numCols ):
                if c == swappedCol and r == pivotRow:
                    newTableau[ r ][ c ] = 1 / pivotElement
                elif c == swappedCol and r != pivotRow:
                    newTableau[ r ][ c ] = self.tableau[ r ][ pivotCol ] / pivotElement * -1
                elif c != swappedCol and r == pivotRow:
                    newTableau[ r ][ c ] = self.tableau[ r ][ c ] / pivotElement
                else:
                    newTableau[ r ][ c ] = (self.tableau[ r ][ c ] - \
                    ( (self.tableau[ r ][ pivotCol ] * self.tableau[ pivotRow ][ c ]) / pivotElement ))
        
        self.tableau = newTableau

    def createEmptyTable( self ):
        newTableau = []
        for r in range( self.numRows ):
            row = []
            for c in range( self.numCols ):
                row.append( 0 )
            newTableau.append( row )
        return newTableau
        
    def swapBase( self, pivotCol, pivotRow ):
        pivotRowVariable = self.rowVariables[ pivotRow ]
        pivotColVariable = self.colVariables[ pivotCol ]

        self.rowVariables[ pivotRow ] = pivotColVariable

        if not self.lexicographic:
            self.colVariables[ pivotCol ] = pivotRowVariable

    def getRowVariables( self ):
        rowVariables = [ "" ]
        for b in self.baseVariables:
            rowVariables.append( b )
        return rowVariables

    def getColVariables( self ):
        colVariables = [ "" ]

        if( self.lexicographic ):
            for b in self.baseVariables:
                colVariables.append( b )

        for n in self.nonBaseVariables:
            colVariables.append( n )

        return colVariables

    def getNumRows( self ):
        return len( self.baseVariables ) + 1

    def getNumCols( self ):
        if self.lexicographic:
            return len( self.nonBaseVariables ) + len( self.baseVariables ) + 1
        else:
            return len( self.nonBaseVariables ) + 1

if __name__ == '__main__':

    # # maximize
    # targetFunction = [ 8, -9, -4 ]
    # restrictions = [
    #     [ 2, 2, 3 ],
    #     [ 5, 8, 9 ]
    # ]
    # baseVariables = [ "x1", "x2" ]
    # nonBaseVariables = [ "x1", "u2" ]

    # lp = LinearProgram( targetFunction, restrictions, baseVariables, nonBaseVariables, False )
    # lp.maximize()

    # # remaximize
    # additionalRestrictions = [ 
    #     [ -1, -2, 1 ]
    # ]
    # additionalBaseVariables = [ "u3" ]

    # lp.remaximize( additionalRestrictions, additionalBaseVariables )

    # maximize
    targetFunction = [ 0, 3, -5, 4 ]
    restrictions = [
        [ 6, 3, 1, 1 ],
        [ 6, 1, 2, 3 ],
        [ 3, 1, -1, 2 ]
    ]
    baseVariables = [ "u1", "u2", "u3" ]
    nonBaseVariables = [ "x1", "x2", "x3" ]

    lp = LinearProgram( targetFunction, restrictions, baseVariables, nonBaseVariables, False )
    lp.maximizeInteger()