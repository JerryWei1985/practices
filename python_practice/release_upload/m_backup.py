#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from enum import Enum
from datetime import datetime
from m_tar import Overwrite

import argparse
import os
import shutil


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
        Language.CHS: {'chs', 'cn', 'zh-cn', 'zh_cn', 'zh'},
        Language.YUE: {'yue', 'zh-yue', 'zh_yue', 'hk', 'zh-hk', 'zh_hk'},
        Language.CHUAN: {'chuan', 'sichuan', 'zh-chuan', 'zh_chuan', 'si-chuan', 'si_chuan'},
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


    project_show_name = {
        ProjectName.Auto: 'auto',
        ProjectName.VoiceInput: 'voice-input',
        ProjectName.TicHome: 'tichome',
        ProjectName.TicWatch: 'ticwatch'
    }


    def __init__(self, release_model_folder, raw_model_folder,
                 language, project):
        self.done = 'done'
        self.date = datetime.today().strftime('%Y%m%d')
        self.language = self.norm_language(language)
        self.project = self.norm_project(project)
        self.release_folder = release_model_folder
        self.raw_folder = raw_model_folder
        self.backup_folder = self.get_backup_folder(self.date)


    def yes_no_input(self, massage):
        yes = {'yes', 'y', 'Y', 'YES'}
        value = input(massage)

        if value in yes:
            return True
        return False


    def copy_file(self, file_path, dest_path, overwrite=Overwrite.no_set):
        if not os.path.exists(file_path):
            raise IOError('There is no {}.'.format(file_path))

        if os.path.isdir(dest_path):
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(dest_path, file_name)
        elif os.path.exists(dest_path):
            if (overwrite == Overwrite.no_set and
                not self.yes_no_input('{} has exited, replace it? [y/n] '.format(dest_path))):
                return None
            elif overwrite == Overwrite.skip:
                print('Exists, skip {}'.format(file_path))
                return None

            print('Exists, remove {}'.format(dest_path))
            os.remove(dest_path)
        else:
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

        print('Copy {}'.format(file_path))
        shutil.copy2(file_path, dest_path)


    def copy_folder(self, file_folder, dest_folder, overwrite=Overwrite.no_set):
        if not os.path.exists(file_folder):
            raise IOError('There is no {}'.format(file_folder))

        if not os.path.isdir(file_folder):
            raise IOError('{} is not a folder.'.format(file_folder))

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        elif not os.path.isdir(dest_folder):
            raise IOError('{} is not a folder.'.format(dest_folder))

        files = os.listdir(file_folder)
        for f in files:
            file_path = os.path.join(file_folder, f)
            dest_path = os.path.join(dest_folder, f)
            if os.path.isfile(file_path):
                self.copy_file(file_path, dest_path, overwrite)
            elif os.path.isdir(file_path):
                self.copy_folder(file_path, dest_path, overwrite)
            elif os.path.islink(file_path):
                file_path = self.get_realpath(file_path)
                if os.path.isdir(file_path):
                    self.copy_folder(file_path, dest_path, overwrite)
                elif os.path.isfile(file_path):
                    self.copy_file(file_path, dest_path, overwrite)


    def get_realpath(self, file_path):
        if not os.path.islink(file_path):
            return file_path

        realpath = os.readlink(file_path)
        if realpath.startswith('/'):
            return realpath

        return os.path.join(file_path, realpath)


    def check_soft_link(self, file_path):
        if not os.path.exists(file_path):
            return True
        if not os.path.islink(file_path):
            raise IOError('{} is not a soft link.'.format(file_path))

        real_file_path = os.readlink(file_path)
        base_name = os.path.basename(real_file_path)
        if self.date == base_name:
            return False

        return True

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
        # 这里车载项目会有些问题，因为当前都放到了cns目录下，没有区分不同项目
        folder_format = '/export/release/{}/{}/server-asr/{}'
        lang_folder = self.language_folder[self.language]
        pro_folder = self.project_folder[self.project]

        return folder_format.format(pro_folder, lang_folder, version)

#    def backup_release(self):
#        index = 0
#        while os.path.isdir(self.backup_folder):
#            index += 1
#        if index != 0:
#            self.backup_folder = '{}-{}'.format(self.backup_folder, index)
#        print('Backup release model files.')
#        shutil.copytree(self.release_folder, self.backup_folder)
#        print(self.backup_folder)


    def backup_release(self, overwrite=Overwrite.no_set):
        done_file = os.path.join(self.backup_folder, self.done)
        if overwrite == Overwrite.skip:
            if os.path.exists(done_file):
                print('Backup has been done. If you want to redo, please remove {}'.format(done_file))
                return
        elif overwrite == Overwrite.no_set:
            if os.path.exists(done_file):
                check = self.yes_no_input('Backup has been done, redo or not? [y/n]')
                if not check:
                    return

        if os.path.exists(self.backup_folder):
            print('Backup folder has exited, remove {}'.format(self.backup_folder))
            shutil.rmtree(self.backup_folder)

        print('Backup release model files.')
        self.copy_folder(self.release_folder, self.backup_folder, Overwrite.overwrite)
        open(done_file, 'a').close()
        print(self.backup_folder)


    def backup_raw(self, overwrite=Overwrite.no_set):
        if self.raw_folder and os.path.exists(self.raw_folder):
            backup_raw_folder = os.path.join(self.backup_folder, 'raw')
            done_file = os.path.join(backup_raw_folder, self.done)

            if overwrite == Overwrite.no_set:
                if os.path.exists(done_file):
                    check = self.yes_no_input(
                        '{} has existed, remove it or not? [y/n]'.format(backup_raw_folder))
                    if not check:
                        return
            elif overwrite == Overwrite.skip:
                if os.path.exists(done_file):
                    print('Backup raw has been done. If you want to redo, please remove {}'.format(done_file))
                    return

            if os.path.exists(backup_raw_folder):
                print('Backup raw folder has existed, remove {}'.format(backup_raw_folder))
                shutil.rmtree(backup_raw_folder)

            print('Backup raw model files.')
            self.copy_folder(self.raw_folder, backup_raw_folder, Overwrite.overwrite)
            open(done_file, 'a').close()
            print(backup_raw_folder)


    def change_latest(self):
        pwd = os.getcwd()
        os.chdir(os.path.dirname(self.backup_folder))
        latest_link = 'latest'

        if self.check_soft_link(latest_link):
            print('Update latset folder link.')

            if os.path.islink('latest'):
                os.remove(latest_link)
            os.symlink(self.date, latest_link)

        os.chdir(pwd)
        print('Finish backup.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='release model folder.')
    parser.add_argument('--input-raw', default='', help='model folder, which before FST conversion.')
    parser.add_argument('--project-name', '-p', required=True)
    parser.add_argument('--language', '-l', required=True)
    parser.add_argument('--overwrite', '-ow', action='store_true')
    args = parser.parse_args()

    overwrite = Overwrite.skip
    if args.overwrite:
        overwrite = Overwrite.overwrite

    backup = BackupRlease(args.input, args.input_raw,
                          args.language, args.project_name)
    backup.backup_release(overwrite)
    backup.backup_raw(overwrite)
    backup.change_latest()