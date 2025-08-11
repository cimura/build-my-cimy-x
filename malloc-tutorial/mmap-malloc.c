#include "mmap-malloc.h"

struct mmap_block_meta *mmap_global_base = NULL;
struct mmap_heap_region *heap_regions = NULL;

struct mmap_block_meta *mmap_find_free_block(struct mmap_block_meta **last, size_t size) {
    struct mmap_block_meta *current = mmap_global_base;
    while (current && !(current->free && current->size >= size && !current->is_large)) {
        *last = current;
        current = current->next;
    }
    return current;
}

void *mmap_request_space(size_t size) {
    // Round up to page size
    size_t total_size = ALIGN(size + MMAP_META_SIZE);
    if (total_size < PAGE_SIZE) {
        total_size = PAGE_SIZE;
    }
    
    void *region = mmap(NULL, total_size, PROT_READ | PROT_WRITE, 
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (region == MAP_FAILED) {
        perror("mmap failed");
        return NULL;
    }
    
    // Record this region for cleanup
    struct mmap_heap_region *new_region = (struct mmap_heap_region *)region;
    new_region->start = region;
    new_region->size = total_size;
    new_region->next = heap_regions;
    heap_regions = new_region;
    
    // Create block metadata after the region header
    struct mmap_block_meta *block = (struct mmap_block_meta *)
        ((char *)region + sizeof(struct mmap_heap_region));
    
    block->size = total_size - sizeof(struct mmap_heap_region) - MMAP_META_SIZE;
    block->next = NULL;
    block->prev = NULL;
    block->free = 0;
    block->magic = 0x12345;
    block->is_large = 0;
    
    return block;
}

void *mmap_request_large_block(size_t size) {
    size_t total_size = ALIGN(size + MMAP_META_SIZE);
    
    void *region = mmap(NULL, total_size, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (region == MAP_FAILED) {
        perror("mmap failed for large block");
        return NULL;
    }
    
    struct mmap_block_meta *block = (struct mmap_block_meta *)region;
    block->size = size;
    block->next = NULL;
    block->prev = NULL;
    block->free = 0;
    block->magic = 0x54321;
    block->is_large = 1;
    
    return block;
}

void mmap_split_block(struct mmap_block_meta *block, size_t size) {
    if (block->size >= size + MMAP_META_SIZE + ALIGN_SIZE && !block->is_large) {
        struct mmap_block_meta *new_block = (struct mmap_block_meta*)
            ((char*)(block + 1) + size);
        
        new_block->size = block->size - size - MMAP_META_SIZE;
        new_block->next = block->next;
        new_block->prev = block;
        new_block->free = 1;
        new_block->magic = 0x87654321;
        new_block->is_large = 0;
        
        if (block->next) {
            block->next->prev = new_block;
        }
        
        block->size = size;
        block->next = new_block;
    }
}

void mmap_coalesce_with_prev(struct mmap_block_meta *block) {
    if (block->prev && block->prev->free && !block->prev->is_large) {
        struct mmap_block_meta *prev = block->prev;
        prev->size += MMAP_META_SIZE + block->size;
        prev->next = block->next;
        if (block->next) {
            block->next->prev = prev;
        }
    }
}

void mmap_merge_free_blocks(struct mmap_block_meta *block) {
    if (block->is_large) return;
    
    // Merge with next blocks
    while (block->next && block->next->free && !block->next->is_large) {
        struct mmap_block_meta *next = block->next;
        block->size += MMAP_META_SIZE + next->size;
        block->next = next->next;
        if (next->next) {
            next->next->prev = block;
        }
    }
    
    // Merge with previous block
    mmap_coalesce_with_prev(block);
}

void mmap_free(void *ptr) {
    if (!ptr) return;
    
    struct mmap_block_meta *block = (struct mmap_block_meta*)ptr - 1;
    
    // Validate magic number
    if (block->magic != 0x77777777 && block->magic != 0x12345 && block->magic != 0x54321) {
        return; // Invalid pointer
    }
    
    if (block->is_large) {
        // Large block - unmap directly
        size_t total_size = ALIGN(block->size + MMAP_META_SIZE);
        if (munmap(block, total_size) == -1) {
            perror("munmap failed");
        }
        return;
    }
    
    block->free = 1;
    block->magic = 0x87654321;
    
    mmap_merge_free_blocks(block);
}

void *mmap_malloc(size_t size) {
    if (size <= 0) {
        return NULL;
    }
    
    size = ALIGN(size);
    
    // Large allocation - use direct mmap
    if (size >= LARGE_BLOCK_THRESHOLD) {
        struct mmap_block_meta *block = mmap_request_large_block(size);
        if (!block) return NULL;
        
        block->magic = 0x77777777;
        return (block + 1);
    }
    
    struct mmap_block_meta *block;
    
    if (!mmap_global_base) {
        // First call
        block = mmap_request_space(size);
        if (!block) return NULL;
        mmap_global_base = block;
    } else {
        struct mmap_block_meta *last = mmap_global_base;
        block = mmap_find_free_block(&last, size);
        
        if (!block) {
            // No suitable free block found - request new space
            struct mmap_block_meta *new_block = mmap_request_space(size);
            if (!new_block) return NULL;
            
            last->next = new_block;
            new_block->prev = last;
            block = new_block;
        } else {
            // Found free block
            mmap_split_block(block, size);
            block->free = 0;
        }
    }
    
    block->magic = 0x77777777;
    return (block + 1);
}

// Cleanup function to release all mmap regions
void mmap_cleanup() {
    struct mmap_heap_region *region = heap_regions;
    while (region) {
        struct mmap_heap_region *next = region->next;
        if (munmap(region->start, region->size) == -1) {
            perror("munmap failed during cleanup");
        }
        region = next;
    }
    heap_regions = NULL;
    mmap_global_base = NULL;
}