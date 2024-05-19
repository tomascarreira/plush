function print_bool(val b: bool);

function main() {
  print_bool(false || false);
  print_bool(false || true);
  print_bool(true || false);
  print_bool(true || true);
}

