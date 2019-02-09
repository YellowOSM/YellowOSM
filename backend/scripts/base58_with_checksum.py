#!/usr/bin/python3
# checksum_version:
# 2 base 9
# 1 base 2

checksum_version = 1
base = 2
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
    """return geo58-int including checksum"""
    x = int(float(x)*100000)
    y = int(float(y)*100000)
    z = int(zoom)
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
    x = x if x > 0 else x*-1
    y = y if y > 0 else y*-1
    i = minusx << (1+3+24+25) | minusy << (3+24+25) | z << (24+25) | x << (25) | y
    i = int(i)
    # resp.media = {
    # media = {
    #     "zoom": int(zoom),
    #     "x": x,
    #     "y": y,
    #     "z": z,
    #     "xbin": bin(x),
    #     "ybin": bin(y),
    #     "zbin": bin(z),
    #     "xbitlength": x.bit_length(),
    #     "ybitlength": y.bit_length(),
    #     "zbitlength": z.bit_length(),
    #     "coord": coord,
    #     "coordbin": bin(coord),
    #     # "coord_b58": coord_b58,
    #     "length": coord.bit_length(),
    #     }
    return i*base + checksum(i)

def convertIntToCoords(i):
    """convert geo58 including checksum"""
    cs = i % base # get checksum
    i = i // base
    if checksum(i) != cs:
        # invalid checksum
        print("invalid checksum")
        return None
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

def checksum(i,v=1):
    """returns the checksum for geo58"""
    if v == 2 :
        base = 9
        cs = 0
        c = 1
        while i > 0:
            cs += (i % base) * c
            i = i // base
            c += 1
            if i < base:
                i = 0
        return cs % base
    elif v == 1:
        base = 2
        cs = 0
        # c = 1
        while i > 0:
            cs += (i % base) #* c
            i = i // base
            # c += 1
            if i < base:
                i = 0
        return cs % base
    else:
        return None

def test(coords):
    x,y,zoom = coords
    print("\033[1m",coords,"\033[m")
    print("convertCoordsToInt: ", end="")
    i = convertCoordsToInt(x,y,zoom)
    print(i)
    print("int2base58: ", end="")
    b58 = int2base58(i)
    print("\033[1m",b58,"\033[m", end="")
    print("bitlength: {}".format(i.bit_length()), end="")
    print(" ... length: ","\033[1m",len(b58),"\033[m")
    cs = checksum(i)
    print("checksum: {}".format(cs))
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

def test2(coords):
    x,y,zoom = coords
    print("\033[1m",coords,"\033[m")
    print("convertCoordsToInt: ", end="")
    i = convertCoordsToInt(x,y,zoom)
    print(i)
    print("int2base58: ", end="")
    b58 = int2base58(i)
    print("\033[1m",b58,"\033[m", end="")
    print("bitlength: {}".format(i.bit_length()), end="")
    print(" ... length: ","\033[1m",len(b58),"\033[m")
    cs = checksum(i)
    print("checksum: {}".format(cs))
    print("base582int: ", end="")
    s = list(b58)
    s[2] = '1'
    b58 = "".join(s)
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

zoom,x,y = 19,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 18,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 17,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 16,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 15,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 14,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 13,47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 12,47.12346,15.12345
test((x,y,zoom))
# zoom,x,y = 11,47.12346,15.12345
# test((x,y,zoom))
zoom,x,y = 15,-47.12346,15.12345
test((x,y,zoom))
zoom,x,y = 19,47.12346,-15.12345
test((x,y,zoom))
zoom,x,y = 17,-47.12346,-15.12345
test((x,y,zoom))
zoom,x,y = 14,-89.12346,-179.12345
test((x,y,zoom))
zoom,x,y = 14,89.12346,-179.12345
test((x,y,zoom))
zoom,x,y = 14,-89.12346,179.12345
test((x,y,zoom))
zoom,x,y = 12,90,180
test((x,y,zoom))
zoom,x,y = 19,-90,180
test((x,y,zoom))
zoom,x,y = 19,-90,-180
test((x,y,zoom))
zoom,x,y = 19,90,-180
test((x,y,zoom))
zoom,x,y = 14,-89.12000,179.00000
test((x,y,zoom))
zoom,x,y = 14,-89.12346,0.0
test((x,y,zoom))
# base 9
# print(convertIntToCoords(base582int("HKVDZvdyYn")))
# print(convertIntToCoords(base582int("HKWDZvdyYn")))
# print(convertIntToCoords(base582int("JKVDZvdyYn")))
# print(convertIntToCoords(base582int("HKVDZvdyYm")))
# print(convertIntToCoords(base582int("HKVDYvdyYn")))
# base 4
# print(convertIntToCoords(base582int("61mbTNFrXH")))
# print(convertIntToCoords(base582int("61mbTNFrXJ")))
# print(convertIntToCoords(base582int("61mbTNFrYH")))
# print(convertIntToCoords(base582int("61mpTNFrXH")))
# print(convertIntToCoords(base582int("62mbTNFrXH")))
# print(convertIntToCoords(base582int("61mbSNFrXH")))
# base 2 with c
# print(convertIntToCoords(base582int("4GJEWGFRBV")))
# print(convertIntToCoords(base582int("4GJEWGFRBW")))
# print(convertIntToCoords(base582int("3GJEWGFRBV")))
# print(convertIntToCoords(base582int("4GJEWGFRPV")))
# print(convertIntToCoords(base582int("4GKEWGFRBV")))
# print(convertIntToCoords(base582int("4GJFWGFRBV")))
# print(convertIntToCoords(base582int("4GJEW6FRBV")))
# print(convertIntToCoords(base582int("4GJEWGFBBV")))
# base 2 plain
print(convertIntToCoords(base582int("4GJEWGFRBW")))
print(convertIntToCoords(base582int("4GJEWGFRBV")))
print(convertIntToCoords(base582int("3GJEWGFRBW")),"<-- ähhhh. gut geraten.")
print(convertIntToCoords(base582int("4GHEWGFRBW")))
print(convertIntToCoords(base582int("4GJRWGFRBW")))
print(convertIntToCoords(base582int("4GJFWGFRBW")))

#zoom,x,y = 14,-89.0000,10.10000
#test2((x,y,zoom))
