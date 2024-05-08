function print_int(val n: int);

function main() {
  print_int(f());
  print_int(g());
}

function f(): int {
  val a: int := 3;
  f := a;
}

function g(): int {
  val a: int := 2;
  g := a;
}
