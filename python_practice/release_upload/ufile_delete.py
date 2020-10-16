#!/usr/bin/env python2
# coding=utf-8

import requests
import os
import argparse
import json
import sys
import time

url_server = "mobvoi-oss"

def parseManager():
    parse = argparse.ArgumentParser(
        description="local delete tool, delete file from ucloud ufile storage")

    parse.add_argument('--bucket',
                '-b',
                required=True,
                help="ucloud's bucketname"
                )

    parse.add_argument('-g','--group',required=True,help="group name")

    parse.add_argument('--password',
                '-p',
                required=True,
                help='user password')

    parse.add_argument('path', help='ufile path')

    args = parse.parse_args()
    return args

def startwith_check(path):
    if path.startswith("/"):
        path = path[1:]

    if path.endswith("/"):
        path = path[:-1]

    return path

def deleteFile(url_server, bucketname, key, headinfo):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/{1}/{2}".format(url_server, bucketname, key)
    try:
        resp = requests.delete(url, headers=headinfo)
        if resp.status_code < 400:
            print "{0} delete success".format(key)
        else:
            print resp.text
    except Exception, e:
        print str(e)

def main():
    args = parseManager()

    headinfo = {
        "groupname": args.group,
        "password": args.password
    }

    bucket_name = args.bucket
    deleteFile(url_server, bucket_name, headinfo=headinfo, key=args.path)


if __name__ == '__main__':
    main()
