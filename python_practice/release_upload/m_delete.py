#!/usr/bin/env python3
# coding=utf-8

import requests
import os
import argparse
import json
import sys
import time

url_server = "mobvoi-oss"
asr_bucketname = "mobvoi-speech-private"
asr_group = "speech"
asr_password = "f3acdf8021d13da3f36086464fe850c9"
asr_model_head = "mobvoi-recognizer-server"
asr_model_url="http://mobvoi-oss/v1/ufile/buckets/mobvoi-speech-private?prefix=mobvoi-recognizer-server"

def parseManager():
    parse = argparse.ArgumentParser(
        description="ASR model local delete tool, delete model file from ucloud ufile storage")

    parse.add_argument('--project-name', '-p', default='', required=False, help='partial path before file name, it is usually projcet name.')
    parse.add_argument('--file-name', help='ufile name')

    args = parse.parse_args()
    return args

def startwith_check(path):
    if path.startswith("/"):
        path = path[1:]

    if path.endswith("/"):
        path = path[:-1]

    return path

def check_oss_file(file_oss_path):
    req = requests.get(asr_model_url)
    oss_file_list = req.json()['files']
    if file_oss_path not in oss_file_list:
        print('There is no {}'.format(file_oss_path))
        return False
    return True

def deleteFile(url_server, bucketname, key, headinfo):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/{1}/{2}".format(url_server, bucketname, key)
    try:
        if not check_oss_file(key):
            sys.exit(4)
        resp = requests.delete(url, headers=headinfo)
        if resp.status_code < 400:
            print("{0} delete success".format(key))
        else:
            print(resp.text)
    except Exception as e:
        print(str(e))

def main():
    args = parseManager()

    headinfo = {
        "groupname": asr_group,
        "password": asr_password
    }

    model_path = '/'.join([asr_model_head, args.file_name])
    if args.project_name:
        model_path = '/'.join([asr_model_head, args.project_name, args.file_name])
    deleteFile(url_server, asr_bucketname, headinfo=headinfo, key=model_path)


if __name__ == '__main__':
    main()