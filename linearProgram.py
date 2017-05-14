from fractions import Fraction
import numpy
import math

class LinearProgram:

    def __init__( self, targetFunction, restrictions, baseVariables, nonBaseVariables ):
        self.targetFunction = targetFunction
        self.restrictions = restrictions
        self.baseVariables = baseVariables
        self.nonBaseVariables = nonBaseVariables

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

    def solve( self, lexicographic ):
        self.lexicographic = lexicographic
        self.prepareTableau()
        self.printTableau()
        
        pivotCol = self.findPivotCol()
        while pivotCol != -1:
            pivotRow = self.findPivotRow( pivotCol )

            # output pivot row and column
            print( "pivot-row: " + self.rowVariables[ pivotRow ] )
            print( "pivot-column: " + self.colVariables[ pivotCol ] )

            self.createNewTableau( pivotCol, pivotRow )
            self.printTableau()
            pivotCol = self.findPivotCol()

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
            if( val < 0 ):
                return c
        return -1

    def findPivotRow( self, pivotCol ):
        if self.lexicographic:
            return self.findPivotRowByLexicographicSearch( pivotCol )

        return self.findPivotRowByNormalSearch( pivotCol )
            
    def findPivotRowByLexicographicSearch( self, pivotCol ):
        possiblePivotRows = self.getRowsWherePivotElementIsGreaterThanZero( pivotCol )
        tuples = self.getTuplesFromCol( 0, pivotCol, possiblePivotRows )
        for c in range( self.numCols ):
            possiblePivotRows = self.extractPossiblePivotRowsFromTuplesInLexicographicOrder( tuples )
            if len( possiblePivotRows ) == 1:
                break
            tuples = self.getTuplesFromCol( c, pivotCol, possiblePivotRows )
        
        return possiblePivotRows[ 0 ]

    def findPivotRowByNormalSearch( self, pivotCol ):
        possiblePivotRows = self.getRowsWherePivotElementIsGreaterThanZero( pivotCol )
        tuples = self.getTuplesFromCol( 0, pivotCol, possiblePivotRows )
        return self.extractPossiblePivotRowsFromTuplesInLexicographicOrder( tuples )[ 0 ]

    def getRowsWherePivotElementIsGreaterThanZero( self, pivotCol ):
        rows = []
        for r in range( 1, self.numRows ):
            pivotElement = self.tableau[ r ][ pivotCol ]
            if pivotElement > 0:
                rows.append( r )
        return rows

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

    targetFunction = [ 0, 1, 1 ]
    restrictions = [
        [ 1, -1, 1 ],
        [ 3, 1, 0 ],
        [ 2, 0, 1 ]
    ]
    baseVariables = [ "u1", "u2", "u3" ]
    nonBaseVariables = [ "x1", "x2" ]

    lp = LinearProgram( targetFunction, restrictions, baseVariables, nonBaseVariables )
    lp.solve( False )