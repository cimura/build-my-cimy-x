# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal Docker-like container runtime implementation written in Go, demonstrating Linux namespaces, pivot_root, and container isolation in ~100 lines of code. The project creates a simple container system using Linux-specific syscalls.

## Build Commands

Since this uses Linux-specific syscalls, it must be built for Linux:

```bash
# Build for Linux (required due to Linux-specific syscalls)
GOOS=linux go build -o docker main.go

# Clean build artifacts
rm -f docker
```

## Running the Container

The binary has two modes:
- `docker run <command>` - Creates parent process with new namespaces
- `docker child <command>` - Internal child process (called by parent)

Example usage (requires Linux environment and rootfs directory):
```bash
./docker run /bin/sh
```

## Architecture

### Core Components

- **main()**: Command dispatcher that routes to parent() or child() functions
- **parent()**: Sets up new namespaces (UTS, PID, MNT) using clone flags and executes child process
- **child()**: Performs pivot_root to change root filesystem and executes the target command
- **must()**: Error handling utility that panics on error

### Key Linux Features Used

- **Namespaces**: UTS (hostname), PID (process IDs), and MNT (mount points)
- **pivot_root()**: Changes the root filesystem from host to container rootfs
- **Bind mounts**: Used to set up the new root filesystem

### Prerequisites for Execution

- Linux environment (uses Linux-specific syscalls)
- `rootfs` directory containing the container filesystem
- Root or appropriate capabilities for namespace operations

## Platform Limitations

This code only works on Linux due to:
- syscall.CLONE_* constants (Linux-specific)
- syscall.Mount and syscall.PivotRoot functions
- syscall.SysProcAttr.Cloneflags field

Cross-compilation to other platforms will build but the resulting binary will not function correctly.

## Project Documentation

### gpt.md - Container Technology Overview

Contains conceptual explanations of container technology:
- Comparison between normal processes and containerized processes
- Explanation of namespaces, memory management, and filesystem isolation
- Technical details on `pivot_root()` vs `chroot`
- Container vs Virtual Machine differences

### memo.md - Container Fundamentals

Provides foundational knowledge about containers:
- Container concept and purpose (dependency isolation)
- Three key technologies: namespaces, cgroups, layered filesystems
- Six Linux namespaces (PID, MNT, NET, UTS, IPC, USER)
- Notes on cgroups and layered filesystems

## Code Structure and Implementation

### main.go - Complete Implementation

```go
package main

import (
	"fmt"
	"os"
	"os/exec"
	"syscall"
)

func main() {
	switch os.Args[1] {
	case "run":
		parent()  // コンテナ作成の開始点
	case "child":
		child()   // 内部的に呼ばれる子プロセス
	default:
		panic("wat should I do")
	}
}

func parent() {
	// 自分自身を"child"モードで再実行
	cmd := exec.Command("/proc/self/exe", append([]string{"child"}, os.Args[2:]...)...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	// 新しい名前空間を作成
	cmd.SysProcAttr = &syscall.SysProcAttr {
		Cloneflags: syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | syscall.CLONE_NEWNS,
	}

	if err := cmd.Run(); err != nil {
		fmt.Println("ERROR", err)
		os.Exit(1)
	}
}

func child() { 
	// rootfsディレクトリをバインドマウント
	must(syscall.Mount("rootfs", "rootfs", "", syscall.MS_BIND, ""))
	
	// 古いルートを保存するディレクトリ作成
	must(os.MkdirAll("rootfs/oldrootfs", 0700))
	
	// ルートファイルシステムを切り替え
	must(syscall.PivotRoot("rootfs", "rootfs/oldrootfs"))
	must(os.Chdir("/"))

	// 指定されたコマンドを実行
	cmd := exec.Command(os.Args[2], os.Args[3:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		fmt.Println("ERROR", err)
		os.Exit(1)
	}
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
```

### Code Flow Explanation

1. **Entry Point (`main`)**: 
   - `run`モード: 新しいコンテナを作成開始
   - `child`モード: 内部的に名前空間内で実行される

2. **Parent Process (`parent`)**:
   - 自分自身を`child`モードで再実行
   - 新しい名前空間を作成 (UTS, PID, MNT)
   - 標準入出力を引き継ぎ

3. **Child Process (`child`)**:
   - `rootfs`ディレクトリをバインドマウント
   - `pivot_root`でルートファイルシステムを変更
   - 指定されたコマンドを新しい環境で実行

### Key Syscalls Used

- **syscall.CLONE_NEWUTS**: 新しいUTS名前空間 (hostname分離)
- **syscall.CLONE_NEWPID**: 新しいPID名前空間 (プロセスID分離)  
- **syscall.CLONE_NEWNS**: 新しいマウント名前空間 (ファイルシステム分離)
- **syscall.Mount**: ファイルシステムのマウント
- **syscall.PivotRoot**: ルートファイルシステムの変更

### Error Handling

- `must()` function: エラーが発生した場合は即座にpanicで終了
- 各プロセスで個別にエラーハンドリングを実装