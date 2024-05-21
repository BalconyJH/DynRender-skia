import httpx
import asyncio
import skia
from dynrender_skia.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message


# 定义异步函数，用于执行Web测试
async def web_test():
    dyn_id = "933799634791301126"
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}&features=itemOpusStyle"
    headers = {
        "referer": f"https://t.bilibili.com/{dyn_id}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
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