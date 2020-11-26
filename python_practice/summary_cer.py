#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import argparse
import re
import email_sender

from collections import OrderedDict


WER_re = re.compile(r'^Overall -> (\d+\.\d+%) N=(\d+) C=\d+ S=\d+ D=\d+ I=\d+')
SER_re = re.compile(r'^SER -> (\d+\.\d+%) utt=(\d+) err=\d+')


def parse_result(result_file):
    with open(result_file, 'r') as infile:
        wer = ''
        ser = ''
        for line in infile:
            wer_match = WER_re.search(line)
            ser_match = SER_re.search(line)
            if wer_match:
                wer = (wer_match.group(1), wer_match.group(2))
            elif ser_match:
                ser = (ser_match.group(1), ser_match.group(2))
        return wer, ser


def load_result_list(list_file):
    result_dic = OrderedDict()
    with open(list_file, 'r') as infile:
        for line in infile:
            tmp = line.strip().split(':')
            if len(tmp) != 2:
                raise ValueError
            set_name = tmp[0]
            result_path = tmp[1]
            result = parse_result(result_path)
            result_dic[set_name] = result
    return result_dic


def output_result(output_file, result_dic):
    with open(output_file, 'w') as outfile:
        result_name = '\t'.join(result_dic.keys)
        outfile.write(result_name + '\n')
        result = ''
        for key in result_dic:
            result += '\t' + '/'.join([result_dic[key][0][0], result_dic[key][1][0]])
        outfile.write(result)


def output_html_table(result_dic):
    table = '<table>{0}</table>'
    tr = '<tr>{0}</tr>'
    td = '<td>{0}</td>'
    col = ''
    row = ''
    for key in result_dic.keys:
        col += td.format(key)
    row += tr.format(col)
    col = ''
    for key in result_dic:
        col += td.format(result_dic[key][0][0] + '/' + result_dic[key][1][0])
    row += tr.format(col)
    return table.format(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-list', '-i')
    parser.add_argument('--output-summary', '-o')
    args = parser.parse_args()

    result_dic = load_result_list(args.result_list)
    output_result(args.output_summary, result_dic)
    table = output_html_table(result_dic)
    email_sender.send_email('ghwei@mobvoi.com', table, 'test')


if __name__ == '__main__':
    main()