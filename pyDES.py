#!/usr/bin/python

import constants
import binascii
from bitarray import bitarray

# This algorithm currently doesn't applying initial
# permutation and its inverse to blocks


def byte_to_binary(n):
        return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary(h):
        return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def shuffle(input, perm, mode=None):
    if mode is None:
        output = ""
        for c in perm:
            output += input[c - 1]
        return output
    else:
        output = bitarray()
        for c in perm:
            output.append(input[c - 1])
        return output

def rotate(l,n):
        return l[n:] + l[:n]

def generateKeys(keys_components, shifts, perm):
    left = keys_components[0][0]
    right = keys_components[0][1]
    for item in shifts:
        left = rotate(left, item)
        right = rotate(right, item)
        keys_components.append((left, right))
    keys = [];
    for item in keys_components[1:17]:
        keys.append(bitarray(shuffle(item[0] + item[1], perm)))
    return keys

def round(input, multiple):
    output = input
    rem = 8 - len(input) % multiple
    if rem >= 2:
        output += "\x0d\x0a" + "\x00" * (rem - 2)
    else:
        output += "\x0d\x0a" + "\x00" * (rem + 6)
    return output

def expand(input):
    return shuffle(input, constants.expand, "Binary")

def xor(a, b):
    length = len(a)
    output = bitarray()
    for i in range(0, length):
        output.append(a[i] ^ b[i])
    return output

def mapSBox(sBox, input):
    row = bitarray()
    row.append(input[0])
    row.append(input[5])
    column = input[1:5]
    row_int = int(row.to01(), 2)
    column_int = int(column.to01(),2)
    out = format(sBox[row_int][column_int], 'b').zfill(4)
    return bitarray(out)

def f(input, sBoxes, key, perm):
    expanded_right = expand(input)
    xored_right = xor(expanded_right, key)
    sboxed_right = bitarray()
    for j in range(0, 8):
        sBox = sBoxes[j]
        sboxed_right.extend(mapSBox(sBoxes[j], xored_right[j*6:(j+1)*6]))
    permuted_right = shuffle(sboxed_right, perm, "Binary")
    return permuted_right

def encryptDES(input, steps, sBoxes, perm, keys):
    blocks = len(input)/64
    output = bitarray()
    for i in range(0, blocks):
        output.extend(encryptDESAux(input[i*64:(i+1)*64],steps, sBoxes, perm, keys))
    return output

def encryptDESAux(input, steps, sBoxes, perm, keys):
    left = input[0:32]
    right = input[32:64]
    for i in range(0, steps):
        permuted_right = f(right, sBoxes, keys[i], perm)
        leftnew = right
        right = xor(left, permuted_right)
        left = leftnew
    output = bitarray()
    output.extend(left)
    output.extend(right)
    return output

def decryptDES(input, steps, sBoxes, perm, keys):
    blocks = len(input)/64
    output = bitarray()
    for i in range(0, blocks):
        output.extend(decryptDESAux(input[i*64:(i+1)*64], steps, sBoxes, perm, keys))
    return output

def decryptDESAux(input, steps, sBoxes, perm, keys):
    left = input[0:32]
    right = input[32:64]
    for i in range(0, steps):
        permuted_right = f(left, sBoxes, keys[steps - 1 - i], perm)
        rightnew = left
        left = xor(right, permuted_right)
        right = rightnew
    output = bitarray()
    output.extend(left)
    output.extend(right)
    return output

def encrypt(input, steps):
    return encryptDES(input, steps, constants.sBoxes, constants.perm, keys)


key_hex = "0E329232EA6D0D73"
key_bin = hex_to_binary(key_hex)

K0 = shuffle(key_bin, constants.pc1)
keys_components = [(K0[0:28], K0[28:56])]
keys = generateKeys(keys_components, constants.shifts, constants.pc2)


if __name__ == "__main__":
    data = "abcdefg"
    data = round(data, 8)
    rounds = 5

    data_binary = bitarray(''.join(format(ord(i),'b').zfill(8) for i in data))

    cipher_bitarray = encrypt(data_binary, rounds)
    cipher_binary = cipher_bitarray.to01()
    cipher_hex = '%0*X' % ((len(cipher_binary) + 3) // 4, int(cipher_binary, 2))

    message_bitarray = decryptDES(cipher_bitarray, rounds, constants.sBoxes, constants.perm, keys)
    message_binary = message_bitarray.to01()
    message_readable = ''.join(chr(int(message_binary[i:i+8], 2))
                            for i in xrange(0, len(message_binary), 8))

    index = message_readable.rfind('\r\n')
    if index != -1:
       message_readable = message_readable[:index]

    print "Cipher text: " + cipher_hex
    print "Decrypted text: " + message_readable

