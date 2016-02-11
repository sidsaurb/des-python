#!usr/bin/python

import pyDES
import random
import constants
from bitarray import bitarray


def generateRandomData():
    data = ""
    for i in range(0,64):
        data += str(random.randrange(0,2))
    return bitarray(data)

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

def mapSBoxInverse(output, sBoxNumber):
    result = []
    output = output[sBoxNumber * 4 : (sBoxNumber + 1) * 4]
    out = int(output.to01(), 2)
    sBox = constants.sBoxes[sBoxNumber]
    i = 0
    for item in sBox:
        j = 0
        for a in item:
            if out == a:
                row = format(i, 'b').zfill(2)
                column = format(j, 'b').zfill(4)
                result.append(bitarray(row[0] + column + row[1]))
            j += 1
        i += 1
    return result

PInverse = inversePerm(constants.perm)

def getKeySetRound1(input, output, sBoxNumber):
    POutput = pyDES.xor(output[0:32], input[0:32])
    SOutput = pyDES.shuffle(POutput, PInverse, "Binary")
    XOROutput = mapSBoxInverse(SOutput, sBoxNumber)
    ExpandOutput = pyDES.expand(input[32:64])
    outsBox = ExpandOutput[sBoxNumber * 6 : (sBoxNumber + 1) * 6]
    keyset = set()
    for i in range(0,4):
        keyset.add(pyDES.xor(outsBox, XOROutput[i]).to01())
    return keyset

def getKeySetRound2(input, output, sBoxNumber):
    POutput = pyDES.xor(output[32:64], input[0:32])
    SOutput = pyDES.shuffle(POutput, PInverse, "Binary")
    XOROutput = mapSBoxInverse(SOutput, sBoxNumber)
    ExpandOutput = pyDES.expand(input[32:64])
    outsBox = ExpandOutput[sBoxNumber * 6 : (sBoxNumber + 1) * 6]
    keyset = set()
    for i in range(0,4):
        keyset.add(pyDES.xor(outsBox, XOROutput[i]).to01())
    return keyset


print "Breaking round 1..\n"

keys = []
for i in range(0,8):
    print "sBox %d keysets:" % (i + 1)
    s = set()
    while len(s) != 1:
        inp = generateRandomData()
        out = pyDES.encrypt(inp, 2)
        keyset = getKeySetRound1(inp, out, i)
        print keyset
        if len(s) == 0:
            s = keyset
        else:
            s.intersection_update(keyset)
    print "intersection: %s \n" % str(s)
    keys.append(s.pop())

foundkeyr1 = ''.join(i for i in keys)

print "original key r1: %s " % pyDES.keys[0].to01()
print "found key r1   : %s\n" % foundkeyr1


print "Breaking round 2..\n"

keys = []
for i in range(0,8):
    print "sBox %d keysets:" % (i + 1)
    s = set()
    while len(s) != 1:
        inp = generateRandomData()
        inp1 = pyDES.encryptDES(inp, 1, [bitarray(foundkeyr1)])
        out = pyDES.encrypt(inp, 2)
        keyset = getKeySetRound2(inp1, out, i)
        print keyset
        if len(s) == 0:
            s = keyset
        else:
            s.intersection_update(keyset)
    print "intersection: %s \n" % str(s)
    keys.append(s.pop())

foundkeyr2 = ''.join(i for i in keys)

print "original key r2: %s " % pyDES.keys[1].to01()
print "found key r2   : %s" % foundkeyr2
