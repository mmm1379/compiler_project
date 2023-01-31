ss = []
PB = []
currentToken = ""
currentNode = None
scope = 0
symbol_table = {}
lastVarAddress = 0
lastTempAddress = 0


class Row:
    def __init__(self, address, lexeme, function, length, type, scope):
        self.address = address
        self.lexeme = lexeme
        self.function = function
        self.length = length
        self.type = type
        self.scope = scope


def getLastVarAddressAndUpdate():
    global lastVarAddress
    lastVarAddress += 4
    return lastVarAddress - 4


def scopeIntro():
    global scope
    scope += 1
    pass


def scopeOutro():
    global scope
    scope -= 1
    pass


def i():
    return len(PB)


def push(x):
    ss.append(x)


def pop(times=1):
    for _ in range(times):
        ss.pop()


def findAddress(token):
    pass


def var_declaration():
    address = getLastVarAddressAndUpdate()
    lexeme = currentNode.children[-3].actualName[1]
    if currentNode.children[0].name == "s_atomic_var_declaration":
        row = Row(address, lexeme, False, 0, "int", scope)
    else:
        length = int(currentNode.children[-5].actualName[1])
        row = Row(address, lexeme, False, length, "array", scope)
    symbol_table[lexeme] = row


def fun_declaration():
    print(currentNode)


def atomic_var_declaration():
    print(currentNode)


def array_declaration():
    print(currentNode)


def PID():
    push(findAddress(currentToken))


def Assign():
    PB.append(f"(ASSIGN, {ss[-1]}, {ss[-2]})")
    pop()


def save():
    push(i())
    PB.append("")


def jpf():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i()}, "
    pop(2)


def jpf_save():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    pop(2)
    push(i() - 1)


def jp():
    PB[ss[-1]] = f"(JP, {i()}, , )"
    pop()


def label():
    push(i())


def iteration_stmt():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    PB[i()] = f"(JP, {ss[-3]}, , )"
    pop(3)


def cod_gen(node, token):
    global currentToken, currentNode
    currentToken = token
    currentNode = node
    action_symbol = node.name
    if action_symbol.startswith("s_"):
        globals()[action_symbol[2:]]()
    elif action_symbol in globals():
        globals()[action_symbol]()


def writePB():
    pass
