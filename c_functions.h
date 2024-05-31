#ifndef C_FUNCTIONS_H
#define C_FUNCTIONS_H

void print_int(int n);
void print_float(float flt);
void print_bool(bool b);
void print_str(char* s);
void print_char(char c);
void print_int_array(int* arr, int size);
void print_float_array(float* arr, int size);
void print_str_array(char** arr, int size);
void print_char_array(char* arr, int size);
void print_bool_array(bool* arr, int size);

int* int_array(int size);
float* float_array(int size);
char** str_array(int size);
char* char_array(int size);
bool* bool_array(int size);

void copy_int_array(int* dest, int* src, int size);

int** int_array_array(int size);

int pow_int(int b, int e);

#endif
