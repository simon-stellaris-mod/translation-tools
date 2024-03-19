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
from collections import OrderedDict

from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from localization import LocalizationManager
from utils import LanguageNames, json, yaml


TranslationValue = NamedTuple("TranslationValue", [
    ("original_value", str),
    ("translate_value", str),
    ("skipped", bool),
    ("update_time", int),
])


class TranslationManager(object):
    """Translation manager
    """

    def __init__(self, source_localization: LocalizationManager) -> None:
        """Create a new TranslationManager
        """
        self._source_localization = source_localization
        self._translation_data: Dict[str, Dict[str, TranslationValue]] = {}   # language to key to item

    @property
    def source_localization(self):
        """Get source localization manager
        """
        return self._source_localization

    def get_translation_keys(self, language: str) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Get translation keys
        Returns:
            (news keys, changed keys, done keys, skipped keys)
        """
        new_keys, changed_keys, done_keys, skipped_keys = [], [], [], []

        if not self._source_localization.sorted_keys:
            return new_keys, changed_keys, done_keys, skipped_keys

        items = self._translation_data.get(language) if self._translation_data else None
        for key in self._source_localization.sorted_keys:
            if not items:
                # New key
                new_keys.append(key)
                continue
            if key not in items:
                # New key
                new_keys.append(key)
            else:
                value = self._source_localization.get(key)
                if not value or not value.values:
                    continue
                # Only use the first language's value to check key state
                if value.values[0].value != items[key].original_value:
                    # Update
                    changed_keys.append(key)
                elif items[key].skipped:
                    # Skipped
                    skipped_keys.append(key)
                else:
                    # Done
                    done_keys.append(key)

        return new_keys, changed_keys, done_keys, skipped_keys

    def get(self, key: str, language: str) -> TranslationValue | None:
        """Get a translation
        """
        if self._translation_data:
            language_values = self._translation_data.get(language)
            if language_values:
                return language_values.get(key)

    def add(self, key: str, language: str, value: str, skipped: bool) -> None:
        """Add a translation
        """
        if not self._translation_data:
            self._translation_data = {}
        if language not in self._translation_data:
            self._translation_data[language] = {}
        # Get original value
        item = self._source_localization.get(key)
        if not item or not item.values:
            raise ValueError("Source localisation not found")
        original_value = item.values[0].value
        # Add it
        self._translation_data[language][key] = TranslationValue(original_value, value, skipped, int(time()))

    def delete(self, key: str, language: str) -> None:
        """Delete a translation
        """
        if self._translation_data:
            language_values = self._translation_data.get(language)
            if language_values and key in language_values:
                del language_values[key]

    def load(self, filepath):
        """Load translation file
        """
        with open(filepath, "r", encoding="utf-8") as fd:
            for line in fd:
                line = line.strip()
                if line:
                    value = json.loads(line)
                    if value:
                        language, key, original_value, translate_value, skipped, update_time = \
                            value.get("l"), value.get("k"), value.get("v0"), \
                            value.get("v1"), value.get("s", False), value.get("t")
                        language = language.strip()
                        key = key.strip()
                        if not language or not key:
                            continue
                        skipped = False if skipped is False else True
                        if not isinstance(update_time, int):
                            update_time = 0
                        # Add this item
                        item = TranslationValue(original_value, translate_value, skipped, update_time)
                        if language not in self._translation_data:
                            self._translation_data[language] = {key:  item}
                        else:
                            self._translation_data[language][key] = item

    def save(self, filepath):
        """Save translation file
        """
        with open(filepath, "w", encoding="utf-8") as fd:
            if self._translation_data:
                for language, items in sorted(self._translation_data.items(), key=lambda p: p[0]):
                    for key, item in sorted(items.items(), key=lambda p: p[0]):
                        if item.translate_value or item.skipped:
                            json_value = {
                                "l": language,
                                "k": key,
                                "v0": item.original_value,
                                "v1": item.translate_value,
                                "t": item.update_time,
                            }
                            if item.skipped:
                                json_value["s"] = True
                            print(json.dumps(json_value, sort_keys=True, ensure_ascii=False), file=fd)

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
        for language, translation_values in self._translation_data.items():
            # Ensure dir
            lang_dir = os.path.join(replace_dir, language)
            if not os.path.isdir(lang_dir):
                os.makedirs(lang_dir)
            # Build data
            build_values = {}
            for key in self._source_localization.sorted_keys:
                translation_value = translation_values.get(key)
                if translation_value and not translation_value.skipped:
                    # Found translation, use the translated value
                    build_values[key] = DoubleQuotedScalarString(translation_value.translate_value)
                elif build_none_translated_key:
                    # Translation not found, try to use the original value or the first value
                    localization_item = self._source_localization.get(key)
                    if localization_item and localization_item.values:
                        for value in localization_item.values:
                            if value.language == language:
                                # Use this language
                                build_values[key] = DoubleQuotedScalarString(value.value)
                                break
                        else:
                            # Use the first language
                            build_values[key] = DoubleQuotedScalarString(localization_item.values[0].value)
            build_data = {"l_%s" % language: build_values}
            # Write yaml file
            with open(os.path.join(lang_dir, "%s_l_%s.yml" % (name, language)), "w", encoding="utf-8-sig") as fd:
                yaml.dump(build_data, fd)


if __name__ == "__main__":

    import re
    import sys
    import itertools

    from argparse import ArgumentParser

    AliasValueRegex = re.compile(r"^ *\$[^\$]*\$ *$", re.UNICODE)

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
        build_parser.add_argument("--source-language", dest="source_language", default=None, choices=LanguageNames,
                                  help="Source language. Only preserve the value of specified language. Will preserve all languages if not specified. (I highly recommend to set this flag in order to avoid unexpected language misusage)")
        build_parser.add_argument("--data-file", dest="data_file", required=True, help="The file which stores the translation data")
        build_parser.add_argument("--output-path", dest="output_path", required=True,
                                  help="The build output directory path. Usually [localisation] of your mod")
        build_parser.add_argument("--build-none-translated-key", dest="build_none_translated_key", default=False,
                                  action="store_true", help="Write none-translated key when building")
        build_parser.set_defaults(handler=run_build)
        # Auto skip
        auto_skip_parser = sub_parsers.add_parser(
            "auto-skip", help="Auto skip alias keys (the value of which is just only a reference to another key)")
        auto_skip_parser.add_argument("--source-path", dest="source_paths", required=True, default=[], action="append",
                                      help="The source path, either a directory or a file. Usually [localisation] directory of a mod or a sub directory of a specific language. You MUST ONLY load file(s) for 1 language. You can specify multiple source paths")
        auto_skip_parser.add_argument("--source-language", dest="source_language", default=None, choices=LanguageNames,
                                      help="Source language. Only preserve the value of specified language. Will preserve all languages if not specified. (I highly recommend to set this flag in order to avoid unexpected language misusage)")
        auto_skip_parser.add_argument("--data-file", dest="data_file", required=True, help="The file which stores the translation data")
        auto_skip_parser.add_argument("--target-language", dest="target_language",
                                      default="simp_chinese", choices=LanguageNames, help="Target language, simp_chinese by default.")
        auto_skip_parser.set_defaults(handler=run_auto_skip)

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
        if not os.path.isdir(os.path.dirname(data_file)):
            raise ValueError("Parent directory of data file [%s] not exist" % data_file)

        output_path = os.path.abspath(args.output_path)
        if not os.path.isdir(output_path):
            raise ValueError("Output dir [%s] not exist" % output_path)

        print("[+] Run build")
        source_localization = LocalizationManager([args.source_language] if args.source_language else None)
        for source_path in source_paths:
            source_localization.load(source_path)
        translation_manager = TranslationManager(source_localization)
        translation_manager.load(data_file)
        translation_manager.build(args.name, output_path, build_none_translated_key=args.build_none_translated_key)
        return 0

    def run_auto_skip(args):
        """Run auto skip
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
        if not os.path.isdir(os.path.dirname(data_file)):
            raise ValueError("Parent directory of data file [%s] not exist" % data_file)

        print("[+] Run auto skip")
        source_localization = LocalizationManager([args.source_language] if args.source_language else None)
        for source_path in source_paths:
            source_localization.load(source_path)
        translation_manager = TranslationManager(source_localization)
        translation_manager.load(data_file)

        new_keys, changed_keys, done_keys, skipped_keys = translation_manager.get_translation_keys(args.target_language)
        # Print states
        print("[+] Before generating skip keys: new [%d] changed [%d] done [%d] skipped [%d]" % (
            len(new_keys), len(changed_keys), len(done_keys), len(skipped_keys)))

        auto_skip_count = 0

        for key in itertools.chain(new_keys, changed_keys):
            localization_item = source_localization.get(key)
            if not localization_item or not localization_item.values or not localization_item.values[0].value:
                continue
            if AliasValueRegex.match(localization_item.values[0].value):
                auto_skip_count += 1
                translation_manager.add(key, args.target_language, "", True)

        print("[+] Found %d new skipped keys" % auto_skip_count)

        # Save and print new stats
        translation_manager.save(data_file)
        new_keys, changed_keys, done_keys, skipped_keys = translation_manager.get_translation_keys(args.target_language)
        print("[+] After generating skip keys: new [%d] changed [%d] done [%d] skipped [%d]" % (
            len(new_keys), len(changed_keys), len(done_keys), len(skipped_keys)))

        return 0

    def main():
        """Main entry
        """
        args = get_args()
        return args.handler(args)

    sys.exit(main())
