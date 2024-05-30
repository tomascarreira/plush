function print_int_array(val arr: [int], val size: int);
function int_array(val size: int): [int];

function sort(var lst : [int], val len : int) : [int] {
  var i : int := 1;

  while i < len {
    val key : int := lst[i];
    var j : int := i - 1;
    while j >= 0 && lst[j] > key {
      lst[j+1] := lst[j];
      j := j - 1;
    }
    lst[j+1] := key;
    i := i + 1;
  }

  sort := lst;
}

function main() {
  var lst : [int] := int_array(4);
  lst[0] := 2;
  lst[1] := 1;
  lst[2] := 4;
  lst[3] := 3;
  lst := sort(lst, 4);
  print_int_array(lst, 4);
}
