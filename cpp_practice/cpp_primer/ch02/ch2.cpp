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
    // constexpr int j = 0;
    // int *p = j;
    const int &r1 = i;
    std::cout << r1 << std::endl;
    i = 10;
    std::cout << r1 << std::endl;
    return 0;
}

int p_2_33() {
    int i = 0, &r = i;
    auto a = r;
    const int ci = i, &cr = ci;
    auto b = ci;
    auto c = cr;
    auto d = &i;
    auto e = &ci;
    const auto f = ci;
    auto &g = ci;
    const auto &j = 42;
    a = 42;
    b = 42;
    c = 42;
    std::cout << *e << std::endl;
    // d = 42;
    e = 42; // 0是可以的，因为内存安全
    // g = 42;
    return 0;
}

int main() {
    // return p_2_14();
    // return p_2_17();
    // return p_2_18();
    // return p_2_19();
    return p_2_33();
}