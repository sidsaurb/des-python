#!usr/bin/python

import pyDES
import random
import constants
import json
from bitarray import bitarray
import binascii

# generate pairs (L0, R0) and (L0', R0') such that
#
# for s1:
# L0 xor L0' = 0x00808200
# R0 xor R0' = 0x60000000
#
# for s2:
# L0 xor L0' = 0x40080000
# R0 xor R0' = 0x04000000
#
# for s3:
# L0 xor L0' = 0x04000100
# R0 xor R0' = 0x00200000
#
# for s4:
# L0 xor L0' = 0x00401000
# R0 xor R0' = 0x00020000
#
# for s5:
# L0 xor L0' = 0x00040080
# R0 xor R0' = 0x00002000
#
# for s6:
# L0 xor L0' = 0x00200008
# R0 xor R0' = 0x00000400
#
# for s7:
# L0 xor L0' = 0x00100001
# R0 xor R0' = 0x00000060
#
# for s8:
# L0 xor L0' = 0x00020820
# R0 xor R0' = 0x00000002
#
# refer generateXORProfiles.py

inputs = [("00808200", "60000000"),
          ("40080000", "04000000"),
          ("04000100", "00200000"),
          ("00401000", "00020000"),
          ("00040080", "00002000"),
          ("00200008", "00000400"),
          ("00100001", "00000060"),
          ("00020820", "00000002")]

def prettyPrintKey(string, length):
    return ' '.join(string[i:i+length] for i in xrange(0,len(string),length))

def generateRandomDataPair(sBoxNo):
    data1 = bitarray()
    data2 = bitarray()
    binary = bitarray(pyDES.hex_to_binary(inputs[sBoxNo][0]))
    for item in binary:
	x = bitarray(str(random.randrange(0,2)))
	data1.extend(x)
	y = bitarray("0") if not item else bitarray("1")
	data2.extend(x ^ y)

    binary = bitarray(pyDES.hex_to_binary(inputs[sBoxNo][1]))
    for item in binary:
	x = bitarray(str(random.randrange(0,2)))
	data1.extend(x)
	y = bitarray("0") if not item else bitarray("1")
	data2.extend(x ^ y)

    return [bitarray(data1), bitarray(data2)]

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

PInverse = inversePerm(constants.perm)

def getKeySetRound4(o1, o2, sNo):
    POutputXor = o1[32:64] ^ o2[32:64] ^ bitarray(pyDES.hex_to_binary("60000000"))
    SOutputXor = pyDES.shuffle(POutputXor, PInverse, "Binary")
    SOutputXorInt = int(SOutputXor[sNo * 4 : (sNo + 1) * 4].to01(), 2)
    ExpandOutput1 = pyDES.expand(o1[0:32])
    ExpandOutput2 = pyDES.expand(o2[0:32])
    SInputXor = ExpandOutput1 ^ ExpandOutput2
    SInputXorInt = int(SInputXor[sNo * 6 : (sNo + 1) * 6].to01(), 2)
    pairs = XORProfile[str(sNo)][str(SInputXorInt)][str(SOutputXorInt)][0]
    keyset = set()
    for item in pairs:
        possibleKey = item[0] ^ int(ExpandOutput2[sNo * 6 : (sNo + 1) * 6].to01(), 2)
        keyset.add(possibleKey)
    return keyset

def getMaximum(countList):
    maximum = 0
    maxkey = 0
    for item in range(0, 64):
        if item in countList:
            if countList[item] > maximum:
                maximum = countList[item]
                maxkey = item
    return maxkey

xor_file = open("XORprofile.json", 'r')
a = xor_file.read()
xor_file.close()

XORProfile = json.loads(a)


print "Breaking round 4.."

keys = []
for i in range(0, 8):
    print "\nsBox %d key counts: " % (i + 1)
    count = dict()
    for attempts in range(0, 6):
        inp = generateRandomDataPair(i)
        out1 = pyDES.encrypt(inp[0], 4)
        out2 = pyDES.encrypt(inp[1], 4)
        keyset = getKeySetRound4(out1, out2, i)
        for item in keyset:
            if item in count:
                count[item] += 1
            else:
                count[item] = 1
    maximum = getMaximum(count)
    keys.append(format(maximum, 'b').zfill(6))
    print count

key =  ' '.join(i for i in keys)

print "\noriginal key r4: %s " % prettyPrintKey(pyDES.keys[3].to01(), 6)
print "found key    r4: %s \n" % ' '.join(i for i in keys)

