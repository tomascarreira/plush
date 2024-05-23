function print_int(val n: int);

struct A {
  var a: int,
}

function main() {
  var sa: struct A := struct A(1);  
  print_int(sa.a);
}

