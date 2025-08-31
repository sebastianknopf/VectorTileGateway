from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from io import BytesIO

import requests

import transform

app = FastAPI()

@app.get('/')
async def index():
    return {"message": "Vector Tile Gateway"}

@app.get('/tile/{zoom}/{x}/{y}.png')
async def tile(zoom: int, x: int, y: int, style: str, width: int = 256, height: int = 256):

    style = requests.get(style)

    bbox = transform.tile_bbox(zoom, x, y)

    response = requests.post('http://vector-tile-renderer:80/render', json={
        "style": style,
        "bounds": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "width": width,
        "height": height
    })

    if response.status_code != 200:
        return {"error": response.content.decode()}

    return StreamingResponse(BytesIO(response.content), media_type="image/png")