function int_array(val size: int): [int];
function print_int_array(val arr: [int], val size: int);

function main() {
  var arr: [int] := int_array(3);
  arr[0] := 1;
  arr[1] := 2;
  arr[2] := 3;

  print_int_array(arr, 3);
}
