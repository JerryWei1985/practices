#!/usr/bin/env python
import os
import sys
import tarfile

root = sys.argv[1]

with tarfile.open('tmp.tar.gz', 'w:gz') as tar:
    os.chdir(root)
    for fs in os.listdir(root):
        tar.add(fs)

