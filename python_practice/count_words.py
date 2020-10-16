#!/usr/bin/env python3
#-*- coding:utf-8 -*-


import argparse
import re


english_re = re.compile("[a-zA-Z]+'[a-zA-Z]+|[a-zA-Z]+")

def extract_eng(string):
    for word_obj in english_re.finditer(string):
        yield word_obj.group(0).lower()

def count_words(file_path_list, output_path):
    words_count = {}
    for file_path in file_path_list:
        with open(file_path, 'r') as infile:
            for line in infile:
                for word in extract_eng(line):
                    if word in words_count:
                        words_count[word] += 1
                    else:
                        words_count[word] = 1
    with open(output_path, 'w') as outfile:
        for item in sorted(words_count.items(), key=lambda x: x[1], reverse=True):
            outfile.write('{}\t{}\n'.format(item[0], item[1]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', '-i', nargs='+')
    parser.add_argument('--output-file', '-o')
    args = parser.parse_args()

    count_words(args.input_file, args.output_file)

if __name__ == '__main__':
    main()
