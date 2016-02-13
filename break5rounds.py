#!usr/bin/python

import pyDES
import random
import constants
import json
from bitarray import bitarray
import binascii
import operator

# generate pairs (L0, R0) and (L0', R0') such that
# they satisfy one of the following properties
#
# non zero input via s1:
# L0 xor L0' = 0x00808200
# R0 xor R0' = 0x60000000
# leads to R1 xor R1' = 0x00 with p = 14/64
#
# noon zero input via s2:
# L0 xor L0' = 0x40080000
# R0 xor R0' = 0x04000000
# leads to R1 xor R1' = 0x00 with p = 16/64
#
# non zero input via s3:
# L0 xor L0' = 0x04000100
# R0 xor R0' = 0x00200000
# leads to R1 xor R1' = 0x00 with p = 12/64
#
# non zero input via s4:
# L0 xor L0' = 0x00401000
# R0 xor R0' = 0x00020000
# leads to R1 xor R1' = 0x00 with p = 12/64
#
# non zero input via s5:
# L0 xor L0' = 0x00040080
# R0 xor R0' = 0x00002000
# leads to R1 xor R1' = 0x00 with p = 10/64
#
# non zero input via s6:
# L0 xor L0' = 0x00200008
# R0 xor R0' = 0x00000400
# leads to R1 xor R1' = 0x00 with p = 16/64
#
# non zero input via s7:
# L0 xor L0' = 0x00100001
# R0 xor R0' = 0x00000060
# leads to R1 xor R1' = 0x00 with p = 14/64
#
# non zero input via s8:
# L0 xor L0' = 0x00020820
# R0 xor R0' = 0x00000002
# leads to R1 xor R1' = 0x00 with p = 12/64
#
# refer generateXORProfiles.py

'''
inputs = [("00808200", "60000000"),
          ("40080000", "04000000"),
          ("04000100", "00200000"),
          ("00401000", "00020000"),
          ("00040080", "00002000"),
          ("00200008", "00000400"),
          ("00100001", "00000060"),
          ("00020820", "00000002")]
'''

pairsNeeded = 0

'''
inputs = [("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000"),
          ("00808200", "60000000")]
'''

inputs = [("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400"),
          ("00200008", "00000400")]


def prettyPrintKey(string, length):
    return ' '.join(string[i:i+length] for i in xrange(0,len(string),length))

def generateRandomDataPair(sBoxNo):
    global pairsNeeded
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
    pairsNeeded += 1
    return [bitarray(data1), bitarray(data2)]

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

PInverse = inversePerm(constants.perm)

def getKeySetRound5(o1, o2, sNo):
    POutputXor = o1[32:64] ^ o2[32:64] ^ bitarray(pyDES.hex_to_binary(inputs[sNo][0]))
    SOutputXor = pyDES.shuffle(POutputXor, PInverse, "Binary")
    SOutputXorInt = int(SOutputXor[sNo * 4 : (sNo + 1) * 4].to01(), 2)
    ExpandOutput1 = pyDES.expand(o1[0:32])
    ExpandOutput2 = pyDES.expand(o2[0:32])
    SInputXor = ExpandOutput1 ^ ExpandOutput2
    SInputXorInt = int(SInputXor[sNo * 6 : (sNo + 1) * 6].to01(), 2)
    pairs = XORProfile[str(sNo)][str(SInputXorInt)][str(SOutputXorInt)][0]
    keyset = set()
    for item in pairs:
        possibleKey = item[0] ^ int(ExpandOutput1[sNo * 6 : (sNo + 1) * 6].to01(), 2)
        keyset.add(possibleKey)
    return keyset

def getMaximum(countList):
    return max(countList.iteritems(), key=operator.itemgetter(1))[0]


xor_file = open("XORprofile.json", 'r')
a = xor_file.read()
xor_file.close()

XORProfile = json.loads(a)

print "Breaking round 5.."

pairs = [] # for caching previous encryptions
keys = []
for i in range(0, 8):
    print "\nsBox %d key counts: " % (i + 1)
    count = dict()
    temp = list(pairs)
    attempts = 0
    while attempts < 28: # 28 by chernoff bound
        if len(temp) != 0:
            x = temp.pop()
            out1 = x[0]
            out2 = x[1]
        else:
            inp = generateRandomDataPair(i)
            out1 = pyDES.encrypt(inp[0], 5)
            out2 = pyDES.encrypt(inp[1], 5)
            pairs.append([out1, out2])
        keyset = getKeySetRound5(out1, out2, i)
        if len(keyset) != 64:
            for item in keyset:
                if item in count:
                    count[item] += 1
                else:
                    count[item] = 1
            attempts += 1
    maximum = getMaximum(count)
    keys.append(format(maximum, 'b').zfill(6))
    print count

key =  ' '.join(i for i in keys)

print "\noriginal key r5: %s " % prettyPrintKey(pyDES.keys[4].to01(), 6)
print "found key    r5: %s \n" % ' '.join(i for i in keys)
print "total encryptions needed: %d \n" % pairsNeeded

