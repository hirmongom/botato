#include <iostream>
#include <string>

extern "C" {
const char* hello_cpp() {
  return "Hello, from C++";
}
}