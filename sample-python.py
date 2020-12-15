import importlib
import logging
import os
import re
from collections import namedtuple

import omegaconf
import torch
from omegaconf import OmegaConf

import util
from dataset import Dataset
from enums import Algorithm, Device, EpsilonDecayType
from exceptions import InvalidConfiguration


class ConfigObj(object):
    """ConfigObj is literally that: an object that contains the entire configuration
    for specific runs of the project in question.  It is usually derived from an
    omegaconf dictionary (https://omegaconf.readthedocs.io/en/2.0_branch/)
    
    """

    def __init__(self, dictionary={}):
        def _traverse(key, element):

            if isinstance(element, (dict, omegaconf.dictconfig.DictConfig)):
                return key, ConfigObj(element)
            else:
                return key, element

        objd = dict(_traverse(k, v) for k, v in dictionary.items())
        self.__dict__.update(objd)

    def __repr__(self, level=0):

        ret = ""

        for k in sorted(vars(self)):
            if not re.search("^__", k):
                if k in ["time_breaks", "order_depths"]:
                    ret += f"\n{4 * level * ' '}{k}:\n{getattr(self, k)}"
                else:
                    if isinstance(getattr(self, k), (ConfigObj)):
                        ret += f"\n{4 * level * ' '}{k}:"
                        ret += getattr(self, k).__repr__(level=level + 1)
                    else:
                        ret += f"\n{4 * level * ' '}{k}: {getattr(self, k)}"

        return ret

    def update(self, source):

        for k, v in vars(source).items():

            if isinstance(v, ConfigObj):

                if hasattr(self, k):

                    getattr(self, k).update(v)

                else:
                    setattr(
                        self, k, ConfigObj(vars(type("config", (object,), vars(v))))
                    )
            else:
                setattr(self, k, v)

        return self

