struct A {
  var a: int,
  val b: float,
}

function main() {
 var s: struct A := struct A(1,1.0);
 var c: float := s.a;
}

