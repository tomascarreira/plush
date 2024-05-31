struct A {
  var n: int
}

function main() {
  f(struct A(1));
}

function f(val a: struct A) {
  var s: struct A := a;  
}
