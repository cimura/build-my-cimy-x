#include <assert.h>
#include <string.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

struct mmap_block_meta
{
    size_t size;
    struct mmap_block_meta *next;
    struct mmap_block_meta *prev;
    int free;
    int magic;
    int is_large;  // Large blocks are directly mmapped
};

#define MMAP_META_SIZE sizeof(struct mmap_block_meta)
#define ALIGN_SIZE 8
#define ALIGN(size) (((size) + (ALIGN_SIZE-1)) & ~(ALIGN_SIZE-1))
#define PAGE_SIZE 4096
#define LARGE_BLOCK_THRESHOLD (PAGE_SIZE - MMAP_META_SIZE)

struct mmap_heap_region {
    void *start;
    size_t size;
    struct mmap_heap_region *next;
};

// Global variables
extern struct mmap_block_meta *mmap_global_base;
extern struct mmap_heap_region *heap_regions;

// Function declarations
void *mmap_malloc(size_t size);
void mmap_free(void *ptr);
struct mmap_block_meta *mmap_find_free_block(struct mmap_block_meta **last, size_t size);
void *mmap_request_space(size_t size);
void *mmap_request_large_block(size_t size);
void mmap_split_block(struct mmap_block_meta *block, size_t size);
void mmap_merge_free_blocks(struct mmap_block_meta *block);
void mmap_coalesce_with_prev(struct mmap_block_meta *block);
void mmap_cleanup(void);