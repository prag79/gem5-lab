#include <stdio.h>

int main(void) {
    int sum = 0;
    for (int i = 0; i < 10000; i++) {
        sum += i;
    }
    printf("\n*** Hello from gem5 SE-mode RV64 ***\n");
    printf("sum(0..9999) = %d\n", sum);
    return 0;
}
