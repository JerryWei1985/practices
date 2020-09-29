#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import argparse
import random


def get_rand_seed(count, infile_path):
    total_count = 0
    with open(infile_path, 'r') as infile:
        total_count = len(infile.readlines())
    rand_seed_set = set()
    while len(rand_seed_set) < count:
        index = random.randint(0, total_count)
        rand_seed_set.add(index)
    return rand_seed_set

def random_select(rand_list, input_path):
    with open(input_path, 'r') as infile:
        line_num = 0
        output_set = set()
        for line in infile:
            if line_num in rand_list:
                output_set.add(line)
            line_num += 1
        return output_set

def random_out(output_set, output_path, contain_path=''):
    with open(output_path, 'w') as outfile:
        for item in output_set:
            outfile.write(item)
        if contain_path:
            with open(contain_path, 'r') as infile:
                for line in infile:
                    outfile.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-list', '-i')
    parser.add_argument('--contain-list', '-c')
    parser.add_argument('--output', '-o')
    parser.add_argument('--count', type=int)
    args = parser.parse_args()

    seed_list = get_rand_seed(args.count, args.input_list)
    rand_line = random_select(seed_list, args.input_list)
    random_out(rand_line, args.output, args.contain_list)
