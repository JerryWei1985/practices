#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import argparse
import re


ngram_order_re = re.compile(r'\\(\d+)-grams:')


def get_ngram_order(read_str):
    order_match = ngram_order_re.search(read_str)
    if order_match:
        return int(order_match.group(1))
    return None


def load_boost_list(boost_list):
    boost_dict = {}
    ngram_order = 0
    with open(boost_list, 'r', encoding='utf-8') as infile:
        for line in infile:
            tmp = line.strip()
            if tmp.startswith('#') or tmp == '':
                continue
            elif tmp.startswith('\\'):
                ngram_order = get_ngram_order(tmp)
                continue
            tmp = tmp.split()
            logP = float(tmp[0])
            logB = 0.0
            tokens = ' '.join(tmp[1:])
            if len(tmp) == ngram_order + 2:
                logB = float(tmp[-1])
                tokens = ' '.join(tmp[1:-1])
            if ngram_order not in boost_dict:
                boost_dict[ngram_order] = {}
            boost_dict[ngram_order][tokens] = (logP, logB)
    return boost_dict


def boost_ngram(tokens, logP, logB, boost_pair, delimiter):
    tmp_str = ''
    if logB != 0.0:
        if boost_pair[1] != 0:
            tmp_str = '{1}{0}{2}{0}{3}'.format(
                delimiter,
                boost_pair[0],
                tokens,
                boost_pair[1]
            )
        else:
            tmp_str = '{1}{0}{2}{0}{3}'.format(
                delimiter,
                boost_pair[0],
                tokens,
                logB
            )
    else:
        tmp_str = '{1}{0}{2}'.format(
            delimiter,
            boost_pair[0],
            tokens
        )
    return tmp_str


def get_delimiter(input_str):
    match = re.search(r'\s', input_str)
    if match:
        return match.group(0)
    return match


def pass_ngram(input_file, output_file, boost_list):
    boost_dict = load_boost_list(boost_list)
    delimiter = ''
    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w') as outfile:
            ngram_order = 0
            for line in infile:
                tmp = line.strip()
                if tmp.startswith('\\'):
                    outfile.write(line)
                    ngram_order = get_ngram_order(tmp)
                    continue
                elif tmp == '' or tmp.startswith('ngram'):
                    outfile.write(line)
                    continue
                elif ngram_order not in boost_dict:
                    outfile.write(line)
                    continue

                if not delimiter:
                    delimiter = get_delimiter(tmp)
                tmp = tmp.split()
                tokens = ''
                logP = 0.0
                logB = 0.0
                if len(tmp) == ngram_order + 1:
                    tokens = ' '.join(tmp[1:])
                else:
                    tokens = ' '.join(tmp[1:-1])

                if tokens in boost_dict[ngram_order]:
                    print(tokens)
                    logP = float(tmp[0])
                    if len(tmp) == ngram_order + 2:
                        logB = float(tmp[-1])
                    boost_pair = boost_dict[ngram_order][tokens]
                    outStr = boost_ngram(
                        tokens, logP, logB, boost_pair, delimiter
                    )
                    outfile.write(outStr + '\n')
                else:
                    outfile.write(line.strip() + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-arpa', '-i')
    parser.add_argument('--boost-list', '-b')
    parser.add_argument('--output-arpa', '-o')
    args = parser.parse_args()
    pass_ngram(args.input_arpa, args.output_arpa, args.boost_list)


if __name__ == '__main__':
    main()