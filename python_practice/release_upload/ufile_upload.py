#!/usr/bin/env python2

# coding=utf-8
import requests
import os
import argparse
import json
import sys
import time
import math

from bar import IncrementalBar

SIZE = 4
BLOCKSIZE = 1024 * 1024 * SIZE  # 4MB
url_server = "mobvoi-oss"


def parseManager():
    parse = argparse.ArgumentParser(
        description="local upload tool, up file to ucloud ufile  storage, ctrl C delete multi uploaded")
    parse.add_argument('--bucket',
                       '-b',
                       required=True,
                       help="ucloud's bucketname"
                       )
    parse.add_argument('path', help='ufile path')

    parse.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='copy directories recursively'
    )

    parse.add_argument('-g', '--group', required=True, help="group name")

    parse.add_argument('--password',
                       '-p',
                       required=True,
                       help='user password')

    parse.add_argument('--upload_file',
                       required=False,
                       help="upload filepath ,need Absloute path,e.g:/home/mobvoi/filename.txt")

    args = parse.parse_args()
    return args


# check file size
def fileSize(filepath):
    size = os.path.getsize(filepath) / (1024 * 1024.0)  # MB
    return size


# iter the file,read fix size
def fileIter(input_stream, size):
    d = input_stream.read(size)
    while d:
        yield d
        d = input_stream.read(size)


def startwith_check(path):
    if path.startswith("/"):
        path = path[1:]

    if path.endswith("/"):
        path = path[:-1]

    return path


def list_dir(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            yield os.path.join(root, name)


# file size lt 4M,exec the function
def uploads(url_server, bucketname, upload_file, key, headinfo):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/{1}/{2}".format(url_server, bucketname, key)
    try:
        with open(upload_file, "rb") as f:
            resp = requests.post(url, data=f, headers=headinfo)

        if resp.status_code == 200:
            file_full_url = 'http://mobvoi-oss/v1/ufile/mobvoi-speech-private/{0}'.format(key)
            print("Upload success!!\n{0}".format(file_full_url))
        else:
            print(resp.text)
    except Exception as e:
        print(str(e))


# intial multi part,return the UploadId and head info
def mulitInit(url_server, bucketname, key, headers):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/multi/init/{1}/{2}".format(url_server, bucketname, key)
    try:
        r = requests.get(url, headers=headers)
        ret = json.loads(r.text)

        if "UploadId" in ret:
            UploadId = ret["UploadId"]
            ret.pop("UploadId")
        else:
            UploadId = None
            print(ret)
        return UploadId, ret
    except Exception as e:
        print(str(e))


# verify init status
def verifyMultiInit(UploadId):
    if UploadId is not None and UploadId.strip("") != "":
        print("Init success!!")
        return True
    else:
        print("Init failed !!")
        sys.exit(0)


# verify multi prat upload status
def verifyMultiPart(status_code, partNumber):
    if status_code == 200:
        print("multi partNumber {0} upload success".format(partNumber))
        return True
    else:
        print("multi partNumber {0} upload failed".format(partNumber))
        return False


def mulitUploadUrl(url_server, bucketname, key, UploadId, partNumber):
    key = startwith_check(key)
    url = 'http://{0}/v1/ufile/multi/upload/{1}/{2}?UploadId={3}&partNumber={4}'.format(url_server, bucketname, key, UploadId, partNumber)
    return url


# finish multi part upload
def finishMulti(url_server, bucketname, key, UploadId, headers, etaglist):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/multi/finish/{1}/{2}?UploadId={3}".format(url_server, bucketname, key, UploadId)
    r = requests.post(url, headers=headers, data=json.dumps({"etag": etaglist}))

    if r.status_code == 200:
        file_full_url = 'http://mobvoi-oss/v1/ufile/mobvoi-speech-private/{0}'.format(key)
        print("Upload success!!\n{0}".format(file_full_url))
    else:
        print(r.text)

    return r


# exec the multi part upload
def mulitUpload(url_server, bucketname, upload_file, key, headict):
    key = startwith_check(key)
    etaglist = []
    UploadId, headers = mulitInit(url_server, bucketname, key, headict)

    headers["groupname"] = headict["groupname"]
    headers["password"] = headict["password"]

    if verifyMultiInit(UploadId):
        pass

    partNumber = 0

    with open(upload_file, "rb") as f:
        upload_file_size = math.ceil(fileSize(upload_file) / SIZE)
        bar = IncrementalBar('Uploading', max=upload_file_size)
        for part_file in fileIter(f, BLOCKSIZE):
            url = mulitUploadUrl(url_server=url_server, bucketname=bucketname,
                                 key=key, UploadId=UploadId, partNumber=partNumber)
            res = requests.post(url, data=part_file, headers=headers)

            while True:
                if res.status_code == 200:
                    etaglist.append(json.loads(res.text)["etag"])
                    partNumber += 1
                    bar.next()
                    break
                else:
                    time.sleep(0.1)
                    res = requests.post(url, data=part_file, headers=headers)

        bar.finish()

    return res, headers, UploadId, partNumber, etaglist


def middle_func(url_server, bucket_name, upload_file, key_name, headinfo):
    res, headers, UploadId, partNumber, etaglist = mulitUpload(url_server=url_server,
                                                               bucketname=bucket_name,
                                                               upload_file=upload_file,
                                                               key=key_name,
                                                               headict=headinfo)
    if int(res.status_code) == 200:
        finishMulti(url_server=url_server, bucketname=bucket_name,
                    key=key_name, UploadId=UploadId,
                    headers=headers, etaglist=etaglist)


def main():
    args = parseManager()
    headinfo = {
        "groupname": args.group,
        "password": args.password
    }

    bucket_name = args.bucket
    upload_file = args.upload_file
    upload_file_size = fileSize(upload_file)

    try:
        if args.recursive and os.path.isdir(args.upload_file):
            upload_folder = args.upload_file
            if upload_folder.endswith('/'):
                upload_folder = upload_folder[:-1]

            base_name = os.path.dirname(upload_folder)
            base_name_prefix = len(base_name) + 1

            for upload_file in list_dir(upload_folder):
                sub_folder = os.path.dirname(upload_file[base_name_prefix:])
                key_name = '/'.join([startwith_check(args.path),
                                     startwith_check(sub_folder),
                                     os.path.basename(upload_file)])
                if upload_file_size > 4:
                    middle_func(url_server=url_server, bucket_name=bucket_name,
                                upload_file=upload_file, key_name=key_name,
                                headinfo=headinfo)
                else:
                    uploads(url_server, bucket_name, upload_file, headinfo=headinfo, key=key_name)
        elif os.path.isfile(args.upload_file):
            key_name = args.path
            if upload_file_size > 4:
                middle_func(url_server=url_server, bucket_name=bucket_name,
                            upload_file=upload_file, key_name=key_name,
                            headinfo=headinfo)
            else:
                uploads(url_server, bucket_name, upload_file, headinfo=headinfo, key=key_name)
        else:
            print('can not find file {0}'.format(args.upload_file))
            exit(3)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
