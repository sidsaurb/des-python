#!/usr/bin/python

import constants
import json
import pyDES
from bitarray import bitarray

a = dict()

for i in range(0, 8):
    a[i] = dict()
    for j in range(0,64):
        a[i][j] = dict()
        for k in range(0,16):
            a[i][j][k] = [[], 0]


for i in range(0, 8):
    for j in range(0, 64):
        for k in range(0, 64):
            a1 = bitarray(format(j, 'b').zfill(6))
            a2 = bitarray(format(k, 'b').zfill(6))
            out1 = pyDES.mapSBox(constants.sBoxes[i], a1)
            out2 = pyDES.mapSBox(constants.sBoxes[i], a2)
            out_xor = out1 ^ out2
            out_xor_val = int(out_xor.to01(), 2)
            inp_xor_val = j ^ k
            a[i][inp_xor_val][out_xor_val][0].append((j, k))
            a[i][inp_xor_val][out_xor_val][1] += 1

target = open("XORprofile.json", 'w')
target.write(json.dumps(a))
target.close()
#print a

