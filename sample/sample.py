from time import perf_counter
import skia
from dynrender.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message
import asyncio
import httpx
import json
import sys
sys.path.append("/home/dmc/Python/DynamicRender")


async def web_test():
    dyn_id = "832529605898273125"
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}&features=itemOpusStyle"
    headers = {
        "referer": f"https://t.bilibili.com/{dyn_id}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }
    message_json = httpx.get(url, headers=headers).json()
    message_formate = await formate_message("web", message_json["data"]["item"])
    start = perf_counter()
    img = await DynRender(font_family="Microsoft YaHei UI").run(message_formate)
    print(perf_counter()-start)
    img = skia.Image.fromarray(img,colorType=skia.ColorType.kRGBA_8888_ColorType)


    img.save("1.png")


if __name__ == "__main__":
    asyncio.run(web_test())
