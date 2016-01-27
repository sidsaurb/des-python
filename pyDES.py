#!/usr/bin/python

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
    if rem > 2:
        output += "\x0d\x0a" + "\x00" * (rem - 2)
    else:
        output += "\x0d\x0a" + "\x00" * (rem + 6)
    return output

def expand(input):
    exp = [32,1,2,3,4,5,
           4,5,6,7,8,9,
           8,9,10,11,12,13,
           12,13,14,15,16,17,
           16,17,18,19,20,21,
           20,21,22,23,24,25,
           24,25,26,27,28,29,
           28,29,30,31,32,1]
    return shuffle(input, exp, "Binary")

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


key_hex = "0E329232EA6D0D73"
key_bin = hex_to_binary(key_hex)

pc1 = [57,49,41,33,25,17,9,
       1,58,50,42,34,26,18,
       10,2,59,51,43,35,27,
       19,11,3,60,52,44,36,
       63,55,47,39,31,23,15,
       7,62,54,46,38,30,22,
       14,6,61,53,45,37,29,
       21,13,5,28,20,12,4]

pc2 = [14,17,11,24,1,5,
       3,28,15,6,21,10,
       23,19,12,4,26,8,
       16,7,27,20,13,2,
       41,52,31,37,47,55,
       30,40,51,45,33,48,
       44,49,39,56,34,53,
       46,42,50,36,29,32]

s1 = [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
      [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
      [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
      [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]]

s2 = [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
      [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
      [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
      [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]]

s3 = [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
      [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
      [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
      [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]]

s4 = [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
      [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
      [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
      [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]]

s5 = [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
      [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
      [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
      [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]]

s6 = [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
      [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
      [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
      [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]]

s7 = [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
      [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
      [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
      [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]]

s8 = [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
      [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
      [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
      [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]

perm = [16,7,20,21,
        29,12,28,17,
        1,15,23,26,
        5,18,31,10,
        2,8,24,14,
        32,27,3,9,
        19,13,30,6,
        22,11,4,25]

sBoxes = [s1, s2, s3, s4, s5, s6, s7, s8]
shifts = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

K0 = shuffle(key_bin, pc1)
keys_components = [(K0[0:28], K0[28:56])]
keys = generateKeys(keys_components, shifts, pc2)

data = "This is a plaintext"
data = round(data, 8)

data_binary = bitarray(''.join(format(ord(i),'b').zfill(8) for i in data))

cipher_bitarray = encryptDES(data_binary, 16, sBoxes, perm, keys)
cipher_binary = cipher_bitarray.to01()
cipher_hex = '%0*X' % ((len(cipher_binary) + 3) // 4, int(cipher_binary, 2))

message_bitarray = decryptDES(cipher_bitarray, 16, sBoxes, perm, keys)
message_binary = message_bitarray.to01()
message_readable = ''.join(chr(int(message_binary[i:i+8], 2))
                           for i in xrange(0, len(message_binary), 8))

print "Cipher text: " + cipher_hex
print "Decrypted text: " + message_readable

