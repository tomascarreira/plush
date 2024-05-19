function bool_array(val size: int): [bool];
function print_bool_array(val arr: [bool], val size: int);

function main() {
  var arr: [bool] := bool_array(3);
  arr[0] := true;
  arr[1] := false;
  arr[2] := true;

  print_bool_array(arr, 3);
}


