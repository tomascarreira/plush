function print_int(val n: int);

function main() {
  var a: int := 1;
  {
    a := 2;
    print_int(a);
  }
  print_int(a);
}
