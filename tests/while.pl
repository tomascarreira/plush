function print_int(val n: int);

function main() {
  var i: int := 5;
  while i > 0 {
    print_int(i);
    i := i - 1;
  }
}
