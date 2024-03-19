# encoding=utf-8

""" Web server
    Author: lipixun
    Created Time : 2024-03-14 12:09:29

    File Name: server.py
    Description:

"""
from typing import Any, Dict

import os
import os.path

from datetime import datetime

from bottle import HTTPError, abort, get, post, request, response, run, static_file, template, TEMPLATE_PATH

from translation import TranslationManager
from utils import json, LanguageNames

gName: str | None = None
gTranslationManager: TranslationManager | None = None
gDefaultTargetLanguage: str | None = None
gBuildOutputPath: str | None = None
gBuildNoneTranslatedKey: bool = False

StaticRootPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
TemplatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views")
TEMPLATE_PATH.insert(0, TemplatePath)


def json_response(f):
    """Wrap as a json response
    """
    def wrapped_func(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            response.add_header("Content-Type", "application/json")
            return json.dumps({"ok": True, "data": result})
        except HTTPError:
            raise
        except Exception as error:
            response.add_header("Content-Type", "application/json")
            return json.dumps({"ok": False, "message": str(error)})
    return wrapped_func


@get("/")
def handle_index():
    """Bottle: Index page
    """
    assert gTranslationManager

    language = get_default_language(request.query.language)  # type: ignore

    render_args: Dict[str, Any] = {
        "language": language,
        "languages": LanguageNames
    }

    return template("index", **render_args)


@get("/_/keys")
@json_response
def handle_get_keys():
    """Bottle: Get keys
    """
    assert gTranslationManager

    # Get keys
    language = get_default_language(request.query.language)  # type: ignore
    new_keys, changed_keys, done_keys, skipped_keys = gTranslationManager.get_keys(language)

    # Filter keys
    query = request.query.query  # type: ignore
    if query:
        query = query.lower()
        # Filter keys by query
        new_keys = [k for k in new_keys if k.lower().find(query) >= 0]
        changed_keys = [k for k in changed_keys if k.lower().find(query) >= 0]
        done_keys = [k for k in done_keys if k.lower().find(query) >= 0]
        skipped_keys = [k for k in skipped_keys if k.lower().find(query) >= 0]

    return {
        "new_keys": new_keys,
        "changed_keys": changed_keys,
        "done_keys": done_keys,
        "skipped_keys": skipped_keys,
    }


@get("/_/translation")
@json_response
def handle_get_translation():
    """Bottle: Get translation
    """
    assert gTranslationManager

    key = request.query.key  # type: ignore
    language = request.query.language  # type: ignore

    if not language:
        language = get_default_language()
    if not key or language not in LanguageNames:
        return

    result = {}
    source_item = gTranslationManager.source_localisation.get(key)
    if source_item:
        result["source"] = {
            "key": source_item.key,
            "values": [
                {
                    "language": value.language,
                    "value": value.value,
                } for value in source_item.values
            ]
        }

    translation_item = gTranslationManager.get(key, language)
    if translation_item:
        result["translation"] = {
            "value": translation_item.translate_value,
            "skipped": translation_item.skipped,
            "update_time": datetime.fromtimestamp(translation_item.update_time).strftime("%Y-%m-%d %H:%M:%S") if translation_item.update_time else "Never",
        }

    return result


@post("/_/translation")
@json_response
def handle_submit_translation():
    """Bottle: Submit translation
    """
    assert gTranslationManager

    if not request.json:
        abort(400, "Require json payload")
    key = request.json.get("key")  # type: ignore
    language = request.json.get("language")  # type: ignore
    value = request.json.get("value")  # type: ignore
    skipped = request.json.get("skipped")  # type: ignore
    if not key:
        abort(400, "Require key")
    if not isinstance(key, str):
        abort(400, "Key must be string")
    if not language:
        language = get_default_language()
    if language not in LanguageNames:
        abort(400, "Invalid language")
    if value is not None and not isinstance(value, str):
        abort(400, "Value must be null or string")
    if not isinstance(skipped, bool):
        skipped = skipped.lower() == "true" if skipped else False
    # Add or delete the translation
    if value or skipped:
        gTranslationManager.add(key, language, value, skipped)
    else:
        gTranslationManager.delete(key, language)


@post("/_/save")
@json_response
def handle_save():
    """Bottle: save
    """
    assert gTranslationManager

    gTranslationManager.save()


@post("/_/save_and_build")
@json_response
def handle_save_and_build():
    """Bottle: Save and build
    """
    assert gTranslationManager
    assert gBuildOutputPath
    assert gName

    gTranslationManager.save()
    gTranslationManager.build(gName, gBuildOutputPath, gBuildNoneTranslatedKey)


@get("/<path:path>")
def handle_static_file(path):
    """Bottle: Get static file
    """
    return static_file(path, root=StaticRootPath)


def get_default_language(language: str | None = None):
    """Get default language
    """
    if language in LanguageNames:
        return language
    return gDefaultTargetLanguage or "simp_chinese"  # Hard code chinese as fallback language


if __name__ == "__main__":

    from argparse import ArgumentParser

    def get_args():
        """Get args
        """
        parser = ArgumentParser(description="Stellaris translation server")
        parser.add_argument("--name", dest="name", required=True, help="Name of this translation. This name will be used in building progress.")
        parser.add_argument("--source-path", dest="source_paths", required=True, default=[], action="append",
                            help="The source path, either a directory or a file. Usually [localisation] directory of a mod or a sub directory of a specific language. You MUST ONLY load file(s) for 1 language. You can specify multiple source paths")
        parser.add_argument("--data-file", dest="data_file", required=True, help="The file which stores the translation data")
        parser.add_argument("--default-target-language", dest="default_target_language",
                            default="simp_chinese", choices=LanguageNames, help="Default target language")
        parser.add_argument("--output-path", dest="output_path", required=True,
                            help="The build output directory path. Usually [localisation] of your mod")
        parser.add_argument("--build-none-translated-key", dest="build_none_translated_key", default=False,
                            action="store_true", help="Write none-translated key when building")
        parser.add_argument("--run-host", dest="run_host", default="0.0.0.0", help="Web server host, 0.0.0.0 by default")
        parser.add_argument("--run-port", dest="run_port", default=8080, type=int, help="Web server port, 8080 by default")
        return parser.parse_args()

    def main() -> None:
        """The main entry
        """
        global gName
        global gTranslationManager
        global gDefaultTargetLanguage
        global gBuildOutputPath
        global gBuildNoneTranslatedKey

        args = get_args()

        gName = args.name
        gDefaultTargetLanguage = args.default_target_language
        gBuildNoneTranslatedKey = args.build_none_translated_key

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

        if not os.path.isdir(os.path.dirname(data_file)):
            raise ValueError("Parent directory of data file [%s] not exist" % data_file)
        if not os.path.isdir(output_path):
            raise ValueError("Output directory [%s] not exist" % output_path)

        gBuildOutputPath = output_path
        gTranslationManager = TranslationManager(source_paths, data_file)

        run(host=args.run_host, port=args.run_port)

    main()
