#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from google.protobuf import text_format
from enum import Enum
import recognizer_params_pb2
import argparse
import os

# 先把通用的做了，再做各个语言的默认情况


class Platform(Enum):
    Server = 1
    Device = 2


class GraphType(object):
    HCLG = 'HclgDecoderResource'
    CLG = 'ClgDecoderResource'


class ResocreModelType(object):
    KenLM = 'KenLMRescorer'


class ModelLanguage(Enum):
    Mandarin = 0
    Cantonese = 1
    English = 2
    Sichuan = 3
    Contact = 4
    VoiceInput = 5
    SmartTV = 6


class RecoConfigGenerater(object):
    def __init__(self, model_path, platform=Platform.Server):
        self.platform = platform
        self.reco_params = recognizer_params_pb2.RecognizerModelParams()
        self.root_path = model_path
        self.reco_params.acoustic_model = os.path.join(self.root_path, 'final.mdl')
        self.reco_params.nnet_config_file = os.path.join(self.root_path, 'nnet_config')
        self.set_cmvn()
        self.set_silence_detection()
        self.set_word_segmenter()


    def full_path(self, *filename):
        return os.path.join(self.root_path, *filename)


    def set_silence_detection(self):
        if self.platform == Platform.Device:
            self.reco_params.silence_detection_config_file = os.path.join(self.root_path, 'vad.config')
        else:
            self.reco_params.silence_detection_config_file = os.path.join(self.root_path, 'combined.dnn.decoder.vad.config.binary')


    def set_word_segmenter(self):
        if self.platform == Platform.Device:
            self.reco_params.word_segmenter_file = os.path.join(self.root_path, 'segmenter.trie')
            self.reco_params.use_online_cmn = False


    def set_cmvn(self):
        if self.platform == Platform.Device:
            self.reco_params.cmvn_train = os.path.join(self.root_path, 'cmvn_train.ark')
        else:
            self.reco_params.cmvn_train = os.path.join(self.root_path, 'cmvn', 'cmvn_train.ark')


    def set_acoustic_model_type(self, m_type='kNnet3'):
        self.reco_params.acoustic_model_type = m_type


    def set_word_symbol_table(self, is_binary=False, build_path=''):
        if is_binary:
            self.reco_params.binary_symbol_table = True
            if build_path:
                self.reco_params.word_symbol_table = build_path
            else:
                self.reco_params.word_symbol_table = os.path.join(self.root_path, 'base_words')
        else:
            self.reco_params.word_symbol_table = os.path.join(self.root_path, 'words.txt')


    def set_noise_filter_model(self, noise_filter):
        if noise_filter:
            self.reco_params.enable_noise_filter = True
            self.reco_params.post_processor_config.model_type.append('NoiseFilter')
            self.reco_params.post_processor_config.noise_filter_param.noise_model = os.path.join(self.root_path, 'noise_model.one')
            self.reco_params.post_processor_config.noise_filter_param.model_params = os.path.join(self.root_path, 'noise_model_config')


    def set_itn_model(self, itn, replacement):
        if itn or replacement:
            self.reco_params.post_processor_config.model_type.append('InverseTextNormalizer')
            if itn:
                self.reco_params.post_processor_config.inverse_text_normalizer_param.rule_fst = os.path.join(self.root_path, 'rule.fst')
            if replacement:
                self.reco_params.post_processor_config.inverse_text_normalizer_param.replacement_list = os.path.join(self.root_path, 'word_replacement.txt')


    def set_post_processor(self, itn=True, replacement=True,
                           noise_filter=False):
        self.set_itn_model(itn, replacement)
        self.set_noise_filter_model(noise_filter)


    def set_tn_models(self, tn=False):
        m_folder = self.full_path('tn')
        if not tn or not os.path.exists(m_folder):
            return None
        model_list = []
        for _, _, files in os.walk(m_folder):
            for f in files:
                model_list.append(os.path.join(m_folder, f))
        if model_list:
            self.reco_params.tn_rule_fst = ','.join(model_list)


    def set_query_white_list(self):
        self.reco_params.query_white_list = self.full_path('query_white_list.txt')


    def set_eos_predictor(self):
        self.reco_params.eos_predictor_file = self.full_path('3term_3gram_v2.model.bin')


    def set_poi_rescore_model(self, order, model_path, relabel_path, weight):
        self.reco_params.graph_resource_config.lm_rescorer_config.base_score_config.weight.append(weight)
        poi_lm = self.reco_params.graph_resource_config.lm_rescorer_config.kenlm_config.add()
        poi_lm.ngram_order = order
        poi_lm.model_path = model_path
        poi_lm.relabel_file_path = relabel_path


    def set_rescore_model(self, order=3, model_typ='KenLMRescorer',
                          model_path='', relabel_path='',
                          bug_fix_model_path='', bug_fix_relabel='',
                          bug_fix_order=4, bug_fix_weight=0):
        if not model_path:
            model_path = self.full_path('lm.binary')
        if not relabel_path:
            relabel_path = self.full_path('relabel.bin')
        self.reco_params.graph_resource_config.lm_rescorer_config.model_type = model_typ
        if model_typ == ResocreModelType.KenLM:
            self.reco_params.graph_resource_config.lm_rescorer_config.homophone_path = self.full_path('homophone.bin')
            rescore_lm = self.reco_params.graph_resource_config.lm_rescorer_config.kenlm_config.add()
            rescore_lm.ngram_order = order
            rescore_lm.model_path = model_path
            rescore_lm.relabel_file_path = relabel_path
            if self.platform == Platform.Server:
                self.reco_params.graph_resource_config.lm_rescorer_config.base_score_config.weight.append(1)
                self.reco_params.graph_resource_config.lm_rescorer_config.base_score_config.weight.append(bug_fix_weight)
                bug_fix_lm = self.reco_params.graph_resource_config.lm_rescorer_config.kenlm_config.add()
                bug_fix_lm.ngram_order = bug_fix_order
                bug_fix_lm.model_path = bug_fix_model_path
                bug_fix_lm.relabel_file_path = bug_fix_relabel


    def set_graph_models(self, is_static=True, build_folder='', 
                         model_type='ClgDecoderResource', is_contact=False,
                         null_fst=''):
        if is_static and is_contact:
            raise ValueError
        self.reco_params.graph_resource_config.model_type = model_type
        self.reco_params.graph_resource_config.transition_model = os.path.join(self.root_path, 'arcs.far')
        if is_static:
            self.reco_params.graph_resource_config.graph = os.path.join(self.root_path, 'CLG.fst')
        else:
            model_paths = ','.join([self.full_path('CL.fst'),
                                    self.full_path('G.fst')])
            if self.platform == Platform.Device:
                model_paths = ','.join([model_paths,
                                        os.path.join(build_folder, 'DATA-ALBUM.fst'),
                                        os.path.join(build_folder, 'DATA-APP.fst'),
                                        os.path.join(build_folder, 'DATA-ARTIST.fst'),
                                        os.path.join(build_folder, 'DATA-CONTACT.fst'),
                                        os.path.join(build_folder, 'DATA-SONG.fst'),
                                        os.path.join(build_folder, 'DATA-VIDEO.fst')])
            else:
                if is_contact:
                    if not null_fst:
                        raise ValueError('Please set null.fst path.')
                    model_paths = ','.join([model_paths,
                                            null_fst, null_fst,
                                            null_fst, null_fst])
                    self.reco_params.graph_resource_config.relabel_file = self.full_path('g.irelabel')
                    self.reco_params.graph_resource_config.expander_cache_config.state_table_path = self.full_path('state_table.bin')
                    self.reco_params.graph_resource_config.expander_cache_config.replace_state_table_path = self.full_path('replace_state_table.bin')
                    self.reco_params.graph_resource_config.expander_cache_config.expander_cache_path = self.full_path('expander_cache.bin')
            self.reco_params.graph_resource_config.graph = model_paths


    def set_context_config(self, full_match=True, length_linear=True,
                           alpha=0.9, beta=1.0, p1=-1, p2=-4):
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.full_match = full_match
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.length_linear = length_linear
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.alpha = alpha
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.beta = beta
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.p1 = p1
        self.reco_params.graph_resource_config.lm_rescorer_config.function_config.app_context.p2 = p2


    def set_device_default(self, build_path, m_type='kOne', tn=False,
                           itn=True, replacement=True, noise_filter=False,
                           query_white_list=False):
        self.platform = Platform.Device
        self.set_acoustic_model_type(m_type)
        build_words_path = os.path.join(build_path, 'words.symb')
        self.set_word_symbol_table(True, build_words_path)
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_graph_models(False, build_path)
        self.set_rescore_model()
        if query_white_list:
            self.set_query_white_list()


    def set_server_default(self, m_type='kNnet3', tn=False,
                           itn=True, replacement=True, noise_filter=True):
        """
        Server default is static CLG and no POI rescore, no bug fix model.
        """
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_graph_models()
        self.set_rescore_model(4)


    def set_contact_server_default(self, m_type='kNnet3', tn=False,
                           itn=True, replacement=True, noise_filter=True):
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        null_fst = self.full_path('null.fst')
        self.set_graph_models(is_static=False, is_contact=True, null_fst=null_fst)
        self.set_rescore_model(4)


    def set_auto_mandarin_server_default(self, bug_fix_folder, bug_fix_order=4,
                                         bug_fix_weight=0.01,
                                         m_type='kNnet3', tn=False, itn=True,
                                         replacement=True, noise_filter=True):
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_context_config()
        self.set_graph_models()
        bug_fix_model = os.path.join(bug_fix_folder, 'bug_lm.bin')
        bug_fix_rel = os.path.join(bug_fix_folder, 'bug_relabel.bin')
        self.set_rescore_model(order=4, bug_fix_model_path=bug_fix_model,
                               bug_fix_relabel=bug_fix_rel,
                               bug_fix_order=bug_fix_order,
                               bug_fix_weight=bug_fix_weight)
        # (area_name, weight, order)
        poi_area = [('huadong_south', 0.5, 4), ('huanan', 0.5, 4),
                    ('huabei', 0.5, 4), ('dongbei', 0.5, 4),
                    ('huazhong', 0.5, 4), ('xibei', 0.5, 4),
                    ('xinan', 0.5, 4), ('huadong_north', 0.5, 4)]
        for area in poi_area:
            poi_model_path = self.full_path('poi', '{}_lm.bin'.format(area[0]))
            poi_rel_path = self.full_path('poi', '{}_relabel.bin'.format(area[0]))
            weight = area[1]
            poi_order = area[2]
            self.set_poi_rescore_model(poi_order, poi_model_path, poi_rel_path, weight)


    def set_auto_cantonese_server_default(self, bug_fix_folder, bug_fix_order=4,
                                          bug_fix_weight=0.1,
                                          m_type='kNnet3', tn=False, itn=True,
                                          replacement=True, noise_filter=False):
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_graph_models()
        bug_fix_model = os.path.join(bug_fix_folder, 'bug_lm.bin')
        bug_fix_rel = os.path.join(bug_fix_folder, 'bug_relabel.bin')
        self.set_rescore_model(order=4, bug_fix_model_path=bug_fix_model,
                               bug_fix_relabel=bug_fix_rel,
                               bug_fix_order=bug_fix_order,
                               bug_fix_weight=bug_fix_weight)
        # (area_name, weight, order)
        poi_area = [('huadong_south', 0.35, 4), ('huadong_north', 0.35, 4),
                    ('huanan', 0.2, 4), ('huabei', 0.35, 4),
                    ('dongbei', 0.35, 4)]
        for area in poi_area:
            poi_model_path = self.full_path('poi', '{}_lm.bin'.format(area[0]))
            poi_rel_path = self.full_path('poi', '{}_relabel.bin'.format(area[0]))
            weight = area[1]
            poi_order = area[2]
            self.set_poi_rescore_model(poi_order, poi_model_path, poi_rel_path, weight)


    def set_auto_sichuan_server_default(self, bug_fix_folder, bug_fix_order=4,
                                        bug_fix_weight=0.1,
                                        m_type='kNnet3', tn=False, itn=True,
                                        replacement=True, noise_filter=False):
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_graph_models()
        bug_fix_model = os.path.join(bug_fix_folder, 'bug_lm.bin')
        bug_fix_rel = os.path.join(bug_fix_folder, 'bug_relabel.bin')
        self.set_rescore_model(order=4, bug_fix_model_path=bug_fix_model,
                               bug_fix_relabel=bug_fix_rel,
                               bug_fix_order=bug_fix_order,
                               bug_fix_weight=bug_fix_weight)
        # (area_name, weight, order)
        poi_area = [('huadong_south', 0.3, 5), ('huanan', 0.3, 5),
                    ('huabei', 0.3, 5), ('dongbei', 0.3, 5),
                    ('huazhong', 0.3, 5), ('xibei', 0.3, 5),
                    ('xinan', 0.3, 5), ('huadong_north', 0.3, 5)]
        for area in poi_area:
            poi_model_path = self.full_path('poi', '{}_lm.bin'.format(area[0]))
            poi_rel_path = self.full_path('poi', '{}_relabel.bin'.format(area[0]))
            weight = area[1]
            poi_order = area[2]
            self.set_poi_rescore_model(poi_order, poi_model_path, poi_rel_path, weight)


    def set_auto_enu_server_default(self, m_type='kNnet3', tn=False, itn=True,
                                    replacement=True, noise_filter=False):
        self.platform = Platform.Server
        self.set_acoustic_model_type(m_type)
        self.set_word_symbol_table()
        self.set_post_processor(itn, replacement, noise_filter)
        self.set_tn_models(tn)
        self.set_graph_models()
        self.set_query_white_list()
        self.set_rescore_model(order=4)


    def generate_config(self, outpath):
        output_folder = os.path.dirname(outpath)
        if (output_folder != '' and
            output_folder != '.' and 
            not os.path.exists(output_folder)):
            os.makedirs(output_folder)
        with open(outpath, 'w') as ofile:
            ofile.write(text_format.MessageToString(self.reco_params))


    def generate_auto_server_by_language(self, language, bug_fix_folder=''):
        if language == ModelLanguage.Mandarin:
            self.set_auto_mandarin_server_default(bug_fix_folder)
        elif language == ModelLanguage.Cantonese:
            self.set_auto_cantonese_server_default(bug_fix_folder)
        elif language == ModelLanguage.Sichuan:
            self.set_auto_sichuan_server_default(bug_fix_folder)
        elif language == ModelLanguage.English:
            self.set_auto_enu_server_default()


    def generate_auto_device_by_language(self, language, m_type, build_path):
        if language == ModelLanguage.English:
            self.set_device_default(build_path, m_type=m_type, query_white_list=True)
        else:
            self.set_device_default(build_path, m_type=m_type)


def parse_args(args):
    if args.platform == 'server':
        if args.build_folder:
            print('build folder setting just for device, ignore it.')
    if args.platform == 'device':
        if not args.build_folder:
            raise ValueError('not set build folder for device.')
        if args.bug_fix_folder:
            print('device not support bug fix model, ignore it.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate default proto for server and device test.')
    parser.add_argument('--model-folder', required=True)
    parser.add_argument('--platform', required=True, choices=['server', 'device'])
    parser.add_argument('--language', required=True, choices=['chs', 'enu', 'yue', 'chuan'])
    parser.add_argument('--am-type', default='kNnet3', choices=['kNnet3, kOne'])
    parser.add_argument('--build-folder', default='')
    parser.add_argument('--bug-fix-folder', default='')
    parser.add_argument('--output-proto', required=True)
    argvs = parser.parse_args()
    parse_args(argvs)

    language = {
        'chs': ModelLanguage.Mandarin,
        'enu': ModelLanguage.English,
        'yue': ModelLanguage.Cantonese,
        'chuan': ModelLanguage.Sichuan,
    }

    p = RecoConfigGenerater(argvs.model_folder)
    if argvs.platform == 'server':
        p.generate_auto_server_by_language(language[argvs.language],
                                           argvs.bug_fix_folder)
    else:
        p.generate_auto_device_by_language(language[argvs.language],
                                           argvs.am_type,
                                           argvs.build_folder)
    p.generate_config(argvs.output_proto)
