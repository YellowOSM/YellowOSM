#!/usr/bin/python3
import logging
import sys

log = logging.getLogger(__name__)
log.setLevel('DEBUG')

LOG_TO_CONSOLE = False
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
        self._geo58 = g58

        log.debug("_init: {} {} {}".format(zoom, self._lat, self._lon))

        if not self._geo58:
            self._geo58 = self._coordsToGeo58(self._zoom, self._lat, self._lon)

        if (not self._zoom or not self._lat or not self._lon) and self._geo58:
            self._zoom, self._lat, self._lon = self._geo58ToCoords(self._geo58)
            # log.debug("{} {} {}, geo58: {}".format(self._zoom, self._lat, self._lon, self._geo58))
            self._validate_coords(self._zoom, self._lat, self._lon)

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

    def _validate_coords(self, zoom, x, y):
        """Coordinates must be within certain range:
        zoom can be between [20 and 5],
        x (lat) can be between  90.00000 and  -90.00000,
        y (lon) can be between 180.00000 and -180.00000
        """
        log.debug("validate: {} {} {}".format(zoom, x, y))
        x = int(float(x)*100000)
        y = int(float(y)*100000)
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
        x = int( (float(x) + 90 ) * 100_000)
        y = int( (float(y) + 180) * 100_000)

        merged_coords = self._bin_merge_x_y(x, y)

        z = int(float(z) + 0.5) # round to closest full int
        z = (z - 20) * -1 # zoom 20 = b0x0

        # coord = z << 51 | x << 26 | y #25 bits
        coord = z << 51 | merged_coords
        coord = int(coord)
        return coord

    def _convertIntToCoords(self, i):
        zoom = (i & (15 << 25+26)) >> (51)
        x, y = self._bin_unmerge_x_y(i & 0x7ffffffffffff)
        # x = (i & (2**25-1 << 26)) >> (26) # 2**24-1 << 25
        # y =  i & (2**26-1) # 67108863 # 2**25-1
        x = float(x- 9000000)/100000
        y = float(y-18000000)/100000
        z = (zoom *-1 + 20)
        z = int(z)
        log.debug("_convertIntToCoords: {} {} {}".format(z, x, y))
        return (z,x,y)


    def _bin_merge_x_y(self, x, y):
        """merge two integers (x: 25 bit, y: 26 bit) on binary level so that
        LSB and MSB are close to each other.
        This will make geo-location codes for locations that are close to
        each other similar.
        """
        x = int(x)
        y = int(y)
        a = 0
        b = 0
        mask = 0x1
        for s in range(1,26):
            # print("s: {}, mask: {}".format(s, hex(mask)))
            a |= ((x & mask) << s)
            mask = mask << 1
        mask = 0x1
        for s in range(0,27):
            b |= ((y & mask) << s)
            mask = mask << 1
        i = a | b
        log.debug("binary merged int: {}".format(i))
        return int(i)

    def _bin_unmerge_x_y(self, i):
        """unmerge two integers from one 51 bit int (x: 25 bit, y: 26 bit)"""
        a = 0
        b = 0
        mask = 0x2
        for s in range(1,27):
            # print("i: {}, a: {}, s: {}, mask: {}".format(i, a, s, hex(mask)))
            a |= ((i & mask) >> s)
            mask = mask << 2

        mask = 0x1
        for s in range(0,27):
            # print("i: {}, b: {}, s: {}, mask: {}".format(i, b, s, hex(mask)))
            b |= ((i & mask) >> s)
            mask = mask << 2
        log.debug("binary reverted coords: {},{}, {},{}".format(a,b,a-9000000,b-18000000))
        return (int(a), int(b))

    def _coordsToGeo58(self, zoom, x, y):
        i = self._convertCoordsToInt(x, y, zoom)
        return self._int2base58(i)

    def _geo58ToCoords(self, g58):
        i = self._base582int(g58)
        z,x,y = self._convertIntToCoords(i)
        log.debug("_get58ToCoords: {} {} {}".format(z, x, y))
        return (z,x,y)
# end Geo58 class


def test(lat=0.0,lon=0.0,zoom=5,coords=None):
    log.debug("---"*20)
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
    # zoom,x,y = 17,47.12346,15.12344
    # test(coords=(x,y,zoom))
    # zoom,x,y = 17,47.12346,15.12346
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
    g58 = Geo58(x=47.07070, y=15.43950)
    g58 = Geo58(x=47.07068, y=15.44130)
    g58 = Geo58(x=47.07068, y=15.44117)
    g58 = Geo58(g58='4dHEin8gh')
    g58 = Geo58(x=47.07068, y=15.44130, zoom=19)
    g58 = Geo58(x=47.07068, y=15.44117, zoom=19)

# if __name__ == "__main__":
#     main()
