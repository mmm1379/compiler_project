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

    def setChildren(self, children):
        if self.name not in [7, 8, 9]:
            children.append(("Invalid input", "ascii-sigma-EOF"))
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
                for char in splitValue[1:]:
                    if char == "sigma":
                        char = sigma
                    allSet = allSet.difference(char)

                for char in allSet:
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


dfaGraph = DfaGraph(12, ["Invalid number", "Invalid input", "Unmatched comment", "Unclosed comment"])
dfaGraph.setFinals([(1, "NUM"),
                    (2, "ID"),
                    (3, "SYMBOL"),
                    (4, "SYMBOL"),
                    (5, "ws"),
                    (6, "SYMBOL"),
                    (10, "comment"),
                    (11, "SYMBOL"),
                    ("Invalid number", "Invalid number"),
                    ("Invalid input", "Invalid input"),
                    ("Unclosed comment", "Unclosed comment"),
                    ("Unmatched comment", "Unmatched comment")
                    ])
dfaGraph.Nodes[0].setChildren([(1, "digit"),
                               (2, "letter"),
                               (3, "="),
                               (4, "symbol-*"),
                               (5, "ws"),
                               (6, "/"),
                               (11, "*"),
                               (0, 'EOF')])
dfaGraph.Nodes[1].setChildren([(1, "digit"),
                               ("Invalid number", "letter"),
                               (1, 'EOF')])
dfaGraph.Nodes["Invalid number"].setChildren([("Invalid number", "letter"),
                                              (0, "sigma-letter"),
                                              ("Invalid number", 'EOF')])
dfaGraph.Nodes[2].setChildren([(2, "digit"),
                               (2, "letter"),
                               (2, 'EOF')])
dfaGraph.Nodes[3].setChildren([(4, "="),
                               (3, 'EOF')])
dfaGraph.Nodes[4].setChildren([(4, 'EOF')])
dfaGraph.Nodes[5].setChildren([(5, "ws"),
                               (5, 'EOF')])
dfaGraph.Nodes[6].setChildren([(7, "/"),
                               (8, "*"),
                               (6, 'EOF')])
dfaGraph.Nodes[7].setChildren([(7, "ascii-\n-EOF"),
                               (10, '\n'),
                               (10, 'EOF')])
dfaGraph.Nodes[8].setChildren([(8, "ascii-*-EOF"),
                               (9, "*"),
                               ("Unclosed comment", "EOF")])
dfaGraph.Nodes[9].setChildren([(8, "ascii-/-*-EOF"),
                               (9, "*"),
                               (10, "/"),
                               ("Unclosed comment", "EOF")])
dfaGraph.Nodes[10].setChildren([(10, 'EOF')])
dfaGraph.Nodes[11].setChildren([("Unmatched comment", "/"),
                                (11, 'EOF')])
dfaGraph.Nodes["Unmatched comment"].setChildren([(0, "sigma"),
                                                 ("Unmatched comment", 'EOF')])
dfaGraph.Nodes["Unclosed comment"].setChildren([(0, "ascii")])
dfaGraph.Nodes["Invalid input"].setChildren([])
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
            char = "EOF"
            # dfaGraph.previousNode = dfaGraph.currentNode
            dfaGraph.currentNode = dfaGraph.currentNode.nextNode(char)
            return (dfaGraph.currentNode.final, token), True, reachedNewLine
        if char == '\n':
            # fix for os
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
lexicalErrorsFile = open("lexical_errors.txt", "w")
lineNumber = 1
hasLexicalError = False
while True:
    nextToken, finished, lastInLine = get_next_token(dfaGraph)
    if '\n' in nextToken[1]:
        lineNumber += 1
    nextToken = list(nextToken)
    if nextToken[0] == "ID":
        if nextToken[1] not in symbol_dict:
            symbol_dict[nextToken[1]] = "ID"
            symbolCount += 1
            symbolFile.write(str(symbolCount) + ' ' + nextToken[1] + '\n')

        nextToken[0] = symbol_dict[nextToken[1]]

    if nextToken[0] == "Unclosed comment" or nextToken[0] == "Invalid number" or \
            nextToken[0] == "Invalid input" or nextToken[0] == "Unmatched comment":
        hasLexicalError = True
        newLineNumber = lineNumber
        if nextToken[0] == "Unclosed comment":
            newLineNumber -= nextToken[1].count('\n')
            nextToken[1] = nextToken[1][0:7] + "..."
        lexicalErrorsFile.write(str(newLineNumber) + ' (' + nextToken[1].strip() + ', ' + nextToken[0] + ')\n')
    elif nextToken[0] != "ws" and nextToken[0] != "comment":
        # if
        tokenFile.write(str('(' + ', '.join(nextToken) + ')') + ('\n' if lastInLine else ' '))

    if finished:
        if not hasLexicalError:
            lexicalErrorsFile.write("There is no lexical error.")
        break
    # write function result to tokens.txt, each line has the line number and sequence of token pairs.

inputFile.close()
tokenFile.close()
lexicalErrorsFile.close()
