import math

def tile_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """
    Calculates the bounding box (W,S,E,N) of a Slippy Map tile (Z/X/Y).
    
    Parameters:
        z (int): Zoom level
        x (int): Tile X coordinate
        y (int): Tile Y coordinate
    
    Returns:
        (west, south, east, north) in decimal degrees
    """
    n = 2 ** z

    def lon(x):
        return x / n * 360.0 - 180.0

    def lat(y):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))

    west = lon(x)
    east = lon(x + 1)
    north = lat(y)
    south = lat(y + 1)

    return west, south, east, north