# A simple Python3 program to find
# maximum score that
# maximizing player can get
import math
def minimax(curDepth, nodeIndex, maxTurn, evaluations, targetDepth):
    # base case : targetDepth reached
    if curDepth == targetDepth:
        return evaluations[nodeIndex]

    if maxTurn:
        return max(minimax(curDepth + 1, nodeIndex * 2, False, evaluations, targetDepth),
                   minimax(curDepth + 1, nodeIndex * 2 + 1, False, evaluations, targetDepth))

    else:
        return min(minimax(curDepth + 1, nodeIndex * 2, True, evaluations, targetDepth),
                   minimax(curDepth + 1, nodeIndex * 2 + 1, True, evaluations, targetDepth))

# Driver code
#scores = [3, 5, 2, 9, 12, 5, 23, 23]
#treeDepth = math.log(len(scores), 2)
#print("The optimal value is : ", end="")
#print(minimax(0, 0, True, scores, treeDepth))

# This code was found on GeeksforGeeks (https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-1-introduction/
# and is contributed by rootshadow