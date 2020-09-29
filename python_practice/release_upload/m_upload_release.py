#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import os
from enum import Enum
from datetime import datetime


class Language(Enum):
    ENU = 0
    CHS = 1
    YUE = 2
    CHUAN = 3
    HK_YUE = 4
    TW = 5

class ProjectName(Enum):
    Auto = 0
    TicHome = 1
    TicWatch = 2
    VoiceInput = 3

class BackupRlease(object):
    language_set = {
        Language.ENU: {'enu', 'en', 'en-us', 'en_us'},
        Language.CHS: {'chs', 'zh', 'zh-cn', 'zh_cn'},
        Language.YUE: {'yue', 'zh-yue', 'zh_yue'},
        Language.CHUAN: {'chuan', 'sichuan', 'zh-chuan', 'zh_chuan'},
        Language.TW: {'tw', 'zh-tw', 'zh_tw'}
    }

    project_name = {
        ProjectName.Auto: {'cns', 'ebo', 'icas', 'audi', '37w', 'kodai', 'ticmirror', 'soa'},
        ProjectName.VoiceInput: {'voice-input', 'voice_input', 'voiceinput'},
        ProjectName.TicWatch: {'ticwatch', 'tic_watch', 'tic-watch'},
        ProjectName.TicHome: {'tichome', 'tic_home', 'tic-home'}
    }

    language_folder = {
        Language.ENU: 'en-us',
        Language.CHS: 'zh-cn',
        Language.YUE: 'zh-yue',
        Language.CHUAN: 'zh-chuan',
        Language.TW: 'zh-tw'
    }

    project_folder = {
        ProjectName.Auto: 'auto/cns',
        ProjectName.VoiceInput: 'voice-input/adults',
        ProjectName.TicHome: 'tichome/big',
        ProjectName.TicWatch: 'ticwatch/adults'
    }

    def __init__(self, release_model_folder, raw_model_folder,
                 language, project):
        self.date = datetime.today()
        self.language = self.norm_language(language)
        self.project = self.norm_project(project)
        self.release_folder = release_model_folder
        self.raw_folder = raw_model_folder
        self.backup_folder = self.get_backup_folder(self.date.strftime('%Y%m%d'))

    def norm_language(self, lang):
        if lang.lower() in self.language_set[Language.CHS]:
            return Language.CHS
        elif lang.lower() in self.language_set[Language.ENU]:
            return Language.ENU
        elif lang.lower() in self.language_set[Language.TW]:
            return Language.TW
        elif lang.lower() in self.language_set[Language.YUE]:
            return Language.YUE
        elif lang.lower() in self.language_set[Language.CHUAN]:
            return Language.CHUAN
        else:
            raise ValueError('Not support language "{}"'.format(lang))

    def norm_project(self, project):
        if project.lower() in self.project_name[ProjectName.Auto]:
            return ProjectName.Auto
        elif project.lower() in self.project_name[ProjectName.VoiceInput]:
            return ProjectName.VoiceInput
        elif project.lower() in self.project_name[ProjectName.TicWatch]:
            return ProjectName.TicWatch
        elif project.lower() in self.project_name[ProjectName.TicHome]:
            return ProjectName.TicHome
        else:
            raise ValueError('Not support project "{}"'.format(project))

    def get_backup_folder(self, version):
        folder_format = '/export/release/{}/{}/server-asr/{}'
        lang_folder = self.language_folder[self.language]
        pro_folder = self.project_folder[self.project]
        return folder_format.format(pro_folder, lang_folder, version)

    def backup_release(self):
        pass