function print_int(val n: int);
function print_bool(val b: bool);

function main() {
  print_int(2*3+4);
  print_int(2+3*4);

  print_int(2/3-4);
  print_int(2-3/4);

  print_int(2%3+4);
  print_int(2+3%4);

  print_int(2+-3);
  print_int(2--3);

  print_bool(!false && false);
  print_bool(!false || true);

  print_bool(false && true || true);

  print_bool(2 + 1 > 3);
  print_bool(2 + 1 >= 3);
  print_bool(2 + 1 < 3);
  print_bool(2 + 1 <= 3);

  print_int((2+3)*4);
}
