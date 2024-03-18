import json

import pytest
import skia
from dynamicadaptor.DynamicConversion import formate_message


@pytest.mark.asyncio
async def test_dyn_render_run(shared_cache, resource_dir, dynrender_instance):
    with open(resource_dir / "message.json", "r", encoding="utf-8") as f:
        resp = json.load(f)

    message = await formate_message("web", resp["data"]["item"])
    img = await dynrender_instance.run(message)

    img = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)
