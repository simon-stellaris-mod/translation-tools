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
LocalisationItem = NamedTuple("LocalisationItem", [("key", str), ("values", List[LocalisationValue])])

AvailableFileSuffix = ["_l_%s.yml" % lang for lang in LanguageNames]
FileHeaderMapping = {"l_%s" % lang: lang for lang in LanguageNames}


class LocalisationData(object):
    """Localisation data
    """

    def __init__(self, source_paths: List[str]) -> None:
        """Create a new LocalisationData
        """
        self._source_paths = source_paths
        self._items: Dict[str, LocalisationItem] = {}
        self._sorted_keys: List[str] = []
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
        self._items = {}

        for source_path in self._source_paths:
            if os.path.isdir(source_path):
                self._read_directory(source_path)
            elif os.path.isfile(source_path):
                self._read_file(source_path)

        # Sort keys
        self._sorted_keys = sorted(self._items.keys())

    def _check_filename(self, filename: str) -> bool:
        """Check filename
        """
        for suffix in AvailableFileSuffix:
            if filename.endswith(suffix):
                return True
        return False

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
                if key not in self._items:
                    self._items[key] = LocalisationItem(key, [LocalisationValue(language, value)])
                else:
                    self._items[key].values.append(LocalisationValue(language, value))


TranslationItem = NamedTuple("TranslationItem", [("original_value", str), ("translate_value", str), ("update_time", int)])


class TranslationManager(object):
    """Translation manager
    """

    def __init__(self, source_paths: List[str], data_file: str) -> None:
        """Create a new TranslationManager
        """
        self._source_paths = source_paths
        self._data_file = data_file
        self._source_localisation = LocalisationData(source_paths)
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

    def build(self, name: str, output_path: str, build_none_translated_key: bool):
        """Build
        """
        if not self._translation_data:
            return
        # Ensure dir
        replace_dir = os.path.join(output_path, "replace")
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
                    elif build_none_translated_key:
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


if __name__ == "__main__":

    import sys

    # Command line tools
    from argparse import ArgumentParser

    def get_args():
        """Get args
        """
        parser = ArgumentParser(description="Stellaris translation cli")
        sub_parsers = parser.add_subparsers(dest="action")
        # Build
        build_parser = sub_parsers.add_parser("build", help="Build mod files")
        build_parser.add_argument("--name", dest="name", required=True, help="Name of this translation")
        build_parser.add_argument("--source-path", dest="source_paths", required=True, default=[], action="append",
                                  help="The source path, either a directory or a file. Usually [localisation] directory of a mod or a sub directory of a specific language. You MUST ONLY load file(s) for 1 language. You can specify multiple source paths")
        build_parser.add_argument("--data-file", dest="data_file", required=True, help="The file which stores the translation data")
        build_parser.add_argument("--output-path", dest="output_path", required=True,
                                  help="The build output directory path. Usually [localisation] of your mod")
        build_parser.add_argument("--build-none-translated-key", dest="build_none_translated_key", default=False,
                                  action="store_true", help="Write none-translated key when building")
        build_parser.set_defaults(handler=run_build)

        return parser.parse_args()

    def run_build(args):
        """Run build
        """
        # Source
        source_paths = []
        if not args.source_paths:
            raise ValueError("Require at least 1 source path")
        for source_path in args.source_paths:
            source_path = os.path.abspath(source_path)
            if not os.path.isdir(source_path) and not os.path.isfile(source_path):
                raise ValueError("Source path [%s] not exist" % source_path)
            source_paths.append(source_path)

        data_file = os.path.abspath(args.data_file)
        output_path = os.path.abspath(args.output_path)

        if not os.path.isdir(output_path):
            raise ValueError("Output dir [%s] not exist" % output_path)

        manager = TranslationManager(source_paths, data_file)
        manager.build(args.name, output_path, build_none_translated_key=args.build_none_translated_key)
        return 0

    def main():
        """Main entry
        """
        args = get_args()
        return args.handler(args)

    sys.exit(main())
