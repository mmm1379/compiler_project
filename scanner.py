# read from input.txt
# Mohammad Mahdi Masoudpour-98102335
# Sajad Paksima-98106286
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
        if self.name in [4, 5, 10, 11, "Unmatched comment"]:
            children.append((0, "ascii-sigma-EOF"))
        if self.name in [1, 2, 3, 6]:
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
                elif splitValue[0] == "ascii":
                    toConvert = ascii
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
                               (0, 'EOF'),
                               ("Invalid input", "ascii-sigma-EOF")])
dfaGraph.Nodes[1].setChildren([(1, "digit"),
                               ("Invalid number", "letter"),
                               (1, 'EOF')])
dfaGraph.Nodes[2].setChildren([(2, "digit"),
                               (2, "letter"),
                               (2, 'EOF')])
dfaGraph.Nodes[3].setChildren([(4, "="),
                               ("Invalid input", "ascii-sigma-EOF"),
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
dfaGraph.Nodes["Invalid number"].setChildren([(0, "ascii-letter"),
                                              ("Invalid number", 'EOF')])
dfaGraph.Nodes["Unmatched comment"].setChildren([(0, "sigma"),
                                                 ("Unmatched comment", 'EOF')])
dfaGraph.Nodes["Unclosed comment"].setChildren([(0, "ascii")])
dfaGraph.Nodes["Invalid input"].setChildren([(0, "ascii")])
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
    symbolFile.write(str(symbolCount) + ".\t" + symbol + "\n")


def get_next_token_old(dfaGraph: DfaGraph):
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
lexicalErrorsFile = open("p2_testcases/T07/lexical_errors.txt", "w")
lineNumber = 1
hasLexicalError = False
lastLexicalLineNumber = None
lastTokenLineNumber = None
finished = False


def scannerFinished():
    tokenFile.write('\n')

    if not hasLexicalError:
        lexicalErrorsFile.write("There is no lexical error.")
    inputFile.close()
    tokenFile.close()
    lexicalErrorsFile.close()
    return {"nextToken": ("$", "EOF"), "lineNumber": lineNumber}


def get_next_token():
    global lineNumber, symbolCount, lastTokenLineNumber, lastLexicalLineNumber, hasLexicalError, finished
    if finished:
        return scannerFinished()
    nextToken, finished, lastInLine = get_next_token_old(dfaGraph)
    if '\n' in nextToken[1]:
        lineNumber += nextToken[1].count('\n')
    nextToken = list(nextToken)
    if nextToken[0] == "ID":
        if nextToken[1] not in symbol_dict:
            symbol_dict[nextToken[1]] = "ID"
            symbolCount += 1
            symbolFile.write(str(symbolCount) + '.\t' + nextToken[1] + '\n')

        nextToken[0] = symbol_dict[nextToken[1]]

    if nextToken[0] == "Unclosed comment" or nextToken[0] == "Invalid number" or \
            nextToken[0] == "Invalid input" or nextToken[0] == "Unmatched comment":
        hasLexicalError = True

        newLineNumber = lineNumber
        if nextToken[0] == "Unclosed comment":
            newLineNumber -= nextToken[1].count('\n')
            nextToken[1] = nextToken[1][0:7] + "..." if len(nextToken[1]) > 7 else ""
        if lastLexicalLineNumber == newLineNumber:
            lexicalErrorsFile.write('(' + (nextToken[1].strip() + ', ' + nextToken[0]) + ') ')
        else:
            if lastLexicalLineNumber is not None:
                lexicalErrorsFile.write('\n')
            lexicalErrorsFile.write(str(newLineNumber) + '.\t(' + nextToken[1].strip() + ', ' + nextToken[0] + ') ')
            lastLexicalLineNumber = newLineNumber
    elif nextToken[0] != "ws" and nextToken[0] != "comment":
        # if
        if lastTokenLineNumber == lineNumber:
            tokenFile.write(str('(' + ', '.join(nextToken) + ')') + ' ')
        else:
            if lastTokenLineNumber is not None:
                tokenFile.write('\n')
            tokenFile.write(str(lineNumber) + '.\t(' + ', '.join(nextToken) + ')' + ' ')
            lastTokenLineNumber = lineNumber
        return {"nextToken": nextToken, "lineNumber": lineNumber}
    if finished:
        return scannerFinished()
    return get_next_token()
    # write function result to tokens.txt, each line has the line number and sequence of token pairs.
