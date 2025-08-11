#include <assert.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

struct block_meta
{
	size_t size;
	struct block_meta *next;
	int free;
	int magic;
};

#define META_SIZE sizeof(struct block_meta)
#define ALIGN_SIZE 8
#define ALIGN(size) (((size) + (ALIGN_SIZE-1)) & ~(ALIGN_SIZE-1))

extern void *global_base;

// Function declarations
void *my_malloc(size_t size);
void my_free(void *ptr);
struct block_meta *find_free_block(struct block_meta **last, size_t size);
struct block_meta *request_space(struct block_meta *last, size_t size);
void split_block(struct block_meta *block, size_t size);
void merge_free_blocks(struct block_meta *block);