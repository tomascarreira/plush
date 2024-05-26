function int_array(val size: int): [int];
function print_int_array(val arr: [int], val size: int);

function main() {
  var arr: [int] := int_array(5);
  arr[0] := 0;
  arr[1] := 1;
  arr[2] := 2;
  arr[3] := 3;
  arr[4] := 4;

  print_int_array(arr, 5);
}
