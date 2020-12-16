#include <iostream>

int p_2_14() {
    int i = 100, sum = 0;
    for (int i = 0; i != 10; ++i)
        sum += i;
    std::cout << i << " " << sum << std::endl;
    return 0;
}

int p_2_17() {
    int i, &ri = i;
    i = 5;
    ri = 10;
    std::cout << i << " " << ri << std::endl;
    return 0;
}

int p_2_18() {
    int i = 0;
    int *p = &i;
    return 0;
}

int p_2_19() {
    int i = 0;
    const int &r1 = i;
    std::cout << r1 << std::endl;
    i = 10;
    std::cout << r1 << std::endl;
    return 0;
}

int main() {
    // return p_2_14();
    // return p_2_17();
    // return p_2_18();
    return p_2_19();
}