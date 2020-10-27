#!/usr/bin/env python3
# coding=utf-8

from enum import Enum
from bar import IncrementalBar
from m_tar import Overwrite

import argparse
import requests
import os
import json
import sys
import time
import math


SIZE = 4
BLOCKSIZE = 1024 * 1024 * SIZE  # 4MB
url_server = "mobvoi-oss"
asr_bucketname = "mobvoi-speech-private"
asr_group = "speech"
asr_password = "f3acdf8021d13da3f36086464fe850c9"
asr_model_head = "mobvoi-recognizer-server"
asr_testset_head = "testsets"
asr_model_url="http://mobvoi-oss/v1/ufile/buckets/mobvoi-speech-private?prefix=mobvoi-recognizer-server"
asr_testsets_url="http://mobvoi-oss/v1/ufile/buckets/mobvoi-speech-private?prefix=testsets"
asr_oss_full_path = "http://mobvoi-oss/v1/ufile/mobvoi-speech-private/{0}"


def yes_no_input(massage):
    yes = {'yes', 'y', 'Y', 'YES'}
    value = input(massage)

    if value in yes:
        return True

    return False


def check_oss_file(file_name, path_head, project_name=''):
    req = requests.get(asr_model_url)
    oss_file_list = req.json()['files']
    oss_path = '/'.join([path_head, file_name])

    if project_name:
        oss_path = '/'.join([path_head, project_name, file_name])

    if oss_path in oss_file_list:
        print('{} has been uploaded.'.format(oss_path))
        return True

    return False


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


# file size lt 4M,exec the function
def uploads(url_server, bucketname, upload_file, key, headinfo):
    key = startwith_check(key)
    url = "http://{0}/v1/ufile/{1}/{2}".format(url_server, bucketname, key)

    try:
        with open(upload_file, "rb") as f:
            resp = requests.post(url, data=f, headers=headinfo)

        if resp.status_code == 200:
            file_full_url = asr_oss_full_path.format(key)
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
        file_full_url = asr_oss_full_path.format(key)
        print("Upload success!!\n{0}".format(file_full_url))
    else:
        print(r.text)
    return r


# exec the multi part upload
def mulitUpload(url_server, bucketname, upload_file, key, headict,
                upload_file_size):
    key = startwith_check(key)
    etaglist = []
    UploadId, headers = mulitInit(url_server, bucketname, key, headict)

    headers["groupname"] = headict["groupname"]
    headers["password"] = headict["password"]

    if verifyMultiInit(UploadId):
        pass

    partNumber = 0

    with open(upload_file, "rb") as f:
        upload_file_count = math.ceil(upload_file_size / SIZE)
        bar = IncrementalBar('Uploading', max=upload_file_count)
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


def middle_func(url_server, bucket_name, upload_file, key_name, headinfo,
                upload_file_size):
    res, headers, UploadId, _, etaglist = mulitUpload(
        url_server, bucket_name, upload_file, key_name, headinfo, upload_file_size)

    if int(res.status_code) == 200:
        finishMulti(url_server, bucket_name, key_name, UploadId,
                    headers, etaglist)


def upload_single_file(upload_file, project_name='',
                       overwrite=Overwrite.no_set,
                       path_head=asr_model_head):
    bucket_name = asr_bucketname
    headinfo = {
        "groupname": asr_group,
        "password": asr_password
    }

    base_name = os.path.basename(upload_file)

    key_name = '{}/{}'.format(path_head, base_name)
    if project_name:
        project_name = project_name.replace('\\', '/')
        key_name = '{}/{}/{}'.format(
            path_head, project_name, base_name)

    if check_oss_file(base_name, path_head, project_name):
        if overwrite == Overwrite.no_set:
            if not yes_no_input('Do you want to overwrite it? [y/n] '):
                return None
        elif overwrite == Overwrite.skip:
            return None

    print('Upload file to {}'.format(
        asr_oss_full_path.format(key_name)))

    upload_file_size = fileSize(upload_file)

    if upload_file_size > 4:
        middle_func(url_server,bucket_name, upload_file,
                    key_name, headinfo, upload_file_size)
    else:
        uploads(url_server, bucket_name, upload_file, key_name, headinfo)


def upload(upload_file, project_name='',
           overwrite=Overwrite.no_set,
           path_head=asr_model_head,
           recursive=False):
    try:
        if os.path.isfile(upload_file):
            upload_single_file(upload_file, project_name, overwrite, path_head)
        elif os.path.isdir(upload_file):
            if not recursive:
                print('"{}" is a folder.\nIf you want to upload all files in it, set --recursive.'.format(upload_file))
                sys.exit(3)
            for r, _, fs in os.walk(upload_file):
                for f in fs:
                    full_path = os.path.join(r, f)
                    upload_single_file(full_path, project_name, overwrite, path_head)
        else:
            print('Illegal input file path "{0}".'.format(upload_file))
            sys.exit(3)
    except Exception as e:
        print(e)


def main(args_string=None, prog_action=None):
    prog = sys.argv[0]
    if prog_action:
        prog = ' '.join([sys.argv[0], prog_action])

    parser = argparse.ArgumentParser(
        prog=prog,
        description='The file will be uploaded to {}'.format(asr_model_url)
    )

    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='uploaded file/folder path.'
    )
    parser.add_argument(
        '--project-name', 
        '-p', 
        required=True,
        help='project name, which will be parent folder name in oss.'
    )
    parser.add_argument(
        '--overwrite',
        '-ow',
        action='store_true'
    )
    parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        help='Recursivly upload files in input folder.'
    )
    parser.add_argument(
        '--oss-root',
        choices=['model', 'testset'],
        help='oss path root. Current just support mobvoi-recognizer-server and testsets',
        default='model'
    )

    args = parser.parse_args(args=args_string)

    overwrite = Overwrite.skip
    if args.overwrite:
        overwrite = Overwrite.overwrite

    oss_root = {
        'model': asr_model_head,
        'testset': asr_testset_head
    }

    upload(args.input, args.project_name, overwrite,
           oss_root[args.oss_root], args.recursive)


if __name__ == '__main__':
    main()