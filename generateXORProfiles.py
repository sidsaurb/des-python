#!/usr/bin/python

import constants
import json
import pyDES
from bitarray import bitarray
import csv

a = dict()

for i in range(0, 8):
    a[i] = dict()
    for j in range(0,64):
        a[i][j] = dict()
        for k in range(0,16):
            a[i][j][k] = [[], 0]


def inversePerm(perm):
    output = []
    for i in range(0, 32):
        output.append(perm.index(i + 1) + 1)
    return output

collapse = inversePerm(constants.expand)
#print collapse

def getInputOutput(sNo, input, output):
    inpbin = bitarray("0" * sNo * 6 + format(input, 'b').zfill(6)
                      + "0" * (7 - sNo) * 6)
    rhs_xor = pyDES.shuffle(inpbin, collapse, "Binary")
    outbin = bitarray("0" * sNo * 4 + format(output, 'b').zfill(4)
                      + "0" * (7 - sNo) * 4)
    lhs_xor = pyDES.shuffle(outbin, constants.perm, "Binary")
    return (("%0.8X" % int(lhs_xor.to01(), 2)),
            ("%0.8X" % int(rhs_xor.to01(), 2)))


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
            #if out_xor_val != 0 and a[i][inp_xor_val][out_xor_val][1] > maximum:
            #maximum = a[i][inp_xor_val][out_xor_val][1]

target = open("XORprofile.json", 'w')
target.write(json.dumps(a))
target.close()

target1 = open("XORTable.csv", 'w')

heading = [["xx", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0A",
            "0B","0C", "0D", "0E", "0F"]]

for i in range(0, 8):
    target1.write("s" + str(i + 1) + " table\n")
    b = csv.writer(target1, delimiter=" ")
    b.writerows(heading)
    maximum = 0
    max_row = 0
    max_column = 0
    for j in range(0, 64):
        row = [("%0.2X" % j)]
        for k in range(0, 16):
            # 2nd check to ensure that the j is of form 00xx00
            if a[i][j][k][1] > maximum and (j == 12 or j == 8 or j == 4):
                maximum = a[i][j][k][1]
                max_row = j
                max_column = k
            row.append(("%0.2d" % a[i][j][k][1]))
        b.writerows([row])
    target1.write("Maximum = %d for row = %0.2X and column = %0.2X\n"
                  % (maximum, max_row, max_column))
    inp = getInputOutput(i, max_row, max_column)
    target1.write("left = %s\tright = %s\n" % (inp[0], inp[1]))
    target1.write("\n")

#print getInputOutput(1, 4, 7)
#print getInputOutput(1, 12, 5)
target1.close()

#print maximum
#print a

