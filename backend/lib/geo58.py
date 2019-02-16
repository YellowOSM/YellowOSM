#!/usr/bin/python3
import logging

log = logging.getLogger(__name__)
log.setLevel('DEBUG')

class Geo58():
    """Geo58 class to hold and convert geo-coordinates in z/x/y format and
    base58 encoded short strings."""

    alph = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    class Geo58Exception(ValueError):
        """Values out of range"""
        pass

    def __init__(self, zoom=19, lat=None, lon=None, x=None, y=None, g58=None):
        """Initialize a Geo58 instance"""
        self._zoom = zoom
        self._lat = lat or x
        self._lon = lon or y
        self._geo58 = g58

        if not self._geo58:
            self._geo58 = self._coordsToGeo58(self._zoom, self._lat, self._lon)

        if (not self._zoom or not self._lat or not self._lon) and self._geo58:
            self._zoom, self._lat, self._lon = self._geo58ToCoords(self._geo58)
            self._validate_coords(self._zoom, self._lat, self._lon)

        log.debug("{} {} {}, geo58: {}".format(self._zoom, self._lat, self._lon, self._geo58))


    def get_geo58(self):
        """Return base58 geo string (geo58)"""
        return self._geo58

    def get_coordinates(self):
        """Return std coordinates (z,x,y)"""
        return (self._zoom, self._lat, self._lon)

    def _int2base58(self, number):
        """Convert an integer into a base58 encoded string"""
        base58str = []
        while number:
            base58str.append(Geo58.alph[int(number % 58)])
            number = int(number / 58)
        base58str.reverse()
        return "".join(base58str)

    def _base582int(self, b58_str):
        """Convert a base58 encoded string into an integer"""
        # alph = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        i = 0
        for c in b58_str:
            i *= 58
            i += Geo58.alph.index(c)
        return int(i)

    def _validate_coords(self, zoom, x, y):
        log.debug("validate: {} {} {}".format(zoom, x, y))
        x = int(float(x)*100000)
        y = int(float(y)*100000)
        zoom = int(float(zoom) + 0.5) # round to closest full int
        if x < -9000000 or x > 9000000:
            raise Geo58.Geo58Exception("lat (x) is out of range")
        if y < -18000000 or y > 18000000:
            raise Geo58.Geo58Exception("lon (y) is out of range")
        if zoom < 12 or zoom > 19:
            raise Geo58.Geo58Exception("zoom is out of range (12-19)")

    def _convertCoordsToInt(self, x, y, z=19):
        self._validate_coords(z,x,y)

        x = int(float(x)*100000)
        y = int(float(y)*100000)
        z = int(float(z) + 0.5) # round to closest full int
        # # max values
        # x = -8999999
        # y = -17999999
        # z = 12

        z = (z - 19) * -1 # zoom 19 = b0x0

        minusx = True if x < 0 else False
        minusy = True if y < 0 else False
        x = abs(x)
        y = abs(y)
        # coord = minusx << (1+3+24+25) | minusy << (3+24+25) | z << (24+25) | x << (25) | y
        coord = minusx << 53 | minusy << 52 | z << 49 | x << 25 | y
        coord = int(coord)
        return coord

    def _convertIntToCoords(self, i):
        # minusx = True if i & (1 << (1+3+24+25)) else False
        minusx = True if i & (1 << (53)) else False
        # minusy = True if i & (1 << (3+24+25)) else False
        minusy = True if i & (1 << (52)) else False
        zoom = (i & (7 << 24+25)) >> (49)
        x = (i & 562949919866880) >> (25) # 2**24-1 << 25
        y = i & 33554431 # 2**25-1
        x = x*-1 if minusx else x
        y = y*-1 if minusy else y
        x = float(x)/100000
        y = float(y)/100000
        z = (zoom *-1 + 19)
        z = int(z)
        return (x,y,z)

    def _coordsToGeo58(self, zoom,x,y):
        i = self._convertCoordsToInt(x,y,zoom)
        return self._int2base58(i)

    def _geo58ToCoords(self, g58):
        i = self._base582int(g58)
        x,y,z = self._convertIntToCoords(i)
        return (z,x,y)

#     x,y,zoom = coords
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
