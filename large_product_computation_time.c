#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <gmp.h> // Inclusion de la bibliothèque GMP

int compare(const void *a, const void *b) {
    double diff = (*(double*)a - *(double*)b);
    return (diff > 0) - (diff < 0);
}

// La tâche tau_1 reçoit l'état du générateur aléatoire
double task_1(gmp_randstate_t state) {
    struct timespec start, end;
    mpz_t num1, num2, result;

    // Initialisation des entiers GMP
    mpz_init(num1);
    mpz_init(num2);
    mpz_init(result);

    // Génération de nombres aléatoires de 40 000 bits (exactement comme en Python)
    mpz_urandomb(num1, state, 40000);
    mpz_urandomb(num2, state, 40000);

    // Début du chronomètre (on ne mesure QUE le temps de calcul)
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Multiplication : result = num1 * num2
    mpz_mul(result, num1, num2);

    // Fin du chronomètre
    clock_gettime(CLOCK_MONOTONIC, &end);

    // Libération de la mémoire
    mpz_clear(num1);
    mpz_clear(num2);
    mpz_clear(result);

    // Retour du temps en millisecondes
    return (end.tv_sec - start.tv_sec) * 1e3 + (end.tv_nsec - start.tv_nsec) / 1e6;
}

int main() {
    int iterations = 10000;
    double *times = malloc(iterations * sizeof(double));

    // Initialisation du générateur aléatoire de GMP
    gmp_randstate_t state;
    gmp_randinit_default(state);
    gmp_randseed_ui(state, time(NULL));

    printf("Mesure des temps d'execution avec GMP en cours...\n");

    for (int i = 0; i < iterations; i++) {
        times[i] = task_1(state);
        if ((i + 1) % (iterations / 10) == 0) {
            printf("Progression : %d%%\n", (i + 1) / (iterations / 100));
        }
    }

    qsort(times, iterations, sizeof(double), compare);

    double min = times[0];
    double max = times[iterations - 1];
    double q1 = times[(int)(iterations * 0.25)];
    double q2 = times[(int)(iterations * 0.50)];
    double q3 = times[(int)(iterations * 0.75)];
    
    // Calcul de C1 (WCET) avec une marge de sécurité de 20%
    double wcet = max * 1.20;

    printf("\n======= Resultats =======\n");
    printf("Min : %.6f ms\n", min);
    printf("Q1  : %.6f ms\n", q1);
    printf("Q2  : %.6f ms\n", q2);
    printf("Q3  : %.6f ms\n", q3);
    printf("Max : %.6f ms\n", max);
    printf("WCET (C1) : %.6f ms\n", wcet);

    // Nettoyage final
    gmp_randclear(state);
    free(times);
    return 0;
}