%token NUM
%token ID
%start program
%%
program: declaration_list
;
declaration_list: declaration_list declaration
| declaration
;
declaration: var_declaration 
| fun_declaration 
;
var_declaration: type_specifier s_PID ID ';'
| type_specifier s_PID ID '[' NUM ']' ';'
;
type_specifier: "int" 
| "void"
;
fun_declaration: type_specifier s_PID ID '(' params ')' compound_stmt
;
params: param_list
| "void"
;
param_list: param_list ',' param
| param
;
param: type_specifier s_PID ID
| type_specifier s_PID ID '[' ']'
;
compound_stmt: '{' local_declarations statement_list '}'
;
local_declarations: local_declarations var_declaration
| /* epsilon */
;
statement_list: statement_list statement
| /* epsilon */
;
statement: expression_stmt
| compound_stmt
| selection_stmt
| iteration_stmt
| return_stmt
| switch_stmt
;
expression_stmt: expression ';'
| "break" ';'
| ';'
;
selection_stmt: "if" '(' expression ')' s_save statement s_jpf "endif"
| "if" '(' expression ')' s_save statement "else" s_jpf_save statement s_jp "endif"
;
iteration_stmt: "while" s_label '(' expression ')' s_save statement
;
return_stmt: "return" ';'
| "return" expression ';'
;
switch_stmt: s_save s_save "switch" '(' s_jmp_to_expr expression ')' '{' case_stmts default_stmt '}'
;
case_stmts: case_stmts case_stmt
| /* epsilon */
;
case_stmt: "case" NUM s_switch_jf ':' statement_list
;
default_stmt: "default" ':' statement_list
| /* epsilon */
;
expression: var '=' expression s_Assign
| simple_expression
;
var: s_PID ID
| s_PID ID '[' expression ']'
;
simple_expression: additive_expression relop additive_expression
| additive_expression
;
relop: '<'
| "=="
;
additive_expression: additive_expression addop term
| term
;
addop: '+'
| '-'
;
term: term mulop factor
| factor
;
mulop: '*'
| '/'
;
factor: '(' expression ')'
| var
| call
| NUM
;
call: s_PID ID '(' args ')'
;
args: arg_list
| /* epsilon */
;
arg_list: arg_list ',' expression
| expression
;
s_PID : /* epsilon */
;
s_Assign : /* epsilon */
;
s_Save : /* epsilon */
;
s_jpf : /* epsilon */
;
s_jpf_save : /* epsilon */
;
s_jp : /* epsilon */
;
s_label : /* epsilon */
;
s_save : /* epsilon */
;
s_jmp_to_expr : /* epsilon */
;
s_switch_jf : /* epsilon */
;
%%
