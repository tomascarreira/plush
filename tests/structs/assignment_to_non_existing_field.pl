struct A {
  var a: int,
  val b: float,
}

function main() {
  var sa: struct A := struct A(1,2.0);  
  sa.c := 3;
}


