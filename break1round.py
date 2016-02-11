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

def getKeySet(input, output, sBoxNumber):
    POutput = pyDES.xor(output[32:64], input[0:32])
    SOutput = pyDES.shuffle(POutput, PInverse, "Binary")
    XOROutput = mapSBoxInverse(SOutput, sBoxNumber)
    ExpandOutput = pyDES.expand(input[32:64])
    outsBox = ExpandOutput[sBoxNumber * 6 : (sBoxNumber + 1) * 6]
    keyset = set()
    for i in range(0,4):
        keyset.add(pyDES.xor(outsBox, XOROutput[i]).to01())
    return keyset

keys = []
for i in range(0,8):
    print "sBox %d keysets:" % (i + 1)
    s = set()
    while len(s) != 1:
        inp = generateRandomData()
        out = pyDES.encrypt(inp, 1)
        keyset = getKeySet(inp, out, i)
        print keyset
        if len(s) == 0:
            s = keyset
        else:
            s.intersection_update(keyset)
    print "intersection: %s \n" % str(s)
    keys.append(s.pop())

print "original key: %s " % pyDES.keys[0].to01()

print "found key   : %s " % ''.join(i for i in keys)

