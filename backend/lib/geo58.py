#!/usr/bin/python3
import logging
import sys

log = logging.getLogger(__name__)
log.setLevel('DEBUG')

LOG_TO_CONSOLE = True
if LOG_TO_CONSOLE:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


class Geo58():
    """Geo58 class to hold and convert geo-coordinates in z/x/y format and
    base58 encoded short strings."""

    alph = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    class Geo58Exception(ValueError):
        """Values out of range"""
        pass

    def __init__(self, zoom=20, lat=None, lon=None, x=None, y=None, g58=None):
        """Initialize a Geo58 instance"""
        self._zoom = zoom
        self._lat = lat or x
        self._lon = lon or y
        self._int = None
        self._merged_int = None
        self._geo58 = g58

        log.debug("_init: {} {} {}".format(zoom, self._lat, self._lon))

        if not self._geo58:
            self._geo58 = self._coordsToGeo58(self._zoom, self._lat, self._lon)

        if (not self._zoom or not self._lat or not self._lon) and self._geo58:
            self._zoom, self._lat, self._lon = self._geo58ToCoords(self._geo58)
            # log.debug("{} {} {}, geo58: {}".format(self._zoom, self._lat, self._lon, self._geo58))
            self._validate_coords(self._zoom, self._lat, self._lon)

        self._merged_int = self._merge_x_y(self._lat, self._lon)
        # print(self._unmerge_x_y(self._merged_int))
        log.debug("_init: {} {} {}".format(self._zoom, self._lat, self._lon))
        log.debug("{} {} {}, geo58: {}".format(self._zoom, self._lat, self._lon, self._geo58))


    def get_geo58(self):
        """Return base58 geo string (geo58)"""
        return self._geo58

    def get_coordinates(self):
        """Return std coordinates (z,x,y)"""
        return (self._zoom, self._lat, self._lon)

    def _int2base58(self, number):
        """Convert an integer into a base58 encoded string"""
        self._int = number
        base58str = []
        while number:
            base58str.append(Geo58.alph[int(number % 58)])
            number = int(number / 58)
        base58str.reverse()
        return "".join(base58str)

    def _base582int(self, b58_str):
        """Convert a base58 encoded string into an integer"""
        i = 0
        for c in b58_str:
            i *= 58
            i += Geo58.alph.index(c)

        self._int = int(i)
        log.debug(hex(self._int))

        return int(i)

    def _validate_coords(self, zoom, x, y):#, from_geo58=False):
        """Coordinates must be within certain range:
        zoom can be between [20 and 5],
        x (lat) can be between  90.00000 and  -90.00000,
        y (lon) can be between 180.00000 and -180.00000
        """
        log.debug("validate: {} {} {}".format(zoom, x, y))
        x = int(float(x)*100000)
        y = int(float(y)*100000)
        # log.debug("validate: {} {} {}".format(zoom, x, y))
        # if from_geo58:
        #     x = x - 9000000
        #     y = y - 18000000
        #     # log.debug("validate: {} {} {}".format(zoom, x, y))
        zoom = int(float(zoom) + 0.5) # round to closest full int
        if x < -9000000 or x > 9000000:
            raise Geo58.Geo58Exception("lat (x) is out of range {} {} {}".format(zoom, x, y))
        if y < -18000000 or y > 18000000:
            raise Geo58.Geo58Exception("lon (y) is out of range {} {} {}".format(zoom, x, y))
        if zoom < 5 or zoom > 20: # 4bit - 20 is no-zoom given
            raise Geo58.Geo58Exception("zoom is out of range (5-20)")
        log.debug("valid: {} {} {}".format(zoom, x, y))

    def _convertCoordsToInt(self, x, y, z=20):
        """Converts coordinates and zoom to one integer.
        """
        log.debug("_convertCoordsToInt: {} {} {}".format(z, x, y))
        self._validate_coords(z,x,y)

        # x is mapped from -90 to +90 -> 0 to 180
        # y is mapped from -180 to 180 -> 0 to 360
        x = int(float(x)*100000+  9000000)
        y = int(float(y)*100000+ 18000000)
        z = int(float(z) + 0.5) # round to closest full int
        # # max values
        # x = -8999999
        # y = -17999999
        # z = 12

        z = (z - 20) * -1 # zoom 20 = b0x0

        # TODO verschränken
        coord = z << 51 | x << 26 | y #25 bits
        coord = int(coord)
        return coord

    def _convertIntToCoords(self, i):
        zoom = (i & (15 << 25+26)) >> (51)
        x = (i & (2**25-1 << 26)) >> (26) # 2**24-1 << 25
        y =  i & (2**26-1) # 67108863 # 2**25-1
        x = float(x- 9000000)/100000
        y = float(y-18000000)/100000
        z = (zoom *-1 + 20)
        z = int(z)
        log.debug("_convertIntToCoords: {} {} {}".format(z, x, y))
        return (z,x,y)

    def _merge_x_y(self, x,y):
        """Merge x and y coordinates
        will merge x and y coordinates to one integer to keep them similar for
        locations that are close to each other.
        e.g:
        x =  4512345
        y = 12309876
        will become: 0142531029384756
        """
        if x < 0 or y < 0:
            raise Geo58.Geo58Exception("x and y must be > 0: {} {}".format(x, y))
        x = x *100_000
        y = y *100_000
        d = 10_000_000
        i = 0
        while d > 0:
            # print("d: {}".format(d))
            a = x // d * 10
            b = y // d
            i += a + b
            # print("i, a, b, x, y : {} {} {} {} {}".format(i,a,b,x,y))
            x %= d
            y %= d
            d //= 10
            if d > 0:
                i = i * 100
            # print("i: {}".format(i))
        return int(i)

    def _unmerge_x_y(self, i):
        x = 0
        y = 0
        d = 10_000_000_000_000_000
        a = None
        b = None
        while d > 10:
            # print("===================")
            d //= 10
            a = i // d
            x = x + a
            d //= 10
            b = (i // d) % 10
            y = y + b
            if d > 10:
                i = i % d
                x *= 10
                y *= 10
            # print("x,y : {} {}, i, d: {} {}, a, b: {} {}".format(x,y, i, d,a,b))
        return (x,y)

    def _coordsToGeo58(self, zoom,x,y):
        i = self._convertCoordsToInt(x,y,zoom)
        return self._int2base58(i)

    def _geo58ToCoords(self, g58):
        i = self._base582int(g58)
        z,x,y = self._convertIntToCoords(i)
        log.debug("_get58ToCoords: {} {} {}".format(z, x, y))
        return (z,x,y)

# #     x,y,zoom = coords
# def test(coords):
#     print("\033[1m",coords,"\033[m")
#     print("self._convertCoordsToInt: ", end="")
#     i = self._convertCoordsToInt(x,y,zoom)
#     print(i)
#     print("self.int2base58: ", end="")
#     b58 = self.int2base58(i)
#     print("\033[1m",b58,"\033[m", end="")
#     print(" ... length: ","\033[1m",len(b58),"\033[m")
#     print("self._base582int: ", end="")
#     i = self._base582int(b58)
#     print(i)
#     print("self._convertIntToCoords: ", end="")
#     coord2 = self._convertIntToCoords(i)
#     print(coord2)
#     assert x == coord2[0]
#     assert y == coord2[1]
#     assert zoom == coord2[2]
#     print(coords, "... ok")
#     print("="*79)
#
# zoom,x,y = 19,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 18,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 17,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 16,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 15,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 14,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 13,47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 12,47.12346,15.12345
# test((x,y,zoom))
# # zoom,x,y = 11,47.12346,15.12345
# # test((x,y,zoom))
# zoom,x,y = 15,-47.12346,15.12345
# test((x,y,zoom))
# zoom,x,y = 19,47.12346,-15.12345
# test((x,y,zoom))
# zoom,x,y = 17,-47.12346,-15.12345
# test((x,y,zoom))
# zoom,x,y = 14,-89.12346,-179.12345
# test((x,y,zoom))
# zoom,x,y = 14,89.12346,-179.12345
# test((x,y,zoom))
# zoom,x,y = 14,-89.12346,179.12345
# test((x,y,zoom))
# zoom,x,y = 12,90,180
# test((x,y,zoom))
# zoom,x,y = 19,-90,180
# test((x,y,zoom))
# zoom,x,y = 19,-90,-180
# test((x,y,zoom))
# zoom,x,y = 19,90,-180
# test((x,y,zoom))

def test(lat=0.0,lon=0.0,zoom=5,coords=None):
    if not coords:
        log.debug("="*10+"> {}, {}, {}".format(lat,lon,zoom))
        g58 = Geo58(lat=lat,lon=lon,zoom=zoom)
    else:
        log.debug("="*10+"> {}, {}, {}".format(coords[0],coords[1],coords[2]))
        g58 = Geo58(lat=coords[0],lon=coords[1],zoom=coords[2])

    # g58 = Geo58(lat=45.07071,lon=15.43951,zoom=5)
    # print(hex(g58._int))
    # print(g58._lat, g58._lon)
    log.debug("="*10+"> "+Geo58(g58=g58._geo58)._geo58)


def main():
    # test(lat=87.07071,lon=175.43951,zoom=15)
    # zoom,x,y = 19,10.12346,0.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 18,10.12347,0.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 17,47.12346,15.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 16,47.12346,15.12344
    # test(coords=(x,y,zoom))
    # zoom,x,y = 15,77.12346,15.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 14,-17.12346,150.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 13,7.12346,1.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 12,47.12346,15.12345
    # test(coords=(x,y,zoom))
    # # zoom,x,y = 11,47.12346,15.12345
    # # test(coords=(x,y,zoom))
    # zoom,x,y = 15,-47.12346,15.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 19,47.12346,-15.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 17,-47.12346,-15.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 14,-89.12346,-179.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 14,89.12346,-179.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 14,-89.12346,179.12345
    # test(coords=(x,y,zoom))
    # zoom,x,y = 12,90,180
    # test(coords=(x,y,zoom))
    # zoom,x,y = 19,-90,180
    # test(coords=(x,y,zoom))
    # zoom,x,y = 19,-90,-180
    # test(coords=(x,y,zoom))
    # zoom,x,y = 19,90,-180
    # test(coords=(x,y,zoom))
    g58 = Geo58(x=47.12345, y=123.09876)
    print(g58._int)
    print(g58._merged_int)

if __name__ == "__main__":
    main()
