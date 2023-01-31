ss = []
PB = []
currentToken = ""


def i():
    return len(PB)


def push(x):
    ss.append(x)


def pop():
    return ss.pop()


def findAddress(token):
    pass


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
    pop()
    pop()


def jpf_save():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, "
    pop()
    pop()
    push(i() - 1)


def jp():
    PB[ss[-1]] = f"JP, {i()}, , "
    pop()


def label():
    push(i())


def label():
    ss.append(len(PB))


def cod_gen(action_symbol, token):
    global currentToken
    currentToken = token
    globals()[action_symbol[2:]]()


def writePB():
    pass
