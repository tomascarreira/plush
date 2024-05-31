#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

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
  printf("\"%s\"\n", s);
}

void print_char(char c) {
  printf("'%c\n'", c);
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

void print_float_array(float* arr, int size) {
  printf("[");
  for (size_t i = 0; i < size; ++i) {
    printf("%f", arr[i]);
    if (i < size - 1) {
      printf(", ");
    }
  }
  printf("]\n");
}

void print_str_array(char** arr, int size) {
  printf("[");
  for (size_t i = 0; i < size; ++i) {
    printf("\"%s\"", arr[i]);
    if (i < size - 1) {
      printf(", ");
    }
  }
  printf("]\n");
}

void print_char_array(char* arr, int size) {
  printf("[");
  for (size_t i = 0; i < size; ++i) {
    printf("'%c'", arr[i]);
    if (i < size - 1) {
      printf(", ");
    }
  }
  printf("]\n");
}

void print_bool_array(bool* arr, int size) {
  printf("[");
  for (size_t i = 0; i < size; ++i) {
    printf("%s", arr[i] ? "true" : "false");
    if (i < size - 1) {
      printf(", ");
    }
  }
  printf("]\n");
}

int* int_array(int size) {
  return malloc(size * sizeof(int));
}

float* float_array(int size) {
  return malloc(size * sizeof(float));
}

char** str_array(int size) {
  return malloc(size * sizeof(char*));
}

char* char_array(int size) {
  return malloc(size * sizeof(char));
}

bool* bool_array(int size) {
  return malloc(size * sizeof(bool));
}

int** int_array_array(int size) {
  return malloc(size * sizeof(int*));
}

void copy_int_array(int* dest, int* src, int size) {
  memcpy(dest, src, size*sizeof(int));
}

int pow_int(int b, int e) {
  return (int) pow(b, e);
}
