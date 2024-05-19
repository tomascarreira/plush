function print_int(val n: int);

function main() {
  print_int(fib(15));
}

function fib(val n: int): int {
  if n = 0 {
    fib := 0;
  } else { if n = 1 {
    fib := 1;
  } else {
    fib := fib(n-1) + fib(n-2);
  }}
}
