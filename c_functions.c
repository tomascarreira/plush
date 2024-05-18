#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

void print_int(int n) {
  printf("%d\n", n);
}

void print_float(float flt) {
  printf("%f\n", flt);
}

void print_bool(bool b) {
  printf("%s\n", b ? "true" : "false");
}

void print_str(char* s) {
  printf("%s\n", s);
}

void print_int_array(int* arr, int size) {
  printf("[");
  for (size_t i = 0; i < size; ++i) {
    printf("%d", arr[i]);
    if (i < size - 1) {
      printf(", ");
    }
  }
  printf("]\n");
}

int* int_array(int size) {
  return malloc(size * sizeof(int));
}

int** int_array_array(int size) {
  return malloc(size * sizeof(int*));
}

int pow_int(int b, int e) {
  return pow(b, e);
}
