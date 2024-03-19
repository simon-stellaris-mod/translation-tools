# encoding=utf-8

""" Translation
    Author: lipixun
    Created Time : 2024-03-14 15:00:12

    File Name: localization.py
    Description:

"""
from typing import Dict, List, NamedTuple

import os.path

from utils import LanguageNames

# Defines a localized value with its language
LocalizationValue = NamedTuple("LocalizationValue", [("language", str), ("value", str)])
# Defines an localized item for a specific key with multiple values
LocalizationItem = NamedTuple("LocalizationItem", [("key", str), ("values", List[LocalizationValue])])

# Stellaris: File name suffix format
FileNameSuffix = ["_l_%s.yml" % lang for lang in LanguageNames]
# Stellaris: Header line format
FileHeaderMapping = {"l_%s" % lang: lang for lang in LanguageNames}


class LocalizationManager(object):
    """Localization manager
    """

    def __init__(self, enabled_languages: List[str] | None = None) -> None:
        """Create a new LocalizationManager
        """
        self._enabled_languages = enabled_languages
        self._items: Dict[str, LocalizationItem] = {}
        self._sorted_keys: List[str] | None = None

    @property
    def sorted_keys(self) -> List[str]:
        """Get sorted keys
        """
        if self._sorted_keys is None:
            self._sorted_keys = sorted(self._items.keys())
        return self._sorted_keys

    def get(self, key, default=None):
        """Get item
        """
        return self._items.get(key, default)

    def load(self, file_or_dir_path: str):
        """Load or reload data
        """
        if os.path.isdir(file_or_dir_path):
            self._read_directory(file_or_dir_path)
        elif os.path.isfile(file_or_dir_path):
            self._read_file(file_or_dir_path)

    def _read_directory(self, dirpath: str) -> None:
        """Read directory
        """
        for name in os.listdir(dirpath):
            fullpath = os.path.join(dirpath, name)
            if os.path.isdir(fullpath):
                self._read_directory(fullpath)
            elif os.path.isfile(fullpath):
                self._read_file(fullpath)

    def _read_file(self, filepath: str) -> None:
        """Read file
        """
        with open(filepath, "r", encoding="utf-8-sig") as fd:
            #
            # Why not parse by a yaml library?
            #
            #   I have found lots of errors in mod localisation files (Invalid empty line with indents as prefix; invalid number after colon; unescaped chars...)
            #   So I decided to parse the file by myself (But write will be proceed by a yaml library) and ignore any errors.
            #

            # Read file header
            line = fd.readline().strip()
            if not line.endswith(":"):
                raise ValueError("Invalid file. Malformed header line [%s]." % line)
            if not line[:-1] in FileHeaderMapping:
                raise ValueError("Invalid file. Malformed header line [%s]." % line)
            language = FileHeaderMapping[line[:-1]]
            # Check enabled languages
            if self._enabled_languages and language not in self._enabled_languages:
                return
            # Read line by line
            for line in fd.readlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if not line.endswith("\""):
                    continue
                index1 = line.find(":")
                index2 = line.find("\"")
                if index1 < 0 or index2 < 0:
                    continue
                key = line[:index1].strip()
                value = line[index2+1:-1].strip()
                # Unescape
                value = value.replace("\\n", "\n").replace("\\\"", "\"").replace("\\\\", "\\")
                # Add it
                if key not in self._items:
                    self._items[key] = LocalizationItem(key, [LocalizationValue(language, value)])
                else:
                    self._items[key].values.append(LocalizationValue(language, value))

    def _check_filename(self, filename: str) -> bool:
        """Check filename
        """
        for suffix in FileNameSuffix:
            if filename.endswith(suffix):
                return True
        return False
