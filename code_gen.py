class Row:
    def __init__(self, address, lexeme, function, length, type, scope, returnValue=None, returnType= None):
        self.address = address
        self.lexeme = lexeme
        self.function = function
        self.length = length
        self.type = type
        self.scope = scope
        self.args = []
        if self.function:
            self.returnType = returnType
            self.returnValue = returnValue
            self.returnAddress = getLastVarAddressAndUpdate()
            args = []
            for i in range(length):
                args.append(findRowByAddress(ss[-1]))
                pop()
            self.args = args[::-1]


ss = []
PB = [""]
currentToken = ""
currentNode = None
lineNumber = 0
scope = 0
symbol_table = {"output": Row(-1, 0, 0, 0, 0, 0)}
lastVarAddress = 0
lastTempAddress = 0
returnValueAddress = None

scopeStack = []

hasSemanticError = False
semanticErrorFile = open("semantic_errors.txt", "w")


def getLastVarAddressAndUpdate(newVarLength=1):
    global lastVarAddress
    temp = lastVarAddress
    lastVarAddress += 4 * newVarLength
    return temp


def scopeIntro():
    global scope
    scope += 1


def scopeOutro():
    global scope
    scope -= 1


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
    returnType = currentNode.children[-1].children[0].actualName[1]
    lexeme = currentNode.children[-2].actualName[1]
    address = ss[-1]
    if lexeme == 'main' and not scope:
        PB[0] = f"(JP, {address}, , )"
    pop()
    params = currentNode.children[-5].children
    if len(params) == 0:
        pass
    if params[0].name == 'void':
        paramLen = 0
    else:
        ps = []
        getParamsNonRecursive(params[0], ps)
        params = ps
        paramLen = len(params)

    symbol_table[lexeme] = Row(address, lexeme, True, paramLen, "func", scope, returnValue=returnValueAddress, returnType = returnType)

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
    scopeStack.append(i() + 1)
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
    PB[ss[-2]] = f"(JPF, {ss[-1]}, {i()}, )"
    pop(2)


def switch_stmt():
    scopeStack.pop()
    pop()
    PB[ss[-1]] = f"(JP, {i()})"
    pop(2)


def push_scope_stack():
    scopeStack.append("breakStmt")


def jpf():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i()}, )"
    pop(2)


def jpf_save():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    pop(2)
    # todo check
    # push(i() - 1)
    push(i())
    PB.append("")


def jp():
    PB[ss[-1]] = f"(JP, {i()}, , )"
    pop()


def label():
    push(i())


def pop_stack():
    pop()


def iteration_stmt():
    scopeStack.pop()
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    PB.append(f"(JP, {ss[-3]}, , )")
    pop(3)
    PB[ss[-1]] = f"(JP, {i()}, , )"
    pop(2)


def break_out():
    PB.append(f"(JP, {scopeStack[-1]}, , )")


def call():
    fName = currentNode.children[-2].actualName[1]
    if fName == "output":
        PB.append(f"(PRINT, {ss[-1]}, , )")
        pop()
        return

    fRow = symbol_table[fName]
    address = fRow.address
    for j, arg in enumerate(fRow.args[::-1]):
        PB.append(f"(ASSIGN, {ss[-(j + 1)]}, {arg.address}, )")
    pop(len(fRow.args))
    PB.append(f"(ASSIGN, #{i() + 2}, {fRow.returnAddress}, )")
    PB.append(f"(JP, {address}, , )")
    pop()
    t = getLastVarAddressAndUpdate()
    PB.append(f"(ASSIGN, {fRow.returnValue}, {t}, )")
    push(t)


def set_return_value_address():
    global returnValueAddress
    returnValueAddress = getLastVarAddressAndUpdate()


def return_expression():
    PB.append(f"(ASSIGN, {ss[-1]}, {returnValueAddress})")
    pop()


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
    PB.append(f"(ADD, #{ss[-2]}, {t2}, {t1})")
    pop(2)
    push(f"@{t1}")


def cod_gen(node, token, lN):
    global currentToken, currentNode, lineNumber
    currentToken = token[1]
    currentNode = node
    lineNumber = lN
    action_symbol = node.name
    func_name = action_symbol
    if action_symbol.startswith("s_"):
        func_name = action_symbol[2:]
    if func_name in globals():
        checkInputForErrors(func_name)
        globals()[func_name]()


def checkInputForErrors(func_name):
    result = True
    if func_name in ["call", "PID"]:
        result &= checkScopingError(func_name)
    if result and func_name == "var_declaration":
        result &= checkDeclarationNotVoid()
    if result and func_name == "call":
        result &= checkFunctionParameters()
    if result and func_name == "check_break":
        result &= checkCorrectBreak()
    if result and func_name in ["simple_expression", "additive_expression", "term"]:
        result &= checkTypeEquals()


def checkScopingError(func_name):
    if func_name == "call":
        symbolName = currentNode.children[-2].actualName[1]
    else:
        symbolName = currentToken

    if symbolName not in symbol_table:
        writeSemanticError(f"'{symbolName}' is not defined")
        return False
    return True


def checkDeclarationNotVoid():
    typeSpecifier = currentNode.children[-1].children[0].actualName[1]
    lexeme = currentNode.children[-2].actualName[1]
    if typeSpecifier == "void":
        writeSemanticError(f"'Illegal type of void for '{lexeme}'")
        return False
    return True


def checkFunctionParameters():
    fName = currentNode.children[-2].actualName[1]
    if fName == "output":
        return True
    fRow = symbol_table[fName]
    argsNode = currentNode.children[-4]
    argList = []
    if argsNode.children[0].actualName != "epsilon":
        pass
    tempNode = argsNode.children[0]
    while tempNode.actualName == "arg_list":
        argList.append(tempNode.children[0])
        tempNode = tempNode.children[-1]
    result = checkParamLenMatch(argList, fRow)
    result &= checkParamTypeMatch(argList, fRow)
    return result


def checkParamLenMatch(argList, fRow):
    if len(argList) != len(fRow.args):
        writeSemanticError(f"Mismatch in numbers of arguments of '{fRow.lexeme}'")
        return False
    return True


def findRowByAddress(address):
    for row in symbol_table.values():
        if row.address == address:
            return row
    return None


def checkParamTypeMatch(argList, fRow):
    returnValue = True
    for i, arg in enumerate(argList[::-1]):
        trueFuncArgType = fRow.args[i].type
        if '#' in str(ss[-(len(argList) - i)]):
            t = "int"
        else:
            argRow = findRowByAddress(ss[-(len(argList) - i)])
            t = argRow.type
        if t != trueFuncArgType:
            writeSemanticError(f"Mismatch in type of argument {i + 1} of '{fRow.lexeme}'. Expected '{trueFuncArgType}' "
                               f"but got '{argRow.type}' instead")
            returnValue = False
    return returnValue


def checkCorrectBreak():
    if not len(scopeStack):
        writeSemanticError("No 'while' or 'switch case' found for 'break'")
        return False
    return True


def checkTypeEquals():
    if len(currentNode.children) != 3:
        return True

    def findChildFactor(node):
        if node.actualName == "factor":
            return node
        return findChildFactor(node.children[0])

    def getType(factor):
        def getVarType(var):
            if len(var.children) == 2:
                lexeme = var.children[0].actualName[1]
                return symbol_table[lexeme].type
            else:
                return "int"

        def getCallType(call):
            return symbol_table[call.children[-2].actualName[1]].returnType

        def getExpressionType(expression):
            if len(expression.children) == 4:
                return getVarType(expression.children[-1])
            else:
                return getType(findChildFactor(expression.children[0]))

        if len(factor.children) == 1:
            if factor.children[0].actualName == "var":
                return getVarType(factor.children[0])
            else:
                return getCallType(factor.children[0])
        elif len(factor.children) == 2:
            return "int"
        else:
            return getExpressionType(factor.children[1])

    type1 = getType(findChildFactor(currentNode.children[0]))
    type2 = getType(findChildFactor(currentNode.children[2]))

    if type1 != type2:
        writeSemanticError(f"Type mismatch in operands, Got {type2} instead of {type1}")
        return False
    return True


def writeSemanticError(toWrite):
    semanticErrorFile.write(f"# {lineNumber} : Semantic Error! {toWrite}.\n")
    global hasSemanticError
    hasSemanticError = True


def finishSemantic():
    checkIfFileContainedErrors()
    semanticErrorFile.close()
    writePB()


def checkIfFileContainedErrors():
    if not hasSemanticError:
        semanticErrorFile.write("The input program is semantically correct.")


def writePB():
    text_file = open("output.txt", "w")
    if hasSemanticError:
        text_file.write(f"The output code has not been generated")
    else:
        for i, x in enumerate(PB):
            # print(f"{i}\t{x}")
            text_file.write(f"{i}\t{x}\n")
    text_file.close()
