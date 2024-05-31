function int_array(val size: int): [int];
function print_int_array(val arr: [int], val size: int);
function print_int(val n: int);
function copy_int_array(val dest: [int], val src: [int], val size: int);

struct ArrayList {
  var arr: [int],
  var cap: int,
  var len: int,
}

function main() {
  var arrlist: struct ArrayList := new(2);
  arrlist := add(arrlist, 1);
  arrlist := add(arrlist, 2);
  print_array_list(arrlist);
  arrlist := add(arrlist, 3);
  print_array_list(arrlist);

  print_int(get(arrlist, 1));
  update(arrlist, 42, 0);
  print_array_list(arrlist);

}

function new(var cap: int): struct ArrayList {
  new := struct ArrayList(int_array(cap), cap, 0);
}

# function needs to return the array list beacause its passed by value. Not that i wanted that but its to late to change :(
function add(var arrlist: struct ArrayList, val value: int): struct ArrayList {
  if arrlist.len = arrlist.cap {
    var new_array: [int] := int_array(arrlist.cap * 2);    
    copy_int_array(new_array, arrlist.arr, arrlist.len);
    arrlist.arr := new_array;
  }

  var tmp: [int] := arrlist.arr;
  tmp[arrlist.len] := value;
  arrlist.len := arrlist.len + 1;

  print_array_list(arrlist);
  add := arrlist;
}

function get(var arrlist: struct ArrayList, val idx: int): int {
  val tmp: [int] := arrlist.arr; 
  get := tmp[idx];
}

function update(var arrlist: struct ArrayList, val value: int, val idx: int): struct ArrayList {
  val tmp: [int] := arrlist.arr; 
  tmp[idx] := value;

  update := arrlist;
}

function print_array_list(val arrlist: struct ArrayList) {
  print_int_array(arrlist.arr, arrlist.len);
}
