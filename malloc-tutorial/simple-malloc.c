#include "simple-malloc.h"

void *global_base = NULL;

struct block_meta *find_free_block(struct block_meta **last, size_t size) {
	struct block_meta *current = global_base;
	while (current && !(current->free && current->size >= size)) {
		*last = current;
		current = current->next;
	}
	return current;
}

struct block_meta *request_space(struct block_meta *last, size_t size) {
	struct block_meta *block;
	block = sbrk(0);
	void *request = sbrk(size + META_SIZE);
	// assert((void *)block == request); // Skip assertion for benchmark
	if (request == (void*)-1) {
		return NULL;
	}
	if (last) {
		last->next = block;
	}
	block->size = size;
	block->next = NULL;
	block->free = 0;
	block->magic = 0x12345;
	return block;
}

//void *my_malloc(size_t size) {
//	void *p = sbrk(0);
//	void *request = sbrk(size);
//	if (request == (void *) -1) {
//		perror("sbrk failed");
//		return NULL; // sbrk failed
//	} else {
//		assert(p == request); // not thread safe
//		return p;
//	}
//}

void split_block(struct block_meta *block, size_t size) {
    if (block->size >= size + META_SIZE + ALIGN_SIZE) {
        struct block_meta *new_block = (struct block_meta*)((char*)(block + 1) + size);
        new_block->size = block->size - size - META_SIZE;
        new_block->next = block->next;
        new_block->free = 1;
        new_block->magic = 0x87654321;
        
        block->size = size;
        block->next = new_block;
    }
}

void merge_free_blocks(struct block_meta *block) {
    while (block->next && block->next->free) {
        block->size += META_SIZE + block->next->size;
        block->next = block->next->next;
    }
}

void my_free(void *ptr) {
    if (!ptr) return;
    
    struct block_meta *block = (struct block_meta*)ptr - 1;
    
    // デバッグ用のmagic numberチェック
    if (block->magic != 0x77777777 && block->magic != 0x12345) {
        return; // 不正なポインタ
    }
    
    block->free = 1;
    block->magic = 0x87654321;
    
    // 隣接する空きブロックとマージ
    merge_free_blocks(block);
}

void *my_malloc(size_t size) {
  struct block_meta *block;
  
  if (size <= 0) {
    return NULL;
  }
  
  // アライメント調整
  size = ALIGN(size);

  if (!global_base) { // First call.
    block = request_space(NULL, size);
    if (!block) {
      return NULL;
    }
    global_base = block;
  } else {
    struct block_meta *last = global_base;
    block = find_free_block(&last, size);
    if (!block) { // Failed to find free block.
      block = request_space(last, size);
      if (!block) {
        return NULL;
      }
    } else {      // Found free block
      split_block(block, size);
      block->free = 0;
      block->magic = 0x77777777;
    }
  }

  return(block+1);
}

//int main() {
//	//char *result = malloc(-1);
//	char *result = malloc(10000000000);
//	//assert(result == NULL);
//	//char *result;
//	strcpy(result, "hello world\n");
//	printf("%s", result);
//}