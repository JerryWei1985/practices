#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import unittest
import sys
import os

import m_upload_release


class TestBackup(unittest.TestCase):
    def __init__(self):
        self.backup = m_upload_release.BackupRlease('', '', '', '')

    def test_normal_language(self):
        # zh-cn
        zh_cn_list = [
            'zh-cn', 'zh_cn', 'zh-CN', 'zh_CN', 'ZH-CN', 'ZH_CN', 'cn', 'CN',
            'chs', 'CHS', 'chS', 'Chs', 'zh-chs', 'zh_chs', 'zh-CHS', 'zh_CHS',
            'zh', 'ZH', 'zhcn', 'ZHCN', 'Chs', 'Cn', 'Zh', 'zhCN'
        ]
        # en-us
        en_us_list = [
            'en-us', 'en_us', 'en-US', 'en_US', 'EN-US', 'EN_US', 'en', 'EN',
            'enu', 'ENU', 'Enu', 'enus', 'ENUS', 'enUS', 'us', 'US', 'usa',
            'USA', 'Us', 'uS', 'eN', 'En'
        ]
        # yue
        yue_list = [
            'yue', 'YUE', 'Yue', 'zh-yue', 'zh_yue', 'zh-YUE', 'zh_YUE',
            'zhyue', 'zh-hk', 'zh_hk', 'zh-HK', 'zh_HK', 'zhhk', 'zhHK',
            'hk', 'HK'
        ]
        # sichuan
        sichuan_list = [
            'sichuan', 'chuan', 'zh-chuan', 'zh_chuan', 'zh-Chuan', 'Chuan',
            'si-chuan', 'si_chuan', 'chuan'
        ]
        for zh in zh_cn_list:
            lang = self.backup.norm_language(zh)
            self.assertEqual(lang, m_upload_release.Language.CHS)
        for us in en_us_list:
            lang = self.backup.norm_language(us)
            self.assertEqual(lang, m_upload_release.Language.ENU)
        for yue in yue_list:
            lang = self.backup.norm_language(yue)
            self.assertEqual(lang, m_upload_release.Language.YUE)
        for chuan in sichuan_list:
            lang = self.backup.norm_language(chuan)
            self.assertEqual(lang, m_upload_release.Language.CHUAN)

    def test_normal_project(self):
        pass

    def test_get_release_folder(self):
        pass

    def test_check_model_files(self):
        pass

if __name__ == '__main__':
    unittest.main()