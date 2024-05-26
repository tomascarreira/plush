struct A {
  var b: struct B,
}

struct B {
  var b: int,
}

function print_int(val n: int);

function main() {
  var s: struct A := struct A(struct B(2));

  var s2: struct B := s.b;

  print_int(s2.b);
}
