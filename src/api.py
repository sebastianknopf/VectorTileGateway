from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
from requests import get, post
from requests import Response as HttpResponse

import transform
import version

app = FastAPI()

@app.get('/')
async def index():
    return {"message": "Vector Tile Gateway"}

@app.get('/tile/{zoom}/{x}/{y}.png')
async def tile(zoom: int, x: int, y: int, style: str, width: int = 256, height: int = 256):

    try:

        # define HTTP helper variables
        http_headers: dict = {
            'User-Agent': f"VectorTileProxy/{version.__version__}"
        }
        
        # transform ZXY slippy map tile into bounding box
        bbox: tuple[float, float, float, float] = transform.tile_bbox(zoom, x, y)
        bbox_str: str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        # fetch desired style
        style: HttpResponse = get(
            style, 
            headers=http_headers
        )

        # combine all parameters and style to render everything by the
        # vector-tile-renderer
        response: HttpResponse = post(
            'http://vector-tile-renderer:80/render', 
            json={
                'style': style.json(),
                'bounds': bbox_str,
                'width': width,
                'height': height
            },
            headers=http_headers
        )

        # check status response of vector-tile-renderer
        if response.status_code == 200:

            # return rendered tile as PNG file
            return StreamingResponse(
                BytesIO(response.content), 
                media_type='image/png'
            )
        else:

            # return error response
            return JSONResponse(
                status_code=response.status_code, 
                content={
                    'error': response.content.decode('utf-8')
                }
            )

    except Exception as ex:
        
        return JSONResponse(
            status_code=500, 
            content={
                'error': str(ex)
            }
        )
