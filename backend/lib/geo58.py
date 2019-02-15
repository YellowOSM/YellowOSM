#!/usr/bin/python3
def int2base58(arg):
    alph = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    base58str = []
    while arg:
        base58str.append(alph[int(arg % 58)])
        arg = int(arg / 58)
    base58str.reverse()
    return "".join(base58str)

def base582int(arg):
    alph = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    i = 0
    for c in arg:
        i *= 58
        i += alph.index(c)
    return int(i)

def convertCoordsToInt(x,y,z=19):
    x = int(float(x)*100000)
    y = int(float(y)*100000)
    z = int(float(z) + 0.5) # round to closest full int
    # # max values
    # x = -8999999
    # y = -17999999
    # z = 12

    if x < -9000000 or x > 9000000:
        raise ValueError()
    if y < -18000000 or y > 18000000:
        raise ValueError()
    if z < 12 or z > 19:
        raise ValueError()
    z = (z - 19) * -1 # zoom 19 = b0x0

    minusx = True if x < 0 else False
    minusy = True if y < 0 else False
    x = abs(x)
    y = abs(y)
    coord = minusx << (1+3+24+25) | minusy << (3+24+25) | z << (24+25) | x << (25) | y
    coord = int(coord)
    return coord

def convertIntToCoords(i):
    minusx = True if i & (1 << (1+3+24+25)) else False
    minusy = True if i & (1 << (3+24+25)) else False
    zoom = (i & (7 << 24+25)) >> (24+25)
    x = (i & 562949919866880) >> (25) # 2**24-1 << 25
    y = i & 33554431 # 2**25-1
    x = x*-1 if minusx else x
    y = y*-1 if minusy else y
    x = float(x)/100000
    y = float(y)/100000
    z = (zoom *-1 + 19)
    z = int(z)
    return (x,y,z)

def coordsToGeo58(zoom,x,y):
    i = convertCoordsToInt(x,y,zoom)
    return int2base58(i)

def geo58ToCoords(g58):
    i = base582int(g58)
    x,y,z = convertIntToCoords(i)
    return (z,x,y)

def test(coords):
    x,y,zoom = coords
    print("\033[1m",coords,"\033[m")
    print("convertCoordsToInt: ", end="")
    i = convertCoordsToInt(x,y,zoom)
    print(i)
    print("int2base58: ", end="")
    b58 = int2base58(i)
    print("\033[1m",b58,"\033[m", end="")
    print(" ... length: ","\033[1m",len(b58),"\033[m")
    print("base582int: ", end="")
    i = base582int(b58)
    print(i)
    print("convertIntToCoords: ", end="")
    coord2 = convertIntToCoords(i)
    print(coord2)
    assert x == coord2[0]
    assert y == coord2[1]
    assert zoom == coord2[2]
    print(coords, "... ok")
    print("="*79)
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
