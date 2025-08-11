# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a minimal malloc implementation tutorial in C, demonstrating custom memory allocation using the `sbrk()` system call.

## Code Structure
- `simple-malloc.h` - Header file with block metadata structure and global declarations
- `simple-malloc.c` - Main implementation with `my_malloc()` function and helper functions
- `memo.md` - Notes about memory management requirements in Japanese

## Key Architecture
The memory allocator uses a linked list of block metadata structures to track allocated and free memory blocks:
- Each block has size, next pointer, free flag, and magic number for debugging
- Global base pointer tracks the beginning of the heap
- Functions: `find_free_block()`, `request_space()`, `my_malloc()`

## Build and Run
```bash
# Compile and create shared library
gcc -fPIC -shared -o malloc.dylib simple-malloc.c

# Compile test executable (when main function is uncommented)
gcc -o a.out simple-malloc.c
./a.out
```

## Development Notes
- Uses `sbrk()` system call for heap memory requests
- Includes TODO comments for alignment and block splitting optimizations
- Magic numbers (0x12345, 0x77777777) used for debugging memory corruption
- Contains commented-out test code in main function

## Improvements Implemented
- **Memory Alignment**: 8-byte alignment for all allocations using ALIGN macro
- **Block Splitting**: `split_block()` function to minimize memory waste
- **Block Merging**: `merge_free_blocks()` function to reduce fragmentation
- **Free Function**: `my_free()` implementation with basic validation

## Known Issues and Bugs
- Thread safety not implemented (global variables cause race conditions)
- Limited error handling for edge cases
- Magic number validation is basic and can be bypassed
- No protection against double-free or use-after-free

## Testing
See `EXERCISES.md` for detailed analysis, test cases, and bug reports

## MMAP Implementation
- Alternative malloc implementation using `mmap()` system calls
- Hybrid approach: small allocations in heap regions, large allocations directly mapped
- Includes cleanup functionality and better memory management
- See `MALLOC_COMPARISON.md` for detailed comparison with sbrk version

## Benchmark Results
- SBRK implementation: ~6x faster for small allocations
- MMAP implementation: ~30x faster for large allocations (≥1MB)
- Compilation: `gcc -o benchmark benchmark.c simple-malloc.c mmap-malloc.c -w`