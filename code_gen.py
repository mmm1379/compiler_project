ss = []
PB = []
currentToken = ""


def i():
    return len(PB)


def push(x):
    ss.append(x)


def pop(times = 1):
    for _ in range(times):
        ss.pop()


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
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {i() + 1}, )"
    pop()
    pop()
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




def cod_gen(action_symbol, token):
    global currentToken
    currentToken = token
    if action_symbol.startswith("s_"):
        globals()[action_symbol[2:]]()
    else:
        globals()[action_symbol]()


def writePB():
    pass
