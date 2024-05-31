function int_array(val size: int): [int];
function print_int_array(val arr: [int], val size: int);

struct A {
  var arr: [int]
}

function main() {
  var s: struct A := struct A(int_array(2));

  var arr2: [int] := s.arr;
  arr2[0] := 1;
  arr2[1] := 2;

  print_int_array(s.arr, 2);
  print_int_array(arr2, 2);
}
