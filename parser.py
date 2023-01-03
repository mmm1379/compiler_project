import json
from scanner import get_next_token

stack = ["0"]

# Opening JSON file
with open('grammar/table.json') as json_file:
    table = json.load(json_file)

parse_table = table['parse_table']
grammar = table['grammar']

while True:
    nextToken = get_next_token()
    print(nextToken)
    if nextToken == "EOF":
        break
    if nextToken[0] == "KEYWORD":
        nextToken[0] = nextToken[1]
    ptResult = parse_table[stack[-1]][nextToken[0]].split('_')
    if ptResult[0] == "shift":
        stack.append(nextToken[0])
        stack.append(ptResult[1])
    elif ptResult[0] == "reduce":
        nextGrammar = grammar[ptResult[1]]
        toPop = 2 * (len(nextGrammar) - 2)
        stack[-toPop:] = [nextGrammar[0]]
        ptResult = parse_table[stack[-2]][stack[-1]].split('_')
        # todo: find goto in table.json
    if ptResult[0] == "goto":
        stack.append(ptResult[1])
