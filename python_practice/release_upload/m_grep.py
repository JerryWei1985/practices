#!/usr/bin/env python3
# coding=utf-8

import argparse
import json
import re
import requests
import sys
import time
import os

asr_bucketname = "mobvoi-speech-private"
asr_model_url = "http://mobvoi-oss/v1/ufile/buckets/mobvoi-speech-private?prefix=mobvoi-recognizer-server"
ufile_url_format = 'http://mobvoi-oss/v1/ufile/buckets/{}?prefix={}'
full_path_url_format = "http://mobvoi-oss/v1/ufile/{}/{}"


def parseManager(args_string=None, prog_action=None):
    prog = sys.argv[0]
    if prog_action:
        prog = ' '.join([sys.argv[0], prog_action])

    parse = argparse.ArgumentParser(
        prog=prog,
        description="ASR model oss path filter tool. Get the full path after filter from {}".format(asr_model_url)
    )

    parse.add_argument(
        're_string',
        help='Regular expression for ufile path filter.'
    )

    args = parse.parse_args(args=args_string)
    return args


def filter_input(input_string):
    url_re = re.compile(r'http://mobvoi-oss/v1/ufile/([^/]+)/(([^/]+)/.+)')
    url_match = url_re.search(input_string)
    if url_match:
        ufile_url = ufile_url_format.format(
                        url_match.group(1),
                        url_match.group(3)
                    )
        re_match_oss_file(url_match.group(2), ufile_url, url_match.group(1))
    elif not input_string.startswith('http'):
        re_match_oss_file(input_string, asr_model_url)
    else:
        print('Illegal input path.')


def re_match_oss_file(re_string, ufile_url, bucket_name=''):
    if not bucket_name:
        bucket_name = asr_bucketname
    req = requests.get(ufile_url)
    oss_file_list = req.json()['files']
    filter_re = re.compile(re_string)
    for item in oss_file_list:
        match = filter_re.search(item)
        if match:
            full_path = full_path_url_format.format(bucket_name, item)
            print(full_path)


def main(args_string=None, prog_action=None):
    args = parseManager(args_string, prog_action)
    filter_input(args.re_string)


if __name__ == '__main__':
    main()
