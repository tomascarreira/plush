function print_int(val n: int);

struct A {
  var a: int
}

var sa: struct A := struct A(2);

function main() {
  print_int(sa.a);
  sa.a := 3;
  print_int(sa.a);
}
