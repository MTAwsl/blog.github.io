import base58
import struct


def cubicRoot(n) :
    start = 0
    end = n
    e = 0.00000001
    while (True) :
        mid = (start + end) / 2
        error = abs(n - (mid * mid * mid))
        if (error <= e) :
            return mid
        if ((mid * mid * mid) > n) :
            end = mid
        else :
            start = mid

def find_cube_root(n):
    lo = 0
    hi = 1 << ((n.bit_length() + 2) // 3)
    while lo < hi:
        mid = (lo+hi) >> 1
        if mid**3 < n:
            lo = mid+1
        else:
            hi = mid
    return lo

STANDARD_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
CUSTOM_ALPHABET = b'9876432*Flag{n0T-EA5y=to+f1Nd}BCDGHJKLMPQRSUVWXYZbcehijkmp'

with open("./enc.dat.bak", "rb") as f:
    buf = f.read()

encrypted, key = buf.split(b"FLAG")

key = base58.b58decode(key.translate(bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)))

print("Key: " + int(find_cube_root(int.from_bytes(key, "big"))).to_bytes(8, "big").decode())

# Key: N5f0cuS_

with open("./sbox.bin", "rb") as f:
    buf = f.read()

it = struct.iter_unpack("<I", buf)
sbox = []
while True:
    try:
        sbox.append(next(it)[0])
    except StopIteration:
        break

def crypt_64bit_down(x, y):
    for i in range(0x11, 1, -1):
        z = sbox[i] ^ x
        x = sbox[0x012 + ((z>>24)&0xff)];
        x = sbox[0x112 + ((z>>16)&0xff)] + x;
        x = sbox[0x212 + ((z>> 8)&0xff)] ^ x;
        x = sbox[0x312 + ((z>> 0)&0xff)] + x;
        x = y ^ x
        y = z
    x = x ^ sbox[1]
    y = y ^ sbox[0]
    return (x, y)

def byteswap32(a):
    return (a >> 8) & 0xFF00 | (a << 8) & 0xFF0000 | (a << 24) & 0xFF000000 | (a >> 24) & 0xFF

it = struct.iter_unpack("<I", encrypted)
encbuf = []
while True:
    try:
        encbuf.append(next(it)[0])
    except StopIteration:
        break

for i in range(0, len(encbuf), 2):
    a, b = encbuf[i], encbuf[i+1]
    a, b = crypt_64bit_down(byteswap32(a), byteswap32(b))
    a = byteswap32(a)
    b = byteswap32(b)
    encbuf[i: i+2] = [a, b]

data = b''
for i in range(0, len(encbuf), 2):
    data += struct.pack("<I", encbuf[i+1])
    data += struct.pack("<I", encbuf[i])

print(data.decode())