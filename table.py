from fractions import Fraction
import numpy
import math

class Table:

    def __init__( self, tableData, base, nobase ):
        self.tableData = tableData
        self.base = base
        self.nobase = nobase
        self.numRows = self.getNumRows()
        self.numCols = self.getNumCols()
        self.rowLabels = self.getRowLabels( base )
        self.colLabels = self.getColLabels( base, nobase )

    def printTable( self ):
        print( "\t", end = "" )
        for c in range( len( self.colLabels ) ):
            print( self.colLabels[ c ], end = "\t" )

        print( "" )

        for r in range( self.numRows ):
            for c in range( self.numCols ):
                if( c == 0 ):
                    print( self.rowLabels[ r ], end = "\t" )
                fraction = Fraction.from_float( self.tableData[ c ][ r ] ).limit_denominator()
                print( fraction, end = "\t" )
            print( "" )
        print( "" )

    def solve( self ):
        self.printTable()
        
        pivotCol = self.findPivotCol()
        while pivotCol != -1:
            pivotRow = self.findPivotRow( pivotCol )

            # output pivot row and column
            print( "pivot-row: " + self.rowLabels[ pivotRow ] )
            print( "pivot-column: " + self.colLabels[ pivotCol ] )

            self.createNewTable( pivotCol, pivotRow )
            self.printTable()
            pivotCol = self.findPivotCol()

    def findPivotCol( self ):
        for r in range( 1, len( tableData ) ):
            val = self.tableData[ r ][ 0 ]
            if( val < 0 ):
                return r
        return -1

    def findPivotRow( self, pivotCol ):
        possiblePivotRows = self.getRowsWherePivotElementIsGreaterThanZero( pivotCol )
        tupleList = self.getTupleListFromCol( 0, pivotCol, possiblePivotRows )
        for c in range( self.numCols ):
            possiblePivotRows = self.extractPossiblePivotRowsFromTupleList( tupleList )
            if len( possiblePivotRows ) == 1:
                break
            tupleList = self.getTupleListFromCol( c, pivotCol, possiblePivotRows )
        
        return possiblePivotRows[ 0 ]

    def getRowsWherePivotElementIsGreaterThanZero( self, pivotCol ):
        rows = []
        for r in range( 1, self.numRows ):
            pivotElement = self.tableData[ pivotCol ][ r ]
            if pivotElement > 0:
                rows.append( r )
        return rows

    def getTupleListFromCol( self, currCol, pivotCol, possiblePivotRows ):
        """
        currCol, pivotCol are indices
        returns a list of tuples where each tuple represents:
        (lexicographic value, row)
        """
        tupleList = []
        for r in possiblePivotRows:
            val = self.tableData[ currCol ][ r ] / self.tableData[ pivotCol ][ r ]
            t = ( val, r )
            tupleList.append( t )
        return tupleList

    def extractPossiblePivotRowsFromTupleList( self, tupleList ):
        tupleList.sort()
        possiblePivotRows = []
        firstTuple = tupleList[ 0 ]
        firstVal = firstTuple[ 0 ]
        for t in tupleList:
            val = t[ 0 ]
            row = t[ 1 ]
            if val != firstVal:
                break
            possiblePivotRows.append( row )

        return possiblePivotRows

    def createNewTable( self, pivotCol, pivotRow ):
        newTableData = self.createEmptyTable()

        rowLabel = self.rowLabels[ pivotRow ]
        swapCol = self.colLabels.index( rowLabel )

        self.swapBase( pivotCol, pivotRow )
        pivotElement = self.tableData[ pivotCol ][ pivotRow ]
        
        for c in range( self.numCols ):
            for r in range( self.numRows ):
                if c == swapCol and r == pivotRow:
                    newTableData[ c ][ r ] = 1 / pivotElement
                elif c == swapCol and r != pivotRow:
                    newTableData[ c ][ r ] = self.tableData[ pivotCol ][ r ] / pivotElement * -1
                elif c != swapCol and r == pivotRow:
                    newTableData[ c ][ r ] = self.tableData[ c ][ r ] / pivotElement
                else:
                    newTableData[ c ][ r ] = (self.tableData[ c ][ r ] - \
                    ( (self.tableData[ pivotCol ][ r ] * self.tableData[ c ][ pivotRow ]) / pivotElement ))
        
        self.tableData = newTableData

    def createEmptyTable( self ):
        newTableData = []
        for c in range( self.numCols ):
            col = []
            for r in range( self.numRows ):
                col.append( 0 )
            newTableData.append( col )
        return newTableData

        
    def swapBase( self, pivotCol, pivotRow ):
        colLabel = self.colLabels[ pivotCol ]
        self.rowLabels[ pivotRow ] = colLabel

    def getRowLabels( self, base ):
        rowLabels = [ "" ]
        for b in base:
            rowLabels.append( b )
        return rowLabels

    def getColLabels( self, base, nonbase ):
        colLabels = [ "" ]
        for b in base:
            colLabels.append( b )
        for n in nonbase:
            colLabels.append( n )
        return colLabels

    def getNumRows( self ):
        return len( self.tableData[ 0 ] )

    def getNumCols( self ):
        return len( self.tableData )

if __name__ == '__main__':

    # tableData = [
    #         [ 4, 8, 12, -4 ],
    #         [ 0, 1, 0, 0 ],
    #         [ 0, 0, 1, 0 ],
    #         [ 0, 0, 0, 1 ],
    #         [ 1, 2, -1, -1 ],
    #         [ 1, -1, 3, -1 ],
    #         [ -5, 2, 3, 5 ],
    #         [ 1, 0, 0, -1 ]
    #     ]

    # base = [ "u1", "u2", "y3" ]
    # nobase = [ "x1", "x2", "x3", "u3" ]

    tableData = [
        [ 0, 0, 0, 1 ],
        [ 0, 1, 0, 0 ],
        [ 0, 0, 1, 0 ],
        [ 0, 0, 0, 1 ],
        [ -0.75, 0.25, 0.5, 0 ],
        [ 150, -60, -90, 0 ],
        [ -0.02, -0.04, -0.02, 3 ],
        [ 6, 9, 3, 0 ]
    ]

    base = [ "u1", "u2", "u3" ]
    nobase = [ "x1", "x2", "x3", "x4" ]

    table = Table( tableData, base, nobase )
    table.solve()
