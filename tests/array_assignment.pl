function int_array(val size: int): [int];
function print_int(val n: int);

function main() {
  var arr: [int] := int_array(1);
  arr[0] := 5;

  print_int(arr[0]);
}
