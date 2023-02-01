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
var_declaration: type_specifier ID ';' s_atomic_var_declaration
| type_specifier ID '[' NUM ']' ';' s_array_declaration
;
type_specifier: "int"
| "void"
;
fun_declaration: type_specifier ID '(' params ')' s_label compound_stmt
;

params: param_list
| "void"
;
param_list: param_list ',' param
| param
;
param: type_specifier ID s_atomic_param_declaration
| type_specifier ID '[' ']' s_array_param_declaration
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
expression_stmt: expression ';' s_pop_stack
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
switch_stmt: s_switch_save "switch" '(' s_jmp_to_expr expression ')' '{' case_stmts default_stmt '}'
;
case_stmts: case_stmts case_stmt
| /* epsilon */
;
case_stmt: "case" s_switch_jf NUM ':' statement_list
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
| s_push_num NUM
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
s_atomic_var_declaration : /* epsilon */
;
s_array_declaration : /* epsilon */
;
s_atomic_param_declaration : /* epsilon */
;
s_array_param_declaration : /* epsilon */
;
s_push_num : /* epsilon */
;
s_pop_stack : /* epsilon */
;
s_switch_save : /* epsilon */
;

%%
