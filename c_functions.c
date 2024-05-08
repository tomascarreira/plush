#include <stdio.h>
#include <stdbool.h>

void print_int(int n) {
  printf("%d\n", n);
}

void print_bool(bool b) {
  printf("%s\n", b ? "true" : "false");
}

void print_str(char* s) {
  printf("%s\n", s);
}
