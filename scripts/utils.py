# encoding=utf-8

""" Utility
    Author: lipixun
    Created Time : 2024-03-14 15:19:21

    File Name: utils.py
    Description:

"""

import sys

try:
    import simplejson as json
except ImportError:
    import json

from ruamel.yaml import YAML

LanguageNames = ["braz_por", "english", "french", "german", "japanese", "korean", "polish", "russian", "simp_chinese", "spanish"]

yaml = YAML()
yaml.width = sys.maxsize        # Prevent from wrap the line
yaml.map_indent = 1             # Only have 1 white space as prefix
yaml.preserve_quotes = True     # Add quotes

__all__ = [
    "json",
    "yaml",
    "LanguageNames",
]
