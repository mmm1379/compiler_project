class Row:
    def __init__(self, address, lexeme, function, length, type, scope):
        self.address = address
        self.lexeme = lexeme
        self.function = function
        self.length = length
        self.type = type
        self.scope = scope
        if self.function:
            self.returnAddress = getLastVarAddressAndUpdate()
            args = []
            for i in range(length):
                args.append(ss[-1])
                pop()
            self.args = args[::-1]


ss = []
PB = [""]
currentToken = ""
currentNode = None
scope = 0
symbol_table = {"output": Row(0,0,0,0,0,0)}
lastVarAddress = 0
lastTempAddress = 0


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


def getParamsNonRecursive(node, ps):
    if node.actualName != "param_list":
        return
    ps.append(node.children[0])
    if len(node.children) != 1:
        getParamsNonRecursive(node.children[2], ps)


def fun_declaration():
    lexeme = currentNode.children[-2].actualName[1]
    address = ss[-1]
    if lexeme == 'main' and not scope:
        PB[0] = f"(JP, {address}, , )"
    pop()
    params = currentNode.children[-4].children
    if params[0].name == 'void':
        paramLen = 0
    else:
        ps = []
        getParamsNonRecursive(params[0], ps)
        params = ps
        paramLen = len(params)

    symbol_table[lexeme] = Row(address, lexeme, True, paramLen, "func", scope)

    if lexeme == 'main' and not scope:
        return
    PB.append(f"(JP, @{symbol_table[lexeme].returnAddress}, , )")


def param():
    lexeme = currentNode.children[-2].actualName[1]
    address = getLastVarAddressAndUpdate()
    if currentNode.children[0].name == "s_atomic_param_declaration":
        row = Row(address, lexeme, False, 0, "int", scope + 1)
    else:
        row = Row(address, lexeme, False, -1, "array", scope + 1)
    push(address)
    symbol_table[lexeme] = row


def PID():
    push(findAddress(currentToken))


def Assign():
    PB.append(f"(ASSIGN, {ss[-1]}, {ss[-2]}, )")
    pop()


def save():
    push(i())
    PB.append("")


def switch_save():
    save()
    save()


def jmp_to_expr():
    PB[ss[-2]] = f"(JP, {i()}, , )"


def switch_jf():
    t = getLastVarAddressAndUpdate()
    PB.append(f"(EQ, #{int(currentToken)}, {ss[-1]}, {t})")
    save()
    push(t)


def case_stmt():
    PB[ss[-2]] = f"(JPF, {ss[-1]}, {i() + 1}, )"
    pop(2)
    PB.append(f"(JP, {ss[-2]}, , )")


def switch_stmt():
    pop()
    PB[ss[-1]] = f"(JP, {i()})"
    pop(2)


def jpf():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i()}, )"
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


def pop_stack():
    pop()


def iteration_stmt():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    PB.append(f"(JP, {ss[-3]}, , )")
    pop(3)


def call():
    fName = currentNode.children[-2].actualName[1]
    if fName == "output":
        PB.append(f"(PRINT, {ss[-1]}, , )")
        pop()
        return
    fRow = symbol_table[fName]
    address = fRow.address
    for j, arg in enumerate(fRow.args[::-1]):
        PB.append(f"(ASSIGN, {ss[-(j + 1)]}, {arg}, )")
    pop(len(fRow.args))
    PB.append(f"(ASSIGN, #{i() + 2}, {fRow.returnAddress}, )")
    PB.append(f"(JP, {address}, , )")
    # push(i())


def push_num():
    push(f"#{int(currentToken)}")


def additive_expression():
    if len(currentNode.children) == 3:
        operation = currentNode.children[1].children[0].actualName[1]
        t = getLastVarAddressAndUpdate()
        if operation == '+':
            PB.append(f"(ADD, {ss[-2]}, {ss[-1]}, {t})")
        if operation == '-':
            PB.append(f"(SUB, {ss[-2]}, {ss[-1]}, {t})")
        pop(2)
        push(t)


def term():
    if len(currentNode.children) == 3:
        operation = currentNode.children[1].children[0].actualName[1]
        t = getLastVarAddressAndUpdate()
        if operation == '*':
            PB.append(f"(MULT, {ss[-2]}, {ss[-1]}, {t})")
        if operation == '/':
            PB.append(f"(DIV, {ss[-2]}, {ss[-1]}, {t})")
        pop(2)
        push(t)


def simple_expression():
    if len(currentNode.children) == 3:
        operation = currentNode.children[1].children[0].actualName[1]
        t = getLastVarAddressAndUpdate()
        if operation == '<':
            PB.append(f"(LT, {ss[-2]}, {ss[-1]}, {t})")
        if operation == '==':
            PB.append(f"(EQ, {ss[-2]}, {ss[-1]}, {t})")
        pop(2)
        push(t)


def array_select():
    t1 = getLastVarAddressAndUpdate()
    t2 = getLastVarAddressAndUpdate()
    PB.append(f"(MULT, {ss[-1]}, #4, {t2})")
    PB.append(f"(ADD, {ss[-2]}, {t2}, {t1})")
    pop(2)
    push(f"@{t1}")


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
    text_file = open("output.txt", "w")
    for i, x in enumerate(PB):
        print(f"{i}\t{x}")
        text_file.write(f"{i}\t{x}\n")
    text_file.close()
