class BFSElement:
    def __init__(self, i, j):
        self.i = i
        self.j = j


def findPath(matrix, size):
    # 1) Create BFS queue q
    q = []

    # 2)scan the matrix
    for i in range(size):
        for j in range(size):

            # if there exists a cell in the matrix such
            # that its value is 1 then append it to q
            if matrix[i, j] == 1:
                q.append(BFSElement(i, j))
                break

    # 3) run BFS algorithm with q.
    while len(q) != 0:
        x = q[0]
        q = q[1:]

        i = x.i
        j = x.j

        # skipping cells which are not valid.
        # if outside the matrix bounds
        if i < 0 or i >= size or j < 0 or j >= size:
            continue

        # if they are walls (value is 0).
        if matrix[i, j] == 0:
            continue

        # 3.1) if in the BFS algorithm process there was a
        # vertex x=(i,j) such that M[i][j] is 2 stop and
        # return True
        if matrix[i, j] == 2:
            return True

        # marking as wall upon successful visitation
        matrix[i][j] = 0

        # appending to queue u=(i,j+1),u=(i,j-1)
        # u=(i+1,j),u=(i-1,j)
        for k in range(-1, 2, 2):
            q.append(BFSElement(i + k, j))
            q.append(BFSElement(i, j + k))

    # BFS algorithm terminated without returning True
    # then there was no element M[i][j] which is 2, then
    # return false
    return False

# This code is contributed by shinjanpatra from GeeksForGeeks
