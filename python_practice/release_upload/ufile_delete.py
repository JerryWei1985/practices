#!/usr/bin/env python3
# coding=utf-8

import requests
import os
import argparse
import json
import sys
import time


url_server = 'mobvoi-oss'


def parseManager():
    parse = argparse.ArgumentParser(
        description='local delete tool, delete file from ucloud ufile storage')

    parse.add_argument(
        '--bucket', '-b', required=True, help="ucloud's bucketname"
    )

    parse.add_argument('-g','--group',required=True,help='group name')

    parse.add_argument('--password', '-p', required=True, help='user password')

    parse.add_argument('path', help='ufile path')

    return parse.parse_args()


def yes_no_input(massage):
    yes = {'yes', 'y', 'Y', 'YES'}
    value = input(massage)

    if value in yes:
        return True

    return False


def check_oss_file(bucket_name, key_name):
    prefix = key_name.split('/')[0]
    asr_model_url = "http://{}/v1/ufile/buckets/{}?prefix={}".format(url_server, bucket_name, prefix)
    req = requests.get(asr_model_url)
    oss_file_list = req.json()['files']

    if key_name not in oss_file_list:
        print('There is no {}'.format(key_name))
        return False

    return True


def startwith_check(path):
    if path.startswith('/'):
        path = path[1:]

    if path.endswith('/'):
        path = path[:-1]

    return path


def deleteFile(url_server, bucketname, key, headinfo):
    key = startwith_check(key)
    url = 'http://{0}/v1/ufile/{1}/{2}'.format(url_server, bucketname, key)
    try:
        if not check_oss_file(bucketname, key):
            sys.exit(4)
        else:
            if yes_no_input('Confirm to delete {}\n[y/n] '.format(url)):
                resp = requests.delete(url, headers=headinfo)
                if resp.status_code < 400:
                    print('{0} delete success'.format(key))
                else:
                    print(resp.text)
    except Exception as e:
        print(str(e))


def main():
    args = parseManager()

    headinfo = {
        'groupname': args.group,
        'password': args.password
    }

    bucket_name = args.bucket
    deleteFile(url_server, bucket_name, headinfo=headinfo, key=args.path)


if __name__ == '__main__':
    main()