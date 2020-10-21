#!/usr/bin/env python3

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
url_server = 'mobvoi-oss'
full_url_format = 'http://{0}/v1/ufile/{1}/{2}'
init_url_format = 'http://{0}/v1/ufile/multi/init/{1}/{2}'
multi_url_format = 'http://{0}/v1/ufile/multi/upload/{1}/{2}?UploadId={3}&partNumber={4}'
finish_url_format = 'http://{0}/v1/ufile/multi/finish/{1}/{2}?UploadId={3}'

def parseManager():
    parse = argparse.ArgumentParser(
        description='local upload tool, up file to ucloud ufile  storage, ctrl C delete multi uploaded')
    parse.add_argument(
        '--bucket',
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

    parse.add_argument('-g', '--group', required=True, help='group name')

    parse.add_argument(
        '--password',
        '-p',
        required=True,
        help='user password'
    )

    parse.add_argument(
        '--upload_file',
        required=False,
        help='upload filepath ,need Absloute path,e.g:/home/mobvoi/filename.txt'
    )

    parse.add_argument('--overwrite', '-ow', action='store_true')

    return parse.parse_args()


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
    if path.startswith('/'):
        path = path[1:]

    if path.endswith('/'):
        path = path[:-1]

    return path


def list_dir(root_dir):
    for root, _, files in os.walk(root_dir):
        for name in files:
            yield os.path.join(root, name)


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


# file size lt 4M,exec the function
def uploads(url_server, bucketname, upload_file, key, headinfo):
    key = startwith_check(key)
    url = full_url_format.format(url_server, bucketname, key)
    try:
        with open(upload_file, 'rb') as f:
            resp = requests.post(url, data=f, headers=headinfo)

        if resp.status_code == 200:
            print('Upload success!!\n{0}'.format(url))
        else:
            print(resp.text)
    except Exception as e:
        print(str(e))


# intial multi part,return the UploadId and head info
def mulitInit(url_server, bucketname, key, headers):
    key = startwith_check(key)
    url = init_url_format.format(url_server, bucketname, key)
    try:
        r = requests.get(url, headers=headers)
        ret = json.loads(r.text)

        if 'UploadId' in ret:
            UploadId = ret['UploadId']
            ret.pop('UploadId')
        else:
            UploadId = None
            print(ret)
        return UploadId, ret
    except Exception as e:
        print(str(e))


# verify init status
def verifyMultiInit(UploadId):
    if UploadId is not None and UploadId.strip('') != '':
        print('Init success!!')
        return True
    else:
        print('Init failed !!')
        sys.exit(0)


def mulitUploadUrl(url_server, bucketname, key, UploadId, partNumber):
    key = startwith_check(key)
    url = multi_url_format.format(
        url_server, bucketname, key, UploadId, partNumber
    )
    return url


# finish multi part upload
def finishMulti(url_server, bucketname, key, UploadId, headers, etaglist):
    key = startwith_check(key)
    url = finish_url_format.format(url_server, bucketname, key, UploadId)
    r = requests.post(url, headers=headers, data=json.dumps({'etag': etaglist}))

    if r.status_code == 200:
        file_full_url = full_url_format.format(url_server, bucketname, key)
        print('Upload success!!\n{0}'.format(file_full_url))
    else:
        print(r.text)

    return r


# exec the multi part upload
def mulitUpload(url_server, bucketname, upload_file, key, headict):
    key = startwith_check(key)
    etaglist = []
    UploadId, headers = mulitInit(url_server, bucketname, key, headict)

    headers['groupname'] = headict['groupname']
    headers['password'] = headict['password']

    if verifyMultiInit(UploadId):
        pass

    partNumber = 0

    with open(upload_file, 'rb') as f:
        upload_file_size = math.ceil(fileSize(upload_file) / SIZE)
        bar = IncrementalBar('Uploading', max=upload_file_size)
        for part_file in fileIter(f, BLOCKSIZE):
            url = mulitUploadUrl(
                url_server=url_server,
                bucketname=bucketname,
                key=key,
                UploadId=UploadId,
                partNumber=partNumber
            )
            res = requests.post(url, data=part_file, headers=headers)

            while True:
                if res.status_code == 200:
                    etaglist.append(json.loads(res.text)['etag'])
                    partNumber += 1
                    bar.next()
                    break
                else:
                    time.sleep(0.1)
                    res = requests.post(url, data=part_file, headers=headers)

        bar.finish()

    return res, headers, UploadId, partNumber, etaglist


def middle_func(url_server, bucket_name, upload_file, key_name, headinfo):
    res, headers, UploadId, _, etaglist = mulitUpload(
        url_server=url_server,
        bucketname=bucket_name,
        upload_file=upload_file,
        key=key_name,
        headict=headinfo
    )
    if int(res.status_code) == 200:
        finishMulti(
            url_server=url_server,
            bucketname=bucket_name,
            key=key_name,
            UploadId=UploadId,
            headers=headers,
            etaglist=etaglist
        )


def main():
    args = parseManager()
    headinfo = {
        'groupname': args.group,
        'password': args.password
    }

    bucket_name = args.bucket
    upload_file = args.upload_file
    upload_file_size = fileSize(upload_file)

    try:
        if args.recursive and os.path.isdir(args.upload_file):
            upload_folder = args.upload_file.rstrip('/')

            sub_folder = os.path.basename(upload_folder)

            for upload_file in list_dir(upload_folder):
                key_name = '/'.join([
                    startwith_check(args.path),
                    sub_folder,
                    os.path.basename(upload_file)
                ])
                if check_oss_file(bucket_name, key_name):
                    if not args.overwrite:
                        if not yes_no_input('File exists in oss, do you want to overwite it. [y/n] '):
                            sys.exit(0)
                if upload_file_size > 4:
                    middle_func(
                        url_server=url_server,
                        bucket_name=bucket_name,
                        upload_file=upload_file,
                        key_name=key_name,
                        headinfo=headinfo
                    )
                else:
                    uploads(
                        url_server,
                        bucket_name,
                        upload_file,
                        headinfo=headinfo,
                        key=key_name
                    )
        elif os.path.isfile(args.upload_file):
            key_name = args.path
            if check_oss_file(bucket_name, key_name):
                if not args.overwrite:
                    if not yes_no_input('File exists in oss, do you want to overwite it. [y/n] '):
                        sys.exit(0)
            if upload_file_size > 4:
                middle_func(
                    url_server=url_server,
                    bucket_name=bucket_name,
                    upload_file=upload_file,
                    key_name=key_name,
                    headinfo=headinfo
                )
            else:
                uploads(
                    url_server,
                    bucket_name,
                    upload_file,
                    headinfo=headinfo,
                    key=key_name
                )
        else:
            print('Can\'t find file {0}'.format(args.upload_file))
            exit(3)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()