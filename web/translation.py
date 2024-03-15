# encoding=utf-8

""" Translation
    Author: lipixun
    Created Time : 2024-03-14 15:00:03

    File Name: translation.py
    Description:

"""
from typing import Dict, List, NamedTuple, Tuple

import os
import os.path

from time import time

from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from utils import LanguageNames, json, yaml

LocalisationValue = NamedTuple("LocalisationValue", [("language", str), ("value", str)])
LocalisationFile = NamedTuple("LocalisationFile", [("name", str), ("keys_", List[str]), ("values", List[LocalisationValue])])
LocalisationDirectory = NamedTuple("LocalisationDirectory", [("name", str), ("files", List[LocalisationFile]), ("dirs", List)])
LocalisationItem = NamedTuple("LocalisationItem", [("key", str), ("values", List[LocalisationValue])])

AvailableFileSuffix = ["_l_%s.yml" % lang for lang in LanguageNames]
FileHeaderMapping = {"l_%s" % lang: lang for lang in LanguageNames}


class LocalisationData(object):
    """Localisation data
    """

    def __init__(self, dirpath: str) -> None:
        """Create a new LocalisationData
        """
        self._dir: LocalisationDirectory | None = None
        self._dirpath = dirpath
        self._items: Dict[str, LocalisationItem] | None = None
        self._sorted_keys: List[str] | None = None
        self.reload()

    @property
    def sorted_keys(self):
        """Get sorted keys
        """
        return self._sorted_keys

    def get(self, key, default=None):
        """Get item
        """
        return self._items.get(key, default) if self._items else default

    def reload(self):
        """Load or reload data
        """
        # Read dir
        items: Dict[str, LocalisationItem] = {}
        root_dir = LocalisationDirectory("", [], [])

        def read_dir(dirpath: str, dir_: LocalisationDirectory):
            for name in os.listdir(dirpath):
                fullpath = os.path.join(dirpath, name)
                if os.path.isdir(fullpath):
                    sub_dir = LocalisationDirectory(name, [], [])
                    dir_.dirs.append(sub_dir)
                    read_dir(fullpath, sub_dir)
                elif os.path.isfile(fullpath):
                    if self._check_filename(fullpath):
                        file_ = self._read_file(fullpath)
                        # Add to directory
                        dir_.files.append(file_)
                        # Add to items
                        for i, key in enumerate(file_.keys_):
                            if key not in items:
                                items[key] = LocalisationItem(key, [file_.values[i]])
                            else:
                                items[key].values.append(file_.values[i])

        read_dir(self._dirpath, root_dir)
        self._dir = root_dir
        self._items = items

        # Sort keys
        self._sorted_keys = sorted(self._items.keys())

    def _check_filename(self, filename: str) -> bool:
        """Check filename
        """
        for suffix in AvailableFileSuffix:
            if filename.endswith(suffix):
                return True
        return False

    def _read_file(self, filename: str) -> LocalisationFile:
        """Read file
        """
        file_ = LocalisationFile(os.path.basename(filename), [], [])

        with open(filename, "r", encoding="utf-8-sig") as fd:
            line = fd.readline().strip()
            if not line.endswith(":"):
                raise ValueError("Invalid file. Malformed header line [%s]." % line)
            if not line[:-1] in FileHeaderMapping:
                raise ValueError("Invalid file. Malformed header line [%s]." % line)
            language = FileHeaderMapping[line[:-1]]
            for line in fd.readlines():
                #
                # Why not parsing by pyyaml?
                #
                #   I have found lots of errors in mod localisation files (Invalid empty line with indents as prefix; invalid number after colon; unescaped chars...)
                #   So I decided to parse the file by myself (But write will be proceed by pyyaml) and ignore any errors.
                #
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
                key = line[:index1]
                value = line[index2+1:-1]
                # Unescape
                value = value.replace("\\\"", "\"").replace("\\\\", "\\")
                # Add it
                file_.keys_.append(key)
                file_.values.append(LocalisationValue(language, value))

        return file_


TranslationItem = NamedTuple("TranslationItem", [("original_value", str), ("translate_value", str), ("update_time", int)])


class TranslationManager(object):
    """Translation manager
    """

    def __init__(self, source_dir: str, data_file: str) -> None:
        """Create a new TranslationManager
        """
        self._source_dir = source_dir
        self._data_file = data_file
        self._source_localisation = LocalisationData(source_dir)
        self._translation_data: Dict[str, Dict[str, TranslationItem]] | None = None   # language to key to item
        # Reload all data
        self.reload()

    @property
    def source_localisation(self):
        """Get source localisation
        """
        return self._source_localisation

    def reload(self):
        """Load or reload all necessary data
        """
        self._source_localisation.reload()
        self._load_translation_data()

    def get_keys(self, language: str) -> Tuple[List[str], List[str], List[str]]:
        """Get keys with state give target language
        """
        new_keys, changed_keys, done_keys = [], [], []

        if not self._source_localisation.sorted_keys:
            return new_keys, changed_keys, done_keys

        items = self._translation_data.get(language) if self._translation_data else None
        for key in self._source_localisation.sorted_keys:
            if not items:
                # New key
                new_keys.append(key)
                continue
            if key not in items:
                # New key
                new_keys.append(key)
            else:
                value = self._source_localisation.get(key)
                if not value or not value.values:
                    continue
                # Only use the first language's value to check key state
                if value.values[0].value != items[key].original_value:
                    # Update
                    changed_keys.append(key)
                else:
                    # Done
                    done_keys.append(key)

        return new_keys, changed_keys, done_keys

    def get(self, key: str, language: str) -> TranslationItem | None:
        """Get a translation
        """
        if self._translation_data:
            language_values = self._translation_data.get(language)
            if language_values:
                return language_values.get(key)

    def add(self, key: str, value: str, language: str) -> None:
        """Add a translation
        """
        if not self._translation_data:
            self._translation_data = {}
        if language not in self._translation_data:
            self._translation_data[language] = {}
        # Get original value
        item = self._source_localisation.get(key)
        if not item or not item.values:
            raise ValueError("Source localisation not found")
        original_value = item.values[0].value
        # Add it
        self._translation_data[language][key] = TranslationItem(original_value, value, int(time()))

    def delete(self, key: str, language: str) -> None:
        """Delete a translation
        """
        if self._translation_data:
            language_values = self._translation_data.get(language)
            if language_values:
                del language_values[key]

    def save(self):
        """Save translation file
        """
        self._save_translation_data()

    def build(self, build_dir: str, name: str):
        """Build
        """
        if not self._translation_data:
            return
        # Ensure dir
        replace_dir = os.path.join(build_dir, "replace")
        if not os.path.isdir(replace_dir):
            os.makedirs(replace_dir)
        # Build each language
        for language, lang_values in self._translation_data.items():
            # Ensure dir
            lang_dir = os.path.join(replace_dir, language)
            if not os.path.isdir(lang_dir):
                os.makedirs(lang_dir)
            # Build data
            lang_items = {}
            if self._source_localisation.sorted_keys:
                for key in self._source_localisation.sorted_keys:
                    item = lang_values.get(key)
                    if item:
                        # Found translation, use the translated value
                        lang_items[key] = DoubleQuotedScalarString(item.translate_value)
                    else:
                        # Translation not found, try to use the original value or the first value
                        source_item = self._source_localisation.get(key)
                        if source_item and source_item.values:
                            for value in source_item.values:
                                if value.language == language:
                                    # Use this language
                                    lang_items[key] = DoubleQuotedScalarString(value.value)
                                    break
                            else:
                                # Use the first language
                                lang_items[key] = DoubleQuotedScalarString(source_item.values[0].value)
            lang_data = {"l_%s" % language: lang_items}
            # Write yaml file
            with open(os.path.join(lang_dir, "%s_l_%s.yml" % (name, language)), "w", encoding="utf-8-sig") as fd:
                yaml.dump(lang_data, fd)

    def _load_translation_data(self) -> None:
        """Load translation data
        """
        if not os.path.isfile(self._data_file):
            return

        data: Dict[str, Dict[str, TranslationItem]] = {}

        with open(self._data_file, "r", encoding="utf-8") as fd:
            for line in fd:
                line = line.strip()
                if line:
                    value = json.loads(line)
                    if value:
                        language, key, original_value, translate_value, update_time = \
                            value.get("l"), value.get("k"), value.get("v0"), value.get("v1"), value.get("t")
                        language = language.strip()
                        key = key.strip()
                        if not isinstance(update_time, int):
                            update_time = 0
                        if language and value:
                            # Add this item
                            if language not in data:
                                data[language] = {
                                    key: TranslationItem(original_value, translate_value, update_time)
                                }
                            else:
                                data[language][key] = TranslationItem(original_value, translate_value, update_time)

        self._translation_data = data

    def _save_translation_data(self):
        """Save translation data

            NOTE: Sort keys fit for git change tracing
        """
        with open(self._data_file, "w", encoding="utf-8") as fd:
            if self._translation_data:
                for language, items in sorted(self._translation_data.items(), key=lambda p: p[0]):
                    for key, item in sorted(items.items(), key=lambda p: p[0]):
                        if item.translate_value:
                            json_value = {
                                "l": language,
                                "k": key,
                                "v0": item.original_value,
                                "v1": item.translate_value,
                                "t": item.update_time,
                            }
                            print(json.dumps(json_value, sort_keys=True, ensure_ascii=False), file=fd)
