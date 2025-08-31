from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
from requests import get, post
from requests import Response as HttpResponse

import json
import memcache
import transform
import version

app = FastAPI()

@app.get('/')
async def index():
    return {"message": "Vector Tile Gateway"}

@app.get('/tile/{zoom}/{x}/{y}.png')
async def tile(zoom: int, x: int, y: int, style: str, width: int = 256, height: int = 256):

    try:

        # define HTTP helpers
        http_headers: dict = {
            'User-Agent': f"VectorTileProxy/{version.__version__}"
        }

        cache = memcache.Client(['vector-tile-cache:11211'], debug=0)

        cache_style_key = f"style:{style}"
        cache_tile_key = f"{cache_style_key}/tile:{zoom}:{x}:{y}:{width}:{height}"

        # transform ZXY slippy map tile into bounding box
        bbox: tuple[float, float, float, float] = transform.tile_bbox(zoom, x, y)
        bbox_str: str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        # fetch desired style
        style_response: any = cache.get(cache_style_key)
        if style_response is None:
            style_response = get(
                style, 
                headers=http_headers
            ).json()

            cache.set(
                cache_style_key, 
                json.dumps(style_response), 
                time=600
            )

            style_data = style_response
        else:
            style_data = json.loads(style_response)

        # combine all parameters and style to render everything by the
        # vector-tile-renderer
        tile_response: any = cache.get(cache_tile_key)
        if tile_response is None:
            tile_response: HttpResponse = post(
                'http://vector-tile-renderer:80/render', 
                json={
                    'style': style_data,
                    'bounds': bbox_str,
                    'width': width,
                    'height': height
                },
                headers=http_headers
            )

            # check status response of vector-tile-renderer
            if tile_response.status_code == 200:

                # set tile data and put into cache
                cache.set(
                    cache_tile_key,
                    tile_response.content
                )

                tile_data: bytes = tile_response.content
            else:

                # return error response
                return JSONResponse(
                    status_code=tile_response.status_code, 
                    content={
                        'error': tile_response.content.decode('utf-8')
                    }
                )
        else:
            tile_data: bytes = tile_response
        
        # return rendered tile as PNG file
        return StreamingResponse(
            BytesIO(tile_data), 
            media_type='image/png'
        )

    except Exception as ex:
        
        return JSONResponse(
            status_code=500, 
            content={
                'error': str(ex)
            }
        )
