from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO
from pathlib import Path
from requests import get, post
from requests import Response as HttpResponse

import json
import memcache
import os
import transform
import version

static_path: str = Path(__file__).parent.parent / 'resources' / 'static'
tmpl_path: str = Path(__file__).parent.parent / 'resources' / 'html'

app: FastAPI = FastAPI()
app.mount('/static', StaticFiles(directory=static_path), name='static')

tmpl: Jinja2Templates = Jinja2Templates(directory=tmpl_path)

@app.get('/')
async def index(request: Request, style: str = None, token: str = None):

    env_token: str = os.getenv('VTG_TOKEN', None)
    if env_token is not None:
        if env_token != token:
            return JSONResponse(
                status_code=401, 
                content={
                    'error': 'Invalid access token!'
                }
            )

    return tmpl.TemplateResponse('index.html', {
        'request': request,
        'version': version.__version__,
        'style': style,
        'token': token,
        'baseurl': request.base_url
    })

@app.get('/tile/{zoom}/{x}/{y}.png')
async def tile(zoom: int, x: int, y: int, style: str, token: str = None, width: int = 256, height: int = 256):

    env_token: str = os.getenv('VTG_TOKEN', None)
    if env_token is not None:
        if env_token != token:
            return JSONResponse(
                status_code=401, 
                content={
                    'error': 'Invalid access token!'
                }
            )
    
    try:

        # define HTTP helpers
        http_headers: dict = {
            'User-Agent': f"VectorTileProxy/{version.__version__}"
        }

        cache: memcache.Client = memcache.Client(['vector-tile-cache:11211'], debug=0)

        cache_style_key = f"style:{style}"
        cache_tile_key = f"{cache_style_key}/tile:{zoom}:{x}:{y}:{width}:{height}"

        # transform ZXY slippy map tile into bounding box
        bbox: tuple[float, float, float, float] = transform.tile_bbox(zoom, x, y)
        bbox_str: str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        # fetch desired style
        style_data: any = cache.get(cache_style_key)
        if style_data is None:
            style_response: HttpResponse = get(
                style, 
                headers=http_headers
            )

            cache.set(
                cache_style_key, 
                style_response.content, 
                time=600
            )

            style_data = style_response.json()
        else:
            style_data = json.loads(style_data)

        # combine all parameters and style to render everything by the
        # vector-tile-renderer
        tile_data: any = cache.get(cache_tile_key)
        if tile_data is None:
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
                    tile_response.content,
                    time=600
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
