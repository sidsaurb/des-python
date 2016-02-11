#!usr/bin/python

import pyDES
import random
import constants
import json
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

PInverse = inversePerm(constants.perm)

def getKeySetRound3(i1, o1, i2, o2, sBoxNumber):
    POutputXor = pyDES.xor(pyDES.xor(pyDES.xor(o1[32:64], o2[32:64]), i1[0:32]),
                           i2[0:32])
    SOutputXor = pyDES.shuffle(POutputXor, PInverse, "Binary")
    SOutputXorInt = int(SOutputXor[sBoxNumber*4:(sBoxNumber+1)*4].to01(), 2)
    ExpandInput1 = pyDES.expand(o1[0:32])
    ExpandInput2 = pyDES.expand(o2[0:32])
    SInputXor = pyDES.xor(ExpandInput1, ExpandInput2)
    SInputXorInt = int(SInputXor[sBoxNumber*6:(sBoxNumber+1)*6].to01(), 2)
    #print XORProfile
    #print XORProfile[str(sBoxNumber)][str(SInputXorInt)][str(SOutputXorInt)]
    pairs = XORProfile[str(sBoxNumber)][str(SInputXorInt)][str(SOutputXorInt)][0]

    keyset = set()
    for item in pairs:
        possibleKey = item[0] ^ int(ExpandInput1[sBoxNumber*6:(sBoxNumber+1)*6].to01(), 2)
        keyset.add(format(possibleKey, 'b').zfill(6))
    return keyset


xor_file = open("XORprofile.json", 'r')
a = xor_file.read()
xor_file.close()

XORProfile = json.loads(a)

print "Breaking round 3..\n"

keys = []
for i in range(0,8):
    print "sBox %d keysets:" % (i + 1)
    s = set()
    while len(s) != 1:
        inp1 = generateRandomData()
        inp2 = generateRandomData()
        out1 = pyDES.encrypt(inp1, 3)
        out2 = pyDES.encrypt(inp2, 3)
        keyset = getKeySetRound3(inp1, out1, inp2, out2, i)
        print keyset
        if len(s) == 0:
            s = keyset
        else:
            s.intersection_update(keyset)
    print "intersection: %s \n" % str(s)
    keys.append(s.pop())

print "original key: %s " % pyDES.keys[2].to01()
print "found key   : %s " % ''.join(i for i in keys)
