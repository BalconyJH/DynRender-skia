# DynRender-skia
使用skia渲染BiliBili动态

# 注意

Linux用户在导入skia-python包时可能会遇到以下报错
```bash
libGL.so.1: cannot open shared object file: No such file or directory
```
## 解决方法

> ubuntu用户

```bash

apt install libgl1

```
> ArchLinux用户

```bash
pacman -S libgl
```
> centos用户
```bash
yum install mesa-libGL -Y

```
