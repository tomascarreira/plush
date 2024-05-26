function int_array(val size: int): [int];
function print_int_array(val arr: [int], val size: int);
function int_array_array(val size: int): [[int]];
function print_int(val n: int);

function main() {
  var arr1: [int] := int_array(2);
  arr1[0] := 1;
  arr1[1] := 2;
  print_int_array(arr1, 2);

  var arr2: [int] := int_array(2);
  arr2[0] := 3;
  arr2[1] := 4;
  print_int_array(arr2, 2);

  var arr: [[int]] := int_array_array(2);
  arr[0] := arr1;
  arr[1] := arr2;
  print_int_array(arr[0], 2);
  print_int_array(arr[1], 2);
  print_int(arr[0][0]);
  print_int(arr[1][1]);

  arr[1][1] := 42;
  print_int(arr[1][1]);
}

