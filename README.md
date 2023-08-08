# DynRender-skia
使用skia渲染BiliBili动态
更新页面效果的优先级会很低
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
pip install dynamicadaptor dynrender-skia
```

## 测试

```python
import httpx
import asyncio
import skia
from dynrender_skia.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message

# 定义异步函数，用于执行Web测试
async def web_test():
    dyn_id = "440646043801479846"
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}&features=itemOpusStyle"
    headers = {
        "referer": f"https://t.bilibili.com/{dyn_id}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    
    # 发起HTTP请求并解析JSON响应
    message_json = httpx.get(url, headers=headers).json()

    # 格式化消息数据
    message_formate = await formate_message("web", message_json["data"]["item"])

    # 使用DynRender执行动态渲染
    img = await DynRender().run(message_formate)

    # 将渲染后的图像转换为Skia Image对象
    img = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)

    # 保存图像为PNG文件
    img.save("1.png")

# 当文件作为主程序执行时
if __name__ == "__main__":
    asyncio.run(web_test())


```

## 效果展示
![示例图片](https://i0.hdslb.com/bfs/new_dyn/a1fae2ca072ef96bc66dc12ea6de569c37815472.png)
