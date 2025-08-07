# docker

## in the beggining
- containerというのは容れ物である。船のcontainerと同じ意味
- 一つの場所からもう一つの場所へと移動するためのもの。
- 依存関係を気にしなくて良くなる

## building a container
- 以下の三つが重要
namespaces, cgroups and layered filesystems

- 6 namespaces
  - PID: mapping table
  - MNT <= this is most important
  - NET: net
  - UTS: hostname and domain name
  - IPC: inter process communication
  - USER: これのおかげでルート権限での実行が可能となる

## CGROUPS

## Layered Filesystems
- 効率的な隔離の実現のため
