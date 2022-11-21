# read from input.txt
class Node:
    def __init__(self, number, dfaGraph):
        self.number = number
        self.edges = {}

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


#

dfaGraph = DfaGraph(30)
dfaGraph.Nodes[0].addChildren([(1, "digit"),
                              (3, "letter"),
                              (5, "+"),
                              (6, "-"),
                              (7, "*"),
                              (8, "/"),
                              (9, "<"),
                              (10, "="),
                              (13, ":"),
                              (14, ";"),
                              (15, ","),
                              (16, "("),
                              (17, "),"),
                              (18, "["),
                              (19, "]"),
                              (20, "{"),
                              (21, "}"),
                              (29, "space")
])
inputFile = open("input.txt", "r")
symbol_dict = {}

with open("symbol_table.txt", "r+") as symbolFile:
    for line in symbolFile:
        tuple = line.split()
        symbol_dict[int(tuple[0])] = tuple[1]


def get_next_token():
    char = inputFile.read(1)

    pass
    # read next token and return pair(Token_type, Token_string)
    # do this char by char


while True:
    get_next_token()
    # write function result to tokens.txt, each line has the line number and sequence of token pairs.

inputFile.close()
