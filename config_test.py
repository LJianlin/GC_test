#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
# Copyright (c) 2020 Baidu.com, Inc. All Rights Reserved
#
# File: start_serve.py
# Project: framework
# Created Date: Wednesday, June 10th 2020, 10:00:08 pm
# Author: liruifeng02
# -----
# Last Modified: Thu Jul 02 2020
# Modified By: liruifeng02
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
"""
import time
import codecs
import shutil
import configparser
import multiprocessing
import os
import subprocess
import sys
from six.moves import shlex_quote
from importlib import import_module

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# from utils import authentication, utils, simple_logger

default_conf_parameters = {
    'config':
        {'cfg': "../config/paddle_model.conf"},

    'auth':
        {'is_auth': True,
         'auth_path': "../src/",
         'auth_module': "authentication",
         'auth_method': "auth",
         'decrypt_model_method': "decrypt_file"},

    'model': {'activate_models': [1],
              'model_gpu_map': {"1": "0"},
              'model_port_map': {"1": "9001"},
              'model_use': {"1": "PaddleDemoModel"},
              'model_path': "../src/",
              'model_module': "paddle_model"},

    'pipeline': {'activate_pipelines': [1],
                 'pipeline_port_map': {"1": "8001"},
                 'pipeline_use': {"1": "PaddleDemoPipeline"},
                 'pipeline_path': "../src/",
                 'pipeline_module': "paddle_pipeline"}}


def conf_parse(conf):
    """

    Returns:

    """
    assert os.path.exists(conf), print("The {} file is not exist.".format(conf))

    default_sections = list(default_conf_parameters.keys())
    conf_parser = configparser.ConfigParser()
    try:
        conf_parser.readfp(codecs.open(conf, "r", "utf-8-sig"))
        conf_sections = conf_parser.sections()

        final = {}
        inter_sections = list(set(conf_sections) & set(default_sections))
        for section in inter_sections:
            conf_options = conf_parser.options(section)
            default_options = default_conf_parameters[section].keys()
            final[section] = {}

            diff_options = list(set(default_options) - set(conf_options))
            if len(diff_options) > 0:
                for option in diff_options:
                    final[section][option] = default_conf_parameters[section][option]
                    print("The '{}.{}' of confing is set to default!".format(section, option))

            inter_options = list(set(default_options) - set(diff_options))
            if len(inter_options) > 0:
                for option in inter_options:
                    final[section][option] = eval(conf_parser.get(section, option))

        diff_sections = list(set(default_sections) - set(inter_sections))
        if len(diff_sections) > 0:
            for section in diff_sections:
                final[section] = {}
                for option in default_conf_parameters[section]:
                    final[section][option] = default_conf_parameters[section][option]
                    print("The '{}.{}' of confing is set to default!".format(section, option))

        self.paddle_model_cfg = final['config']['cfg']

        self.is_auth = final['auth']['is_auth']
        self.auth_path = final['auth']['auth_path']
        self.auth_module = final['auth']['auth_module']
        self.auth_method = final['auth']['auth_method']
        self.decrypt_model_method = final['auth']['decrypt_model_method']

        self.activate_models = final['model']['activate_models']
        self.model_gpu_map = final['model']['model_gpu_map']
        self.model_port_map = final['model']['model_port_map']
        self.model_use = final['model']['model_use']
        self.model_path = final['model']['model_path']
        self.model_module = final['model']['model_module']

        self.activate_pipelines = final['pipeline']['activate_pipelines']
        self.pipeline_port_map = final['pipeline']['pipeline_port_map']
        self.pipeline_use = final['pipeline']['pipeline_use']
        self.pipeline_path = final['pipeline']['pipeline_path']
        self.pipeline_module = final['pipeline']['pipeline_module']

    except Exception as e:
        logging.fatal("Fail to parse conf as Exception: {}".format(e))
        # print("Fail to parse conf as Exception: {}".format(e))


if __name__ == "__main__":
    """
    main
    """
    config = "config.conf"
    # start_task(config)
    # conf_parse()
    # args = ParseConf(config)
    # args.\
    conf_parse(config)
