#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import os
import tarfile
import sys

from enum import Enum


folder = {'.', '*', './', '.\\', './*', '.\\*'}


class Action(Enum):
    Compress = 0
    Decompress_bz2 = 1
    Decompress_gz = 2
    Decompress_tar = 3
    Decompress_zip = 4
    Decompress_rar = 5


class FileType(Enum):
    rar = 0
    zip = 1
    bz2 = 2
    gz = 3
    tar = 4
    other = 5


class Overwrite(Enum):
    overwrite = 0
    skip = 1
    no_set = 2


class Tar(object):
    def __init__(self, input_path, output_path, overwrite=Overwrite.no_set):
        self.input_path = input_path
        self.output_path = output_path
        self.compress_done = os.path.join(os.path.dirname(self.output_path), '.tar_done')
        self.decompress_done = '.untar_done'
        self.overwrite = overwrite
        self.action = Action.Compress
        self.action_type = FileType.bz2
        self.init_folder = os.getcwd()
        self.check_input()
        if self.action == Action.Compress:
            self.check_action(self.output_path)
        else:
            self.check_action(self.input_path)
        if self.output_check():
            self.output()

    def check_compress_done(self):
        if os.path.exists(self.compress_done):
            print('Compress has done.', end=' ')
            if self.overwrite == Overwrite.skip:
                return True
            elif self.overwrite == Overwrite.no_set:
                return not self.yes_no_input('Redo or not? [y/n]')
        return False


    def check_input(self):
        if self.input_path.endswith('.tar.bz2'):
            self.action = Action.Decompress_bz2
        elif self.input_path.endswith('.tar.gz'):
            self.action = Action.Decompress_gz
        elif self.input_path.endswith('.tar'):
            self.action = Action.Decompress_tar
        elif self.input_path.endswith('.zip'):
            self.action = Action.Decompress_zip
        elif self.input_path.endswith('.rar'):
            self.action = Action.Decompress_rar
        elif self.input_path in folder:
            self.action = Action.Compress

    def check_action(self, file_path):
        if file_path.endswith('.tar.bz2'):
            self.action_type = FileType.bz2
        elif file_path.endswith('.tar.gz'):
            self.action_type = FileType.gz
        elif file_path.endswith('.tar'):
            self.action_type = FileType.tar
        elif file_path.endswith('.zip'):
            self.action_type = FileType.zip
        elif file_path.endswith('.rar'):
            self.action_type = FileType.rar
        else:
            self.action_type = FileType.other

    def yes_no_input(self, massage):
        yes = {'yes', 'y', 'Y', 'YES'}
        value = input(massage)
        if value in yes:
            return True
        return False

    def output_check(self):
        if self.action == Action.Compress:
            if (self.action_type == FileType.rar or
                self.action_type == FileType.zip):
                raise ValueError('Not support rar and zip compress.')
            elif self.action_type == FileType.other:
                raise ValueError('Please set an available output compress file.')
            elif os.path.exists(self.output_path):
                if ((self.overwrite == Overwrite.no_set and
                    self.yes_no_input('Compressed file has existed, overwrite? [y/n] ')) or
                    self.overwrite == Overwrite.overwrite):
                    os.remove(self.output_path)
                else:
                    return False
        elif (self.action == Action.Decompress_rar or
              self.action == Action.Decompress_zip):
              raise ValueError('Not support rar and zip decompress.')
        elif self.action_type != FileType.other:
              raise ValueError('Output is a compressed output path.')
        return True

    def check_not_link(self, file):
        if os.path.islink(file):
            return self.yes_no_input('Warning: {} is link file. Contain it? [y/n] '.format(file))
        return True

# 不能用绝对路径
    def check_input_files(self, path):
        if not os.path.exists(path):
            raise IOError("{} doesn't exist.".format(path))
        if os.path.isdir(path):
            files = os.listdir(path)
            if not files:
                print('Input is empty.')
                sys.exit(0)
            return files, path
        return [path], os.path.dirname(path)

    def compress_files(self, files, mode):
        if not self.check_compress_done():
            if os.path.exists(self.output_path):
                print('Remove {}'.format(self.output_path))
                os.remove(self.output_path)
            with tarfile.open(self.output_path, mode) as tar:
                for f in files:
                    file_type = 'file'
                    if os.path.isdir(f):
                        file_type = 'folder'
                        if f == 'raw':
                            print('Skip: {}'.format(f))
                            continue
                    elif os.path.islink(f):
                        file_type = 'link'
                    elif (f == 'raw' or f == '.done' or f == 'done' or
                          f == os.path.basename(self.compress_done) or
                          f == self.decompress_done or
                          f.endswith('.bz2') or
                          f.endswith('.gz') or
                          f.endswith('.tar')):
                        print('Skip: {}'.format(f))
                        continue
                    print('Adding: {} {}'.format(file_type, f))
                    tar.add(f)
            open(self.compress_done, 'a').close()

    def compress(self):
        if self.input_path.endswith('*'):
            if self.input_path == '*':
                self.input_path = os.getcwd()
            else:
                self.input_path = os.path.abspath(self.input_path.rstrip('*'))
        files, work_folder = self.check_input_files(self.input_path)
        pwd = os.getcwd()
        os.chdir(work_folder)
        if self.action_type == FileType.tar:
            self.compress_files(files, 'w')
        elif self.action_type == FileType.gz:
            self.compress_files(files, 'w:gz')
        elif self.action_type == FileType.bz2:
            self.compress_files(files, 'w:bz2')
        else:
            raise IOError("Don't support compressed output.")
        os.chdir(pwd)

    def decompress_done_check(self, output_folder):
        if os.path.exists(os.path.join(output_folder, self.decompress_done)):
            return True
        return False

    def decompress(self):
        output_folder = self.output_path
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        elif os.path.isdir(output_folder):
            if not self.decompress_done_check(output_folder):
                fname = os.path.basename(self.input_path)
                fname = fname.rstrip('.bz2').rstrip('gz').rstrip('.tar')
                output_folder = os.path.join(output_folder, fname)
                if self.decompress_done_check(output_folder):
                    if ((self.overwrite == Overwrite.no_set and
                        not self.yes_no_input('Output has existed, do you want to overwrite it? [y/n]')) or
                        self.overwrite == Overwrite.skip):
                        return
            else:
                if ((self.overwrite == Overwrite.no_set and
                    not self.yes_no_input('Output has existed, do you want to overwrite it? [y/n]')) or
                    self.overwrite == Overwrite.skip):
                    return
            if os.path.exists(output_folder):
                os.remove(output_folder)
            os.makedirs(output_folder)
        else:
            raise IOError('{} is not a folder.'.format(self.output_path))

        pwd = os.getcwd()
        os.chdir(output_folder)
        with tarfile.open(self.input_path) as tar:
            tar.extractall()
        open(self.decompress_done, 'a').close()
        os.chdir(pwd)

    def output(self):
        if self.action == Action.Compress:
            self.compress()
        else:
            self.decompress()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='input path.')
    parser.add_argument('--output', '-o', required=True, help='output path.')
    parser.add_argument('--overwrite', '-ow', action='store_true')
    args = parser.parse_args()

    overwrite = Overwrite.skip
    if args.overwrite:
        overwrite = Overwrite.overwrite

    Tar(args.input, args.output, overwrite)