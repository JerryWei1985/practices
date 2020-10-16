#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from m_tar import *
import argparse
import m_backup
import m_upload


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='ship model folder path.')
    parser.add_argument('--input-raw', help='raw model folder path.')
    parser.add_argument('--project-name', '-p', required=True)
    parser.add_argument('--language', '-l', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--continue', '-c', dest='cont', action='store_true', help='skip done action.')
    group.add_argument('--overwrite', '-ow', action='store_true', help='remove all have done, and redo.')
    return parser.parse_args()


def main():
    args = parse_args()
    backup = m_backup.BackupRlease(args.input, args.input_raw,
                                   args.language, args.project_name)

    overwrite = Overwrite.no_set
    if args.cont:
        overwrite = Overwrite.skip
    elif args.overwrite:
        overwrite = Overwrite.overwrite

    backup.backup_release(overwrite)
    backup.backup_raw(overwrite)
    backup.change_latest()

    language = backup.language_folder[backup.norm_language(args.language)]
    project = backup.project_show_name[backup.norm_project(args.project_name)]
    tar_bz2 = '{0}_{1}_{2}.tar.bz2'.format(language, project, backup.date)

    Tar(backup.backup_folder, tar_bz2, overwrite)
    m_upload.upload(os.path.join(backup.backup_folder, tar_bz2), project)


if __name__ == '__main__':
    main()