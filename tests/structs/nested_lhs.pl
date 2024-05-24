struct A {
  var b: struct B,
}

struct B {
  var b: int,
}

function print_int(val n: int);

function main() {
  var s: struct A := struct A(struct B(2));

  s.b.b := 3;
  print_int(s.b.b);
}

