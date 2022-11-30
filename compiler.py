# read from input.txt
global previousNode
global currentNode

symbol = set("; : , [ ] ( ) { } + - * <".split())
ws = {" ", "\n", "\r", "\t", "\v", "\f"}
ascii = set([chr(i) for i in range(128)])
digit = set([chr(i) for i in range(48, 58)])
letters = set([chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)])
sigma = symbol.union(ws, digit, letters, {"/", "="})


class Node:
    def __init__(self, name, dfaGraph, final=None):
        self.name = name
        self.edges = {}
        self.dfaGraph = dfaGraph
        self.final = final

    def addChildren(self, children):

        for child in children:

            edgeValue = child[1]
            childNum = child[0]
            splitValue = edgeValue.split("-")

            if len(splitValue) == 1:
                toConvert = None
                if splitValue[0] == "ws":
                    toConvert = ws
                elif splitValue[0] == "digit":
                    toConvert = digit
                elif splitValue[0] == "letter":
                    toConvert = letters
                if toConvert is None:
                    self.edges[edgeValue] = self.dfaGraph.Nodes[childNum]
                else:
                    for char in toConvert:
                        self.edges[char] = self.dfaGraph.Nodes[childNum]

            else:
                if splitValue[0] == "ascii":
                    allSet = ascii
                elif splitValue[0] == "sigma":
                    allSet = sigma
                else:
                    allSet = symbol
                for char in allSet.difference(set(splitValue[1:])):
                    self.edges[char] = self.dfaGraph.Nodes[childNum]

        if self.final is not None:
            for char in sigma.difference(set((self.edges.keys()))):
                self.edges[char] = self.dfaGraph.Nodes[0]

    def nextNode(self, edgeValue):
        return self.edges[edgeValue]


#
class DfaGraph:
    def __init__(self, NOState, extraStates):
        self.Nodes = {}
        for i in range(NOState):
            self.Nodes[i] = (Node(i, self))
        for extra in extraStates:
            self.Nodes[extra] = (Node(extra, self))

        self.currentNode = self.Nodes[0]
        self.previousNode = None

    def setFinals(self, finals):
        for nodeNum, name in finals:
            self.Nodes[nodeNum].final = name


dfaGraph = DfaGraph(12, ["invalid number", "invalid input", "unmatched comment", "unclosed comment"])
dfaGraph.setFinals([(1, "NUM"),
                    (2, "ID"),
                    (3, "SYMBOL"),
                    (4, "SYMBOL"),
                    (5, "ws"),
                    (6, "SYMBOL"),
                    (10, "comment"),
                    (11, "SYMBOL")
                    ])
dfaGraph.Nodes[0].addChildren([(1, "digit"),
                               (2, "letter"),
                               (3, "="),
                               (4, "symbol-*"),
                               (5, "ws"),
                               (6, "/"),
                               (11, "*")])
dfaGraph.Nodes[1].addChildren([(1, "digit"),
                               ("invalid number", "letter")])
dfaGraph.Nodes[2].addChildren([(2, "digit"),
                               (2, "letter")])
dfaGraph.Nodes[3].addChildren([(4, "=")])
dfaGraph.Nodes[4].addChildren([])
dfaGraph.Nodes[5].addChildren([(5, "ws")])
dfaGraph.Nodes[6].addChildren([(7, "/"),
                               (8, "*")])
dfaGraph.Nodes[7].addChildren([(7, "ascii-\n-EOF"),
                               (10, '\n'),
                               (10, 'EOF')])
dfaGraph.Nodes[8].addChildren([(8, "ascii-*-EOF"),
                               (9, "*"),
                               ("unclosed comment", "EOF")])
dfaGraph.Nodes[9].addChildren([(8, "ascii-/-*-EOF"),
                               (9, "*"),
                               (10, "/"),
                               ("unclosed comment", "EOF")])
dfaGraph.Nodes[10].addChildren([])
dfaGraph.Nodes[11].addChildren([("unmatched comment", "/")])
#
# for node in dfaGraph.Nodes.values():
#     print("node name:" + str(node.name))
#     for edge in node.edges:
#         print(edge)
# exit(0)
inputFile = open("input.txt", "rb")
symbol_dict = {
    "if": "KEYWORD",
    "else": "KEYWORD",
    "void": "KEYWORD",
    "int": "KEYWORD",
    "while": "KEYWORD",
    "break": "KEYWORD",
    "switch": "KEYWORD",
    "default": "KEYWORD",
    "case": "KEYWORD",
    "return": "KEYWORD",
    "endif": "KEYWORD",
}

symbolCount = 0
symbolFile = open("symbol_table.txt", "w")
for symbol in symbol_dict:
    symbolCount += 1
    symbolFile.write(str(symbolCount) + " " + symbol + "\n")


def get_next_token(dfaGraph: DfaGraph):
    token = ""
    reachedNewLine = False
    while True:
        char = inputFile.read(1).decode("ascii")
        if char == '':
            return (dfaGraph.previousNode.final, token), True, reachedNewLine
        if char == '\n':
            reachedNewLine = True
        dfaGraph.previousNode = dfaGraph.currentNode
        token += char
        dfaGraph.currentNode = dfaGraph.currentNode.nextNode(char)
        if dfaGraph.currentNode.name == dfaGraph.Nodes[0].name:
            inputFile.seek(-1, 1)
            return (dfaGraph.previousNode.final, token[:-1]), False, reachedNewLine
        else:
            pass


tokenFile = open("tokens.txt", "w")
while True:
    nextToken, finished, lastInLine = get_next_token(dfaGraph)
    nextToken = list(nextToken)
    if nextToken[0] == "ID":
        if nextToken[1] not in symbol_dict:
            symbol_dict[nextToken[1]] = "ID"
            symbolCount += 1
            symbolFile.write(str(symbolCount) + ' ' + nextToken[1] + '\n')

        nextToken[0] = symbol_dict[nextToken[1]]

    if finished:
        break
    if nextToken[0] != "ws" and nextToken[0] != "comment":
        tokenFile.write(str('(' + ','.join(nextToken) + ')') + ('\n' if lastInLine else ' '))
    # write function result to tokens.txt, each line has the line number and sequence of token pairs.

inputFile.close()
tokenFile.close()
