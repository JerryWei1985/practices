#!/usr/bin/env python3
# coding=utf-8


import argparse
import sys
import m_grep
import m_upload
import m_delete


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['upload', 'delete', 'grep'],
        help=''
    )
    action = None
    if len(sys.argv) > 1:
        action = [sys.argv[1]]
    action_args = parser.parse_args(action)
    args = None
    if len(sys.argv) > 2:
        args = sys.argv[2:]

    if action_args.action == 'upload':
        m_upload.main(args, action_args.action)
    elif action_args.action == 'delete':
        m_delete.main(args, action_args.action)
    elif action_args.action == 'grep':
        m_grep.main(args, action_args.action)


if __name__ == '__main__':
    main()