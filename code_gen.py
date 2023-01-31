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


def getLastVarAddressAndUpdate(newVarLength=1):
    global lastVarAddress
    temp = lastVarAddress
    lastVarAddress += 4 * newVarLength
    return temp


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
    return symbol_table[token].address


def var_declaration():
    lexeme = currentNode.children[-2].actualName[1]
    if currentNode.children[0].name == "s_atomic_var_declaration":
        address = getLastVarAddressAndUpdate()
        row = Row(address, lexeme, False, 0, "int", scope)
    else:
        length = int(currentNode.children[-4].actualName[1])
        address = getLastVarAddressAndUpdate(length)
        row = Row(address, lexeme, False, length, "array", scope)
    symbol_table[lexeme] = row


def fun_declaration():
    lexeme = currentNode.children[-2].actualName[1]
    address = ss[-1]
    pop()
    params = currentNode.children[-4].children
    if params[0].name == 'void':
        paramLen = 0
    else:
        paramLen = len(params)

    symbol_table[lexeme] = Row(address, lexeme, True, paramLen, "func", scope)


def param():
    lexeme = currentNode.children[-2].actualName[1]
    if currentNode.children[0].name == "s_atomic_param_declaration":
        address = getLastVarAddressAndUpdate()
        row = Row(address, lexeme, False, 0, "int", scope + 1)
    else:
        row = Row(-1, lexeme, False, -1, "array", scope + 1)
    symbol_table[lexeme] = row


def save_address():
    push(i())
    PB.append("")


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


# def var():
#     push(findAddress(currentNode.children[-2].actualName[1]))


def push_num():
    push(f"#{int(currentToken)}")


def cod_gen(node, token):
    global currentToken, currentNode
    currentToken = token[1]
    currentNode = node
    action_symbol = node.name
    func_name = action_symbol
    if action_symbol.startswith("s_"):
        func_name = action_symbol[2:]
    if func_name in globals():
        globals()[func_name]()


def writePB():
    for i in PB:
        print(i)
