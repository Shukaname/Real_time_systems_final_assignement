#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <gmp.h> 

int compare(const void *a, const void *b) {
    double diff = (*(double*)a - *(double*)b);
    return (diff > 0) - (diff < 0);
}

//measure how long it takes to muiltiply two 40k bits number
double task_1(gmp_randstate_t state) {
    struct timespec start, end;
    mpz_t num1, num2, result;

    // Initializing large variable using gmp
    mpz_init(num1);
    mpz_init(num2);
    mpz_init(result);

    // Generate random 40 000 bits number 
    mpz_urandomb(num1, state, 40000);
    mpz_urandomb(num2, state, 40000);

    // Start clock
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Multiplication : result = num1 * num2
    mpz_mul(result, num1, num2);

    // Stop clock
    clock_gettime(CLOCK_MONOTONIC, &end);

    // Freeing memory
    mpz_clear(num1);
    mpz_clear(num2);
    mpz_clear(result);

    // Return time in millisec
    return (end.tv_sec - start.tv_sec) * 1e3 + (end.tv_nsec - start.tv_nsec) / 1e6;
}

int main() {
    int iterations = 10000; //number of multiplication to measure
    double *times = malloc(iterations * sizeof(double));

    // Initializing gmp random number generator
    gmp_randstate_t state;
    gmp_randinit_default(state);
    gmp_randseed_ui(state, time(NULL));

    printf("Start measuring time...\n");

    for (int i = 0; i < iterations; i++) {
        times[i] = task_1(state);
        if ((i + 1) % (iterations / 10) == 0) {
            printf("Progress : %d%%\n", (i + 1) / (iterations / 100));
        }
    }

    qsort(times, iterations, sizeof(double), compare);

    double min = times[0];
    double max = times[iterations - 1];
    double q1 = times[(int)(iterations * 0.25)];
    double q2 = times[(int)(iterations * 0.50)];
    double q3 = times[(int)(iterations * 0.75)];
    
    // Compute WCET with a 20% margin
    double wcet = max * 1.20;

    printf("\n======= Results =======\n");
    printf("Min : %.6f ms\n", min);
    printf("Q1  : %.6f ms\n", q1);
    printf("Q2  : %.6f ms\n", q2);
    printf("Q3  : %.6f ms\n", q3);
    printf("Max : %.6f ms\n", max);
    printf("WCET (C1) : %.6f ms\n", wcet); // WCET computed : 2.17 ms

    // Final cleaning
    gmp_randclear(state);
    free(times);
    return 0;
}