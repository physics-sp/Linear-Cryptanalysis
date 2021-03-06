#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from basic_SPN import *
import linear_cryptanalysis_lib as lc_lib
from math import fabs, ceil

# modify accordingly
def do_sbox(number):
    return sbox[number]

# modify accordingly
def do_inv_sbox(number):
    return sbox_inv[number]

# modify accordingly
def do_pbox(state):
    state_temp = 0
    for bitIdx in range(0,16):
        if(state & (1 << bitIdx)):
            state_temp |= (1 << pbox[bitIdx])
    state = state_temp
    return state

def main():

    NUM_P_C_PAIRS = 10000
    SBOX_BITS  = 4
    NUM_SBOXES = 4
    NUM_ROUNDS = 4
    MIN_BIAS = 0.008
    MAX_BLOCKS_TO_BF = 3

    lc_lib.initialize(NUM_P_C_PAIRS,
                      SBOX_BITS,
                      NUM_SBOXES,
                      NUM_ROUNDS,
                      MIN_BIAS,
                      MAX_BLOCKS_TO_BF,
                      do_sbox,
                      do_inv_sbox,
                      do_pbox)


    print('analizing cipher...')
    # there is no need to do this each time
    start = time.time_ns()
    linear_aproximations = lc_lib.analize_cipher()
    end = time.time_ns()
    print("done, took {:d} ns".format(end - start))
    if len(linear_aproximations) == 0:
        exit('no linear aproximations could be found!')

    print('\nbest linear aproximations:')
    # just for demonstration
    for i in range(10):
        try:
            print(linear_aproximations[i])
        except IndexError:
            break

    print('\nthe linear aproximation with the best bias will be used:')
    # you may choose anyone you like
    linear_aproximation = linear_aproximations[0]

    # just for demonstration
    end_sboxs = ', '.join(list(map(str, linear_aproximation[2])))
    print('ε: {:f}\nstart: sbox n°{:d}\nend sboxes:{}'.format(linear_aproximation[0], linear_aproximation[1][0], end_sboxs))
    Nl = ceil( pow(pow(linear_aproximation[0], -1), 2))
    print('\nneeded plaintext/ciphertext pairs (according to Matsui\'s paper):\nNl ≈ 1/(ε^2): {:d}'.format(ceil(Nl)))

    print('\nthe following key blocks will be recovered:{}'.format(' '.join(list(map(str, list(linear_aproximation[2].keys()))))))

    # this will be different with another cipher
    key = keyGeneration()
    k_int = int(key, 16)

    # find which key bits we should obtain
    key_to_find = 0
    for block_num in linear_aproximation[2]:
        k = k_int >> ((NUM_SBOXES - (block_num-1) - 1) * SBOX_BITS)
        k = k & ((1 << SBOX_BITS) - 1)
        key_to_find = (key_to_find << SBOX_BITS) | k

    # the 'encrypt' function might be different for you
    p_c_pairs = []
    for pt in range(NUM_P_C_PAIRS):
        p_c_pairs.append( [pt, encrypt(pt, key)] )

    print('\nbreaking cipher...\n')
    # obtain the biases given the p/c pairs and the linear aproximation
    start = time.time_ns()
    biases = lc_lib.get_biases(p_c_pairs, linear_aproximation)
    end = time.time_ns()
    print("done, took {:d} ns".format(end - start))

    # get the key with the most hits
    maxResult, maxIdx = 0, 0
    for rIdx, result in enumerate(biases):
        if result > maxResult:
            maxResult = result
            maxIdx    = rIdx

    if maxIdx == key_to_find:
        print('Success!')
        bits_found = '{:b}'.format(maxIdx).zfill(len(linear_aproximation[2])*SBOX_BITS)
        bits_found = [bits_found[i:i+SBOX_BITS] for i in range(0, len(bits_found), SBOX_BITS)]

        blocks_num = list(linear_aproximation[2].keys())

        zipped = list(zip(blocks_num, bits_found))

        print('\nobtained key bits:')
        for num_block, bits in zipped:
            print('block {:d}: {}'.format(num_block, bits))

    else:
        print('Failure')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
