# Relatorio sobre como implementei structs no plush


## Syntax

declarar structs

```struct A {
  var a: int,
  val b: float,
}```

initializar structs
`var sa: struct A := struct A(1,2.0);`

acedar a campos da struct
`sa.a := 3;`

permitr trailing ','

## Mudanças feitas no compilador

### Lexer

Adicionar o token 'struct' à lista reserved
Adicionar o token 'PERIOD' '.' para acedor ao campos da struct

## Parser

mudar type para aceitar qualquer string

acrescentar regra à gramatica para permitir declaraçao de structs

acrescentar ao enum TypeEnum Struct

adicionar regra à gramática para struct initiliazition (podem estar em qualquer sitio que uma expression pode)

adicionar a regra para aceder aos campos da struct. Impementar como uma binary operation(Como fiz para o indexing)

adicionar uma regra para escrever para um campo da struct

## Pretty printer da árvore

imprimir a struct declaration node
impreimir struct init node

## Type checker

verificar declarar struct
verificar ler de um campo no struct
verificar escrever para um campo no struct

criar uma class Field foi necessário -> parte do parser

## Interpretador

## Codegen

necessário adicionar à arvore informação ao field para o getptraddress

## Improvements

1. FFI
  data packing scheme
  opaque structure types

2. Recursive Structs

## Coisas notáveis a referir

Constant folding for globals. importante para coisas como `val tau: float := 3.14 * 2`. Apesar de não permitir `val pi: float := 3.14; val tau: float := pi * 2`.

Shadowing. `var a: int := 2; { var a: int := 3; }` (ver test relevante). Mas não aceita `var a: int := 2; var a: int := 3;` Ou seja shadowing no mesmo escopo. Gostaria que não fosse o caso mas não encontrei uma maneira simples de faze-lo. O problema é com o llvm por ser ssa
