function print_int_array(val arr: [int], val size: int);
function int_array(val size: int): [int];

function main() {
  var arr1: [int] := int_array(2);
  arr1[0] := 1;
  arr1[1] := 2;

  var arr2: [int] := arr1;
  arr2[0] := 3;

  print_int_array(arr1, 2);
  print_int_array(arr2, 2);
}
