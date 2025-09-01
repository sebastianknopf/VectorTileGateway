# VectorTileGateway
A lightweight Dockerized service to render MapLibre/Mapbox vector tiles on demand and serve them as PNG images.
Ideal for testing styles, generating raster tiles for clients without vector support, or building a custom vector tile proxy.

- Accepts Z/X/Y tile requests via [FastAPI](https://github.com/fastapi/fastapi).
- Uses [mbgl-renderer](https://github.com/consbio/mbgl-renderer) to render tiles according to your MapLibre (former: Mapbox) style.
- Caches loaded styles and tiles using a [memcached](https://github.com/memcached/memcached) instance.
- Returns rendered tiles directly to the client as PNG using an [uvicorn](https://github.com/encode/uvicorn) server.
- Handles multiple requests in parallel and can be deployed easily with Docker Compose.

CURRENTLY UNDER DEVELOPMENT . . . .

## Usage
Coming soon ...

## Known Issues / Limitations
Coming soon ...

## Contributions
Coming soon ...

## License
This project is licensed under the Apache License. See [LICENSE.md](LICENSE.md) for more information.