import json

import aiofiles
import pytest
import skia
from dynamicadaptor.DynamicConversion import formate_message

from dynrender_skia.Core import DynRender


@pytest.mark.asyncio
async def test_dyn_render_run(shared_cache, resource_dir):
    async with aiofiles.open(resource_dir / "message.json", encoding="utf-8") as f:
        resp = await f.read()

    message_data = json.loads(resp)
    message = await formate_message("web", message_data["data"]["item"])
    if message is None:
        return
    img = await DynRender(static_path=str(shared_cache)).run(message)

    img = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)
