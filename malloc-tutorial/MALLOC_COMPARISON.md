# SBRK vs MMAP Memory Allocator Comparison

## 実装の概要

### SBRK-based Implementation (simple-malloc.c)
- `sbrk()`システムコールを使用してheapを拡張
- 単一の連続したメモリ領域を管理
- 単純なlinked listによるfree block管理

### MMAP-based Implementation (mmap-malloc.c)
- `mmap()`システムコールでページ単位のメモリ確保
- 小さなallocationはheap region内で管理
- 大きなallocation（>4KB）は直接mmapで確保
- 双方向linked listと複雑なmerge機能

## ベンチマーク結果

```
=== SBRK-based malloc benchmark ===
Allocation time: 0.3421 seconds
Free time (50%): 0.0000 seconds
Reallocation time: 0.0003 seconds

=== MMAP-based malloc benchmark ===
Allocation time: 2.2674 seconds
Free time (50%): 0.0001 seconds
Reallocation time: 0.0002 seconds

=== Large allocation benchmark (1MB each) ===
SBRK large allocation time: 0.0031 seconds
SBRK large free time: 0.0000 seconds
MMAP large allocation time: 0.0001 seconds
MMAP large free time: 0.0001 seconds
```

## 性能分析

### 小さなAllocation（<1KB）
- **SBRK**: 非常に高速（0.34秒 for 10,000 allocations）
- **MMAP**: 大幅に遅い（2.27秒 for 10,000 allocations）
- **理由**: mmapのoverheadとページアラインメント

### 大きなAllocation（≥1MB）
- **SBRK**: 中程度の速度（0.0031秒 for 100 allocations）
- **MMAP**: 最高速度（0.0001秒 for 100 allocations）
- **理由**: mmapは大きなblockを直接管理

### Free Performance
- **SBRK**: 極めて高速（ほぼゼロ時間）
- **MMAP**: 高速だが若干のoverhead
- **理由**: sbrkはfree時にOSへの返却なし

## 利点と欠点の比較

### SBRK Implementation

#### 利点
1. **高速な小割当て**: システムコールのoverheadが最小
2. **シンプルな実装**: 理解しやすく、デバッグが容易
3. **メモリ効率**: メタデータのoverheadが小さい
4. **cache効率**: 連続したメモリ領域でcache hit率が高い

#### 欠点
1. **メモリ返却不能**: OSに未使用メモリを返せない
2. **断片化の蓄積**: 長時間実行でメモリ断片化が進行
3. **非推奨API**: 現代のシステムでsbrkは非推奨
4. **仮想メモリ非効率**: 不要な領域も仮想アドレス空間を消費

### MMAP Implementation

#### 利点
1. **メモリ返却可能**: 不要なメモリを即座にOSに返却
2. **大きなallocation効率**: 大容量メモリを効率的に処理
3. **現代的なAPI**: mmapは推奨される標準的手法
4. **柔軟な管理**: ページ単位での細かい制御が可能

#### 欠点
1. **小割当ての低速性**: システムコールのoverheadが大きい
2. **複雑な実装**: デバッグとメンテナンスが困難
3. **メタデータoverhead**: 管理構造が複雑で容量が大きい
4. **ページ粒度**: 小さなallocationでも4KBページが必要

## 使用場面の推奨

### SBRK Implementation適用場面
- 組み込みシステムや制約のある環境
- 小さなallocationが多いアプリケーション
- 短時間実行のプログラム
- 教育・学習目的

### MMAP Implementation適用場面
- 長時間実行のサーバーアプリケーション
- 大きなメモリ消費が予想される処理
- メモリ使用量の変動が激しいアプリケーション
- 本格的なproduction環境

## セキュリティと安全性

### SBRK Security Issues
- Heap overflow detection困難
- Use-after-free保護なし
- Double-free検出不十分

### MMAP Security Advantages
- ページ単位の保護設定可能
- 個別regionの権限制御
- より細かいメモリ保護機能

## 実装の改善提案

### SBRK Implementation改善点
1. Better alignment handling
2. Heap canary値による破壊検出
3. 統計情報の収集機能
4. Thread-safe版の実装

### MMAP Implementation改善点
1. Small allocation用の最適化
2. Region poolingによる効率化
3. Advanced coalescing algorithm
4. Memory usage tracking

## 結論

**小規模・短期実行**: SBRK implementationが圧倒的に有利
**大規模・長期実行**: MMAP implementationが適している
**教育目的**: SBRK implementationが理解しやすい
**Production使用**: MMAP implementationが安全

現代のmalloc実装（glibc malloc等）は両方の利点を組み合わせ、小さなallocationにはsbrkベースのheap、大きなallocationにはmmapを使用するhybrid approachを採用している。