ss = []
PB = []
currentToken = ""


def findAddress(token):
    pass


def PID():
    ss.append(findAddress(currentToken))


def Assign():
    PB.append(f"(ASSIGN, {ss[-1]}, {ss[-2]})")
    ss.pop()


def save():
    ss.append(len(PB))
    PB.append("")


def jpf():
    PB[ss[-1]] = f"(JPF, {ss[-2]}, {len(PB)}, "
    ss.pop()
    ss.pop()


def jpf_save():
    pass


def jp():
    pass


def cod_gen(action_symbol, token):
    global currentToken
    currentToken = token
    globals()[action_symbol[2:]]()


def writePB():
    pass
