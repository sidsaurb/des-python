#!usr/bin/python

import pyDES
import random
import constants
import json
from bitarray import bitarray
import binascii

# generate pairs (L0, R0) and (L0', R0') such that
# L0 xor L0' = 0x00808200
# R0 xor R0' = 0x60000000

def generateRandomDataPair():
    data1 = bitarray()
    data2 = bitarray()
    binary = bitarray(pyDES.hex_to_binary("00808200"))
    for item in binary:
	x = bitarray(str(random.randrange(0,2)))
	data1.extend(x)
	y = bitarray("0") if not item else bitarray("1")
	data2.extend(x ^ y)
    
    binary = bitarray(pyDES.hex_to_binary("60000000"))
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


pairs = []	# for caching previous encryptions

minIterations = 7
maxIterations = 40 # gives correct result almost everytime for iterations >= 33

print "\nOriginal key for r4 is: %s " % pyDES.keys[3].to01()
print "Correct count indicates how many times we got correct results out of 50 trials\n"

print "Breaking round 4.."
print "Starting with interations in range (%d, %d)\n" % (minIterations, maxIterations)

for iters in range(minIterations, maxIterations + 1):
    correct = 0
    incorrect = 0
    for trial in range(0, 50):
	keys = []
        for i in range(0, 8):
            #print "\nsBox %d key counts: " % (i + 1)
            count = dict()
            for attempts in range(0, iters):
                if len(pairs) == iters:
	            out1 = pairs[attempts][0]
	            out2 = pairs[attempts][1]
	        else:
                    inp = generateRandomDataPair()
                    out1 = pyDES.encrypt(inp[0], 4)
                    out2 = pyDES.encrypt(inp[1], 4)
	            #pairs.append([out1, out2])
        
	        keyset = getKeySetRound4(out1, out2, i)
	        for item in keyset:
	            if item in count:
	                count[item] += 1
	            else:
		        count[item] = 1
            maximum = getMaximum(count)
            keys.append(format(maximum, 'b').zfill(6))
            #print count
	key =  ''.join(i for i in keys)
	#print key
        if key == pyDES.keys[3].to01():
	    correct += 1
	else:
            incorrect += 1
    print "Iterations %d stats:" % iters
    print "Correct %d, Incorrect %d\n" % (correct, incorrect)

#print "\noriginal key r4: %s " % pyDES.keys[3].to01()
#print "found key    r4: %s \n" % ''.join(i for i in keys)

