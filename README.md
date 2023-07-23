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

apt install libgl1-mesa-glx

```
> ArchLinux用户

```bash
pacman -S libgl
```
> centos用户
```bash
yum install mesa-libGL -y

```

# 使用方法

## 安装必要依赖
```bash
pip install dynamicadaptor skia-python
```

## 测试

```python
import httpx
import asyncio
import skia
from dynrender_skia.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message


async def web_test():
    dyn_id = "440646043801479846"
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}&features=itemOpusStyle"
    headers = {
        "referer": f"https://t.bilibili.com/{dyn_id}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    message_json = httpx.get(url, headers=headers).json()

    message_formate = await formate_message("web", message_json["data"]["item"])
    img = await DynRender().run(message_formate)
    img = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)
    img.save("1.png")

if __name__ == "__main__":
    asyncio.run(web_test())

```

## 效果展示
![示例图片](https://i0.hdslb.com/bfs/new_dyn/a1fae2ca072ef96bc66dc12ea6de569c37815472.png)
