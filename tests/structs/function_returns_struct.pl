function print_int(val n: int);

struct A {
  var n: int,
}

function main() {
  var s: struct A := f();
  print_int(s.n);
}

function f(): struct A {
  f := struct A(1);
}
