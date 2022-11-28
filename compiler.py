# read from input.txt
global previousNode
global currentNode


class Node:
    def __init__(self, number, dfaGraph, final=None):
        self.number = number
        self.edges = {}
        self.dfaGraph = dfaGraph
        self.final = final

    def addChildren(self, children):
        for child in children:
            edgeValue = child[0]
            childNum = child[1]
            self.edges[edgeValue] = self.dfaGraph.Nodes[childNum]

    def nextNode(self, edgeValue):
        return self.edges[edgeValue]


#
class DfaGraph:
    def __init__(self, NOState):
        self.Nodes = []
        for i in range(NOState):
            self.Nodes[i] = Node(i, self)
        self.currentNode = self.Nodes[0]
        self.previousNode = None


dfaGraph = DfaGraph(30)
dfaGraph.Nodes[0].addChildren([(1, "digit"),
                               (2, "letter"),
                               (3, "="),
                               (4, "sym"),
                               (5, "ws"),
                               (6, "/")])
dfaGraph.Nodes[1].addChildren([(1, "digit")])
dfaGraph.Nodes[2].addChildren([(2, "digit"),
                               (2,"letter")])
dfaGraph.Nodes[3].addChildren([(4, "=")])
dfaGraph.Nodes[6].addChildren([(7, "/"),
                               (8,"*")])
dfaGraph.Nodes[7].addChildren([(7,"all - \n - EOF"),
                               (10,'\n'),
                               (10,'EOF')])
dfaGraph.Nodes[8].addChildren([(8, "all - *"),
                               (9, "*")])
dfaGraph.Nodes[9].addChildren([(8, "all - /"),
                               (10, "/")])
inputFile = open("input.txt", "r")
symbol_dict = {}
symbolCount = 0
with open("symbol_table.txt", "r+") as symbolFile:
    for line in symbolFile:
        tuple = line.split()
        symbol_dict[int(tuple[1])] = True
        symbolCount += 1


def get_next_token(dfaGraph: DfaGraph):
    token = ""
    while True:
        char = inputFile.read(1)
        if char == '':
            return (dfaGraph.previousNode.final, token), True, ' '
        if char == '\n':
            return (dfaGraph.previousNode.final, token), False, '\n'
        dfaGraph.previousNode = dfaGraph.currentNode
        token += char
        dfaGraph.currentNode = dfaGraph.currentNode.nextNode(char)
        if dfaGraph.currentNode == dfaGraph.Nodes[0]:
            return (dfaGraph.previousNode.final, token[:-1]), False, ' '


tokenFile = open("tokens.txt", "w")
while True:
    nextToken, finished, lastChar = get_next_token(dfaGraph)
    if nextToken[0] == "ID":
        if nextToken[1] not in symbol_dict:
            symbolFile.write(str(symbolCount)+' '+nextToken[1]+'\n')
        symbol_dict[nextToken[1]] = True

    if finished:
        break
    tokenFile.write(str(get_next_token(dfaGraph)) + lastChar)
    # write function result to tokens.txt, each line has the line number and sequence of token pairs.

inputFile.close()
tokenFile.close()
