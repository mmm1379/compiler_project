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
                self.printName = "(" + self.printName[0] + ", " + self.printName[1] + ")"
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
follows = table['follow']
reachedEnd = False
nextToken = (None, None)

syntaxErrorFile = open("syntax_errors.txt", "w")

hasSyntaxError = False


def writeSyntaxError(error, lineNo=None):
    global hasSyntaxError
    hasSyntaxError = True
    printable_line_number = ""
    if lineNo is not None:
        printable_line_number = f"#{lineNo} : "
    syntaxErrorFile.write(printable_line_number + error + "\n")


while True:
    flag = False
    if nextToken[0] == "$":
        newParent.children = [stack[-2][1]] + newParent.children
        break
    nextTokenDict = get_next_token()
    lineNumber = nextTokenDict["lineNumber"]
    nextToken = list(nextTokenDict["nextToken"])
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
        if nextToken[2] not in parse_table[stack[-1][0]]:
            writeSyntaxError(f"syntax error , illegal {nextToken[2]}", lineNumber)
            nextTokenDict = get_next_token()
            lineNumber = nextTokenDict["lineNumber"]
            nextToken = list(nextTokenDict["nextToken"])
            if nextToken[0] in ["KEYWORD", "SYMBOL"]:
                nextToken.append(nextToken[1])
            else:
                nextToken.append(nextToken[0])
            flag2 = False
            while True:
                non_state, state = stack[-2], stack[-1][0]
                for non_terminal, op in parse_table[state].items():
                    non_state, state = stack[-2], stack[-1][0]
                    if op.startswith("goto"):

                        while nextToken[0] not in follows[non_terminal]:
                            if nextToken[0] == "$":
                                writeSyntaxError("syntax error , Unexpected EOF", lineNumber)
                                exit(0)
                            else:
                                writeSyntaxError(f"syntax error , discarded {nextToken[1]} from input", lineNumber)
                            nextTokenDict = get_next_token()
                            lineNumber = nextTokenDict["lineNumber"]
                            nextToken = list(nextTokenDict["nextToken"])
                            if nextToken[0] in ["KEYWORD", "SYMBOL"]:
                                nextToken.append(nextToken[1])
                            else:
                                nextToken.append(nextToken[0])
                        flag2 = True
                        break

                if flag2:
                    stack.append((non_terminal, Node(non_terminal)))
                    stack.append((op.split('_')[1], Node(op.split('_')[1])))
                    break
                else:
                    stack.pop()
                    stack.pop()
                    writeSyntaxError(f"syntax error , discarded {non_state[1].printName} from stack")
            writeSyntaxError(f"syntax error , missing {non_terminal}", lineNumber)

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
    n = text_file.write(newParent.getPrintString().strip())
    text_file.close()

if not hasSyntaxError:
    syntaxErrorFile.write("There is no syntax error.")
writeToParseTreeFile()
