#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import os
import tarfile

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
                overwrite = False
                if self.overwrite == Overwrite.no_set:
                    overwrite = self.yes_no_input('Compressed file has existed, overwrite? [y/n] ')
                elif self.overwrite == Overwrite.overwrite:
                    overwrite = True
                if overwrite:
                    os.remove(self.output_path)
                return overwrite
        elif (self.action == Action.Decompress_rar or
              self.action == Action.Decompress_zip):
              raise ValueError('Not support rar and zip decompress.')
        elif self.action_type != FileType.other:
              raise ValueError('Output is a compressed output path.')
        return True

    def check_link(self, file):
        if os.path.islink(file):
            return self.yes_no_input('Warning: {} is link file. Contain it? [y/n] '.format(file))
        return True

# 此处有bug，相对路径是否可用，使用绝对路径会有什么影响
    def check_input_files(self, path):
        if not os.path.exists(path):
            raise IOError("{} doesn't exist.".format(path))
        if os.path.isdir(path):
            os.chdir(path)
            files = os.listdir(path)
            if not files:
                print('Input is empty.')
                return None
            return files
        return [path]

    def compress_files(self, files, mode):
        with tarfile.open(self.output_path, mode) as tar:
            for f in files:
                if self.check_link(f):
                    tar.add(f)

    def compress(self):
        if self.input_path.endswith('*'):
            if self.input_path == '*':
                self.input_path = os.getcwd()
            else:
                self.input_path = os.path.abspath(self.input_path.rstrip('*'))
        files = self.check_input_files(self.input_path)
        if self.action_type == FileType.tar:
            self.compress_files(files, 'w')
        elif self.action_type == FileType.gz:
            self.compress_files(files, 'w:gz')
        elif self.action_type == FileType.bz2:
            self.compress_files(files, 'w:bz2')
        else:
            raise IOError("Don't support compressed output.")

    def decompress(self):
        output_folder = self.output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        elif os.path.isdir(self.output_path):
            fname = os.path.basename(output_folder)
            fname = fname.rstrip('.bz2').rstrip('gz').rstrip('.tar')
            output_folder = os.path.join(output_folder, fname)
            os.makedirs(output_folder)
        else:
            raise IOError('{} is not a folder.'.format(self.output_path))
        os.chdir(output_folder)
        with tarfile.open(self.input_path) as tar:
            tar.extractall()

    def output(self):
        if self.action == Action.Compress:
            self.compress()
        else:
            self.decompress()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', required=True)
    parser.add_argument('--overwrite', '-ow', action='store_true')
    args = parser.parse_args()

    overwrite = Overwrite.skip
    if args.overwrite:
        overwrite = Overwrite.overwrite
    Tar(args.input, args.output, overwrite)
