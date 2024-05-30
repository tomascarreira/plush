function print_bool(val b: bool);

function isPrime(val n : int) : bool {
  var i : int := 2;
  var res :int := 0;
  while i < n {
    if n % i = 0 {
      res := res + 1;
    }
    i := i + 1;
  }

  if res = 0 {
    isPrime := true;
  } else {
    isPrime := false;
  }
}

function main(val args : [string]) {
  val result : bool := isPrime(7);
  print_bool(result);
}
