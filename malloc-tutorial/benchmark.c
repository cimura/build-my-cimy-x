#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <sys/time.h>

// Include both implementations
#include "simple-malloc.h"
#include "mmap-malloc.h"

#define NUM_ALLOCATIONS 10000
#define MAX_SIZE 1024

double get_time_diff(struct timeval start, struct timeval end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
}

void benchmark_sbrk_malloc() {
    struct timeval start, end;
    void *ptrs[NUM_ALLOCATIONS];
    
    printf("=== SBRK-based malloc benchmark ===\n");
    
    // Allocation benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS; i++) {
        size_t size = (rand() % MAX_SIZE) + 1;
        ptrs[i] = my_malloc(size);
        if (ptrs[i]) {
            // Write some data to ensure the memory is actually used
            memset(ptrs[i], i % 256, size);
        }
    }
    gettimeofday(&end, NULL);
    printf("Allocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS; i += 2) { // Free every other allocation
        if (ptrs[i]) {
            my_free(ptrs[i]);
        }
    }
    gettimeofday(&end, NULL);
    printf("Free time (50%%): %.4f seconds\n", get_time_diff(start, end));
    
    // Reallocation benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS / 2; i++) {
        size_t size = (rand() % MAX_SIZE) + 1;
        void *ptr = my_malloc(size);
        if (ptr) {
            memset(ptr, i % 256, size);
            my_free(ptr);
        }
    }
    gettimeofday(&end, NULL);
    printf("Reallocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free remaining
    for (int i = 1; i < NUM_ALLOCATIONS; i += 2) {
        if (ptrs[i]) {
            my_free(ptrs[i]);
        }
    }
    
    printf("\n");
}

void benchmark_mmap_malloc() {
    struct timeval start, end;
    void *ptrs[NUM_ALLOCATIONS];
    
    printf("=== MMAP-based malloc benchmark ===\n");
    
    // Allocation benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS; i++) {
        size_t size = (rand() % MAX_SIZE) + 1;
        ptrs[i] = mmap_malloc(size);
        if (ptrs[i]) {
            // Write some data to ensure the memory is actually used
            memset(ptrs[i], i % 256, size);
        }
    }
    gettimeofday(&end, NULL);
    printf("Allocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS; i += 2) { // Free every other allocation
        if (ptrs[i]) {
            mmap_free(ptrs[i]);
        }
    }
    gettimeofday(&end, NULL);
    printf("Free time (50%%): %.4f seconds\n", get_time_diff(start, end));
    
    // Reallocation benchmark
    gettimeofday(&start, NULL);
    for (int i = 0; i < NUM_ALLOCATIONS / 2; i++) {
        size_t size = (rand() % MAX_SIZE) + 1;
        void *ptr = mmap_malloc(size);
        if (ptr) {
            memset(ptr, i % 256, size);
            mmap_free(ptr);
        }
    }
    gettimeofday(&end, NULL);
    printf("Reallocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free remaining
    for (int i = 1; i < NUM_ALLOCATIONS; i += 2) {
        if (ptrs[i]) {
            mmap_free(ptrs[i]);
        }
    }
    
    // Cleanup
    mmap_cleanup();
    
    printf("\n");
}

void large_allocation_benchmark() {
    struct timeval start, end;
    const size_t large_size = 1024 * 1024; // 1MB
    const int num_large = 100;
    
    printf("=== Large allocation benchmark (1MB each) ===\n");
    
    // SBRK large allocations
    void *sbrk_ptrs[num_large];
    gettimeofday(&start, NULL);
    for (int i = 0; i < num_large; i++) {
        sbrk_ptrs[i] = my_malloc(large_size);
        if (sbrk_ptrs[i]) {
            memset(sbrk_ptrs[i], i % 256, 1024); // Touch first page
        }
    }
    gettimeofday(&end, NULL);
    printf("SBRK large allocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free SBRK allocations
    gettimeofday(&start, NULL);
    for (int i = 0; i < num_large; i++) {
        if (sbrk_ptrs[i]) {
            my_free(sbrk_ptrs[i]);
        }
    }
    gettimeofday(&end, NULL);
    printf("SBRK large free time: %.4f seconds\n", get_time_diff(start, end));
    
    // MMAP large allocations
    void *mmap_ptrs[num_large];
    gettimeofday(&start, NULL);
    for (int i = 0; i < num_large; i++) {
        mmap_ptrs[i] = mmap_malloc(large_size);
        if (mmap_ptrs[i]) {
            memset(mmap_ptrs[i], i % 256, 1024); // Touch first page
        }
    }
    gettimeofday(&end, NULL);
    printf("MMAP large allocation time: %.4f seconds\n", get_time_diff(start, end));
    
    // Free MMAP allocations
    gettimeofday(&start, NULL);
    for (int i = 0; i < num_large; i++) {
        if (mmap_ptrs[i]) {
            mmap_free(mmap_ptrs[i]);
        }
    }
    gettimeofday(&end, NULL);
    printf("MMAP large free time: %.4f seconds\n", get_time_diff(start, end));
    
    mmap_cleanup();
    printf("\n");
}

int main() {
    srand(time(NULL));
    
    printf("Memory Allocator Benchmark Comparison\n");
    printf("=====================================\n\n");
    
    benchmark_sbrk_malloc();
    benchmark_mmap_malloc();
    large_allocation_benchmark();
    
    return 0;
}