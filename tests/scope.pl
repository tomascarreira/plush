function print_int(val n: int);

function main() {
  var a: int := 1;
  {
    var a: int := 2;
    print_int(a);
  }
  print_int(a);
}
