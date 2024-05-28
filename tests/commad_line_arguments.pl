function print_int(val n: int);
function print_str(val s: string);

function main(val argc: int, val argv: [string]) {
  print_int(argc);
  print_str(argv[0]);
}
