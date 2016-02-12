#!usr/bin/python

import pyDES
import random
import constants
import json
from bitarray import bitarray

def generateRandomDataPair():
    data1 = ""
    data2 = ""
    for i in range(0,32):
        data1 += str(random.randrange(0,2))
        data2 += str(random.randrange(0,2))
    for i in range(0,32):
	x = random.randrange(0,2)
        data1 += str(x)
	data2 += str(x)
    return [bitarray(data1), bitarray(data2)]

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

PInverse = inversePerm(constants.perm)

def getKeySetRound3(i1, o1, i2, o2, sNo):
    POutputXor = o1[32:64] ^ o2[32:64] ^ i1[0:32] ^ i2[0:32]
    SOutputXor = pyDES.shuffle(POutputXor, PInverse, "Binary")
    SOutputXorInt = int(SOutputXor[sNo * 4 : (sNo + 1) * 4].to01(), 2)
    ExpandOutput1 = pyDES.expand(o1[0:32])
    ExpandOutput2 = pyDES.expand(o2[0:32])
    SInputXor = ExpandOutput1 ^ ExpandOutput2
    SInputXorInt = int(SInputXor[sNo * 6 : (sNo + 1) * 6].to01(), 2)
    #print XORProfile
    #print XORProfile[str(sBoxNumber)][str(SInputXorInt)][str(SOutputXorInt)]
    pairs = XORProfile[str(sNo)][str(SInputXorInt)][str(SOutputXorInt)][0]
    #print pairs
    keyset = set()
    #print SInputXorInt, SOutputXorInt
    for item in pairs:
        possibleKey = item[0] ^ int(ExpandOutput2[sNo * 6 : (sNo + 1) * 6].to01(), 2)
	#print item[0] ^ item[1]
	#print possibleKey
	#a = pyDES.mapSBox(constants.sBoxes[sBoxNumber], bitarray(format(item[0], 'b').zfill(6)))
	#b = pyDES.mapSBox(constants.sBoxes[sBoxNumber], bitarray(format(item[1], 'b').zfill(6)))
	#print item[0] ^ item[1], int((a ^ b).to01(), 2)
        keyset.add(format(possibleKey, 'b').zfill(6))
    return keyset


xor_file = open("XORprofile.json", 'r')
a = xor_file.read()
xor_file.close()

XORProfile = json.loads(a)

#print XORProfile["0"]["52"]["13"]
print "Breaking round 3..\n"

pairs = []	# for caching previous encryptions
keys = []
for i in range(0, 8):
    print "sBox %d keysets:" % (i + 1)
    s = set()
    temp = list(pairs)
    while len(s) != 1:
        if len(temp) != 0:
            x = temp.pop()
            inp = [x[0], x[1]]
            out1 = x[2]
            out2 = x[3]
        else:
            inp = generateRandomDataPair()
            out1 = pyDES.encrypt(inp[0], 3)
            out2 = pyDES.encrypt(inp[1], 3)
        pairs.append([inp[0], inp[1], out1, out2])
        keyset = getKeySetRound3(inp[0], out1, inp[1], out2, i)
        print keyset
        if len(s) == 0:
            s = keyset
        else:
            s.intersection_update(keyset)
    print "intersection: %s \n" % str(s)
    keys.append(s.pop())

print "original key r3: %s " % pyDES.keys[2].to01()
print "found key    r3: %s " % ''.join(i for i in keys)

