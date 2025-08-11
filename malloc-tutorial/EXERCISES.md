# Malloc Implementation Exercises and Analysis

## Exercise 1: Memory Alignment

### Problem Analysis
The original malloc implementation does not ensure proper memory alignment. Built-in C types require alignment up to 8 bytes on most systems.

### Solution Implemented
- Added `ALIGN_SIZE` constant (8 bytes)
- Added `ALIGN` macro: `(((size) + (ALIGN_SIZE-1)) & ~(ALIGN_SIZE-1))`
- Modified `my_malloc()` to align requested size before allocation

### Why Alignment Matters
- CPUは適切にアラインされていないメモリアクセスでパフォーマンス低下またはクラッシュが発生する可能性がある
- 8バイトアラインメントはdouble、long long、ポインタなどの基本型に対応

## Exercise 2: Block Splitting

### Problem Analysis
Original implementation wastes memory when reusing large blocks for small allocations.

### Solution Implemented
```c
void split_block(struct block_meta *block, size_t size) {
    if (block->size >= size + META_SIZE + ALIGN_SIZE) {
        // Create new block from remaining space
        struct block_meta *new_block = (struct block_meta*)((char*)(block + 1) + size);
        new_block->size = block->size - size - META_SIZE;
        new_block->next = block->next;
        new_block->free = 1;
        new_block->magic = 0x87654321;
        
        // Update current block
        block->size = size;
        block->next = new_block;
    }
}
```

### Key Features
- 分割には最小サイズ（META_SIZE + ALIGN_SIZE）が必要
- 新しいブロックは自動的にfreeリストに追加される
- Magic numberでデバッグ支援

## Exercise 3: Block Merging

### Problem Analysis
Fragmentation occurs when adjacent free blocks are not merged together.

### Solution Implemented
```c
void merge_free_blocks(struct block_meta *block) {
    while (block->next && block->next->free) {
        block->size += META_SIZE + block->next->size;
        block->next = block->next->next;
    }
}
```

### Integration
- `my_free()`でブロック解放時に自動的にマージ
- 隣接する全ての空きブロックを結合
- メモリ断片化を大幅に削減

## Exercise 4: Bug Analysis

### Identified Bugs and Issues

1. **find_free_block()の論理エラー**
   - `simple-malloc.c:57`: `last`の初期化が不適切
   - 修正: `find_free_block()`内でlastを正しく設定

2. **Magic Number Inconsistency**
   - 異なる状況で異なるmagic numberを使用（0x12345, 0x77777777）
   - 一貫性のないデバッグ情報

3. **Thread Safety Issues**
   - Global variableの競合状態
   - マルチスレッド環境では危険

4. **Error Handling**
   - `sbrk()`失敗時の不完全な処理
   - Null pointerチェックの不足

5. **Memory Leak Prevention**
   - Double freeの検出なし
   - Use-after-freeの検出なし

### Security Considerations
- Buffer overflowの検出なし
- Magic numberチェックは基本的だが不十分
- メモリ破壊の検出機能が限定的

## Testing Recommendations

### Basic Functionality Tests
```c
// Alignment test
void* p1 = my_malloc(1);
assert(((uintptr_t)p1 % 8) == 0);

// Split test
void* p2 = my_malloc(1000);
void* p3 = my_malloc(10);
my_free(p2);
void* p4 = my_malloc(100); // Should reuse p2's space

// Merge test
void* p5 = my_malloc(100);
void* p6 = my_malloc(100);
my_free(p5);
my_free(p6); // Should merge with p5
```

### Edge Cases
- Zero size allocation
- Very large allocations
- Multiple free calls on same pointer
- Free with invalid pointers

## Performance Implications

### Time Complexity
- Allocation: O(n) - linear search through free list
- Deallocation: O(1) - constant time with merging
- Memory usage: Improved with splitting and merging

### Space Complexity
- Metadata overhead: 16-24 bytes per block
- Fragmentation: Significantly reduced with merging
- Alignment waste: Minimal with proper alignment

## Conclusion

実装された改善により、メモリ効率、アラインメント、断片化の問題が解決された。しかし、スレッドセーフティやセキュリティ面での課題は残っており、本格的な使用には追加の対策が必要。