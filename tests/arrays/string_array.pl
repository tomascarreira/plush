function str_array(val size: int): [string];
function print_str_array(val arr: [string], val size: int);

function main() {
  var arr: [string] := str_array(3);
  arr[0] := "banana";
  arr[1] := "pera";
  arr[2] := "anona";

  print_str_array(arr, 3);
}
