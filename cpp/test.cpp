#include <iostream>

extern "C" {
void hello_cpp() {
  std::cout << "Hello, from C++" << std::endl;
}