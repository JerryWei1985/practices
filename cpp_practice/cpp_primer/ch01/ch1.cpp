#include <iostream>
#include "Sales_item.h"

//int main() {
//    std::cout << "Enter two numbers:" << std::endl;
//    int v1 = 0, v2 = 0;
//    std::cin >> v1 >> v2;
//    std::cout << "The sum of " << v1 << " and " << v2
//              << " is " << v1 + v2 << std::endl;
//    return 0;
//}

int p_01() {
    int currVal = 0, val = 0;
    if (std::cin >> currVal) {
        int cnt = 1;
        while (std::cin >> val) {
            if (currVal == val) {
                ++cnt;
            } else {
                std::cout << currVal << " occurs "
                          << cnt << " times" << std::endl;
                currVal = val;
                cnt = 1;
            }
        }
        std::cout << currVal << " occurs " << cnt << " times " << std::endl;
    }
    return 0;
}

int p_1_7() {
//    std::cout << "/*" << std::endl;
//    std::cout << "*/" << std::endl;
//    std::cout << /* "*/" */";
    std::cout << /* "*/" /* "/*" */;
}

// 求1到10之和
int c_1_4_1() {
    int i = 1, sum = 0;
    while (i <= 10) {
        sum += i;
        i++;
    }
    std::cout << "Sum of 1 to 10 inclusive is "
              << sum << std::endl;
    return 0;
}

int p_1_9() {
    int val = 50, sum = 0;
    while (val <= 100) {
        sum += val;
        val++;
    }
    std::cout << "50 + ... + 100 = " << sum << std::endl;
    return 0;
}

int p_1_10() {
    int val = 10, sum = 0;
    while (val > 0) {
        sum += val;
        val--;
    }
    std::cout << "10 + ... + 1 = " << sum << std::endl;
    return 0;
}

int p_1_11() {
    int first_num = 0, second_num = 0, sum = 0;
    std::cout << "Input two numbers: " << std::endl;
    std::cin >> first_num >> second_num;
    if (first_num > second_num) {
        first_num += second_num;
        second_num = first_num - second_num;
        first_num -= second_num;
    } else if (first_num == second_num) {
        std::cout << "Two numbers are the same." << std::endl;
        return 0;
    }
    int i = first_num;
    while (i <= second_num) {
        sum += i;
        i++;
    }
    std::cout << first_num << " + ... + " << second_num
              << " = " << sum << std::endl;
    return 0;
}

int p_1_12() {
    int sum = 0;
    for (int i = -100; i <= 100; ++i)
        sum += i;
    std::cout << sum << std::endl;
}

int p_1_20() {
    Sales_item item1;
    while (std::cin >> item1) {
        std::cout << item1 << std::endl;
    }
    return 0;
}

int p_1_21() {

}

int main() {
//    return  p_01();
//    return p_1_7();
//    return c_1_4_1();
//    return p_1_9();
//    return p_1_10();
//    return p_1_11();
//    return p_1_12();
    return p_1_20();
}
