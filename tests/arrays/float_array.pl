function float_array(val size: int): [float];
function print_float_array(val arr: [float], val size: int);

function main() {
  var arr: [float] := float_array(3);
  arr[0] := 1.0;
  arr[1] := 2.0;
  arr[2] := 3.0;

  print_float_array(arr, 3);
}
