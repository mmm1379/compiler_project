import json
from scanner import get_next_token


class Node:
    def __init__(self, name, isLeaf=False):
        self.printName = name
        if isLeaf:
            self.name = name[2]
            if self.printName[0] == "$":
                self.printName = "$"
            else:
                self.printName = tuple(self.printName[:-1])
        else:
            self.name = name
        self.children = []
        self.isLeaf = isLeaf

    def getTuple(self):
        return self.name, self

    def addChild(self, child):
        self.children.append(child)

    def getPrintString(self, depth=0, terminateList=None, stringBuilder=[]):
        if terminateList is None:
            terminateList = []
        stringBuilder.append(str(self.printName) + "\n")
        for child in self.children.__reversed__():
            childTerminateList = terminateList.copy()
            for i in terminateList:
                if i:
                    stringBuilder.append("│")
                stringBuilder.append("\t")
            if child == self.children[0]:
                stringBuilder.append("└── ")
                childTerminateList.append(0)
            else:
                stringBuilder.append("├── ")
                childTerminateList.append(1)
            child.getPrintString(depth + 1, childTerminateList, stringBuilder)
        return ''.join(stringBuilder)


stack = ["0"]

# Opening JSON file
with open('grammar/table.json') as json_file:
    table = json.load(json_file)

parse_table = table['parse_table']
grammar = table['grammar']
reachedEnd = False
nextToken = (None, None)
while True:
    flag = False
    if nextToken[0] == "$":
        newParent.children = [stack[-2][1]] + newParent.children
        break
    nextToken = list(get_next_token())
    # if not reachedEnd:
    # if nextToken[0] == '$':
    #     reachedEnd = True
    # print(nextToken)
    # if nextToken == "EOF":
    #     break
    if nextToken[0] in ["KEYWORD", "SYMBOL"]:
        nextToken.append(nextToken[1])
    else:
        nextToken.append(nextToken[0])

    while not flag:
        ptResult = parse_table[stack[-1][0]][nextToken[2]].split('_')
        if ptResult[0] == "shift":
            stack.append(Node(nextToken, isLeaf=True).getTuple())
            stack.append(Node(ptResult[1]).getTuple())
        elif ptResult[0] == "reduce":
            nextGrammar = grammar[ptResult[1]]
            if "epsilon" in nextGrammar:
                epsNode = Node(nextGrammar[0])
                epsNode.addChild(Node("epsilon"))
                stack.append(epsNode.getTuple())
            else:
                toPop = 2 * (len(nextGrammar) - 2)
                popList = stack[-toPop:]
                newParent = Node(nextGrammar[0])
                for i in range(len(popList) - 2, -1, -2):
                    newParent.addChild(popList[i][1])
                stack[-toPop:] = [(nextGrammar[0], newParent)]
            ptResult = parse_table[stack[-2][0]][stack[-1][0]].split('_')
            # todo: find goto in table.json
        flag = True
        if ptResult[0] == "goto":
            stack.append(Node(ptResult[1]).getTuple())
            flag = False


def writeToParseTreeFile():
    text_file = open("parse_tree.txt", "w")
    n = text_file.write(newParent.getPrintString())
    text_file.close()

writeToParseTreeFile()