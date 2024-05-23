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
