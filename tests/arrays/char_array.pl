function char_array(val size: int): [char];
function print_char_array(val arr: [char], val size: int);

function main() {
  var arr: [char] := char_array(3);
  arr[0] := 'a';
  arr[1] := 'b';
  arr[2] := 'c';

  print_char_array(arr, 3);
}

