function print_int(val n: int);

struct A {
  var a: int,
  val b: float,
}

function main() {
  var sa: struct A := struct A(1,2.0);  
  sa.a := 3;
  print_int(sa.a);
}
