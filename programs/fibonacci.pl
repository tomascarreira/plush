function print_int(val n: int);

function fib(var n: int): int {
  var res: int := 0;
  if n = 0 {
    res := 0;
  } else {

  if n = 1 {
    res := 1;
  } else {
    var a: int := 0;
    var b: int := 1;
    while n > 1 {
      val tmp: int := a;
      a := b;
      b := tmp + b;
      n := n - 1;
     
    }

    res := b;
  }
  }


  fib := res;
}

function main(){
  print_int(fib(7));
}
