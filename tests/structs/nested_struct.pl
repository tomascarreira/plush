struct A {
  var b: struct B,
  var a: int
}

struct B {
  var b: int,
}

function print_int(val n: int);

function main() {
  var s: struct A := struct A(struct B(2), 1);
  print_int(s.b.b);
  var s2: struct B := s.b;
  print_int(s2.b);
  print_int(s.a);

  s.b.b := 3;
  print_int(s.b.b);
}
