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
    return render_index(
        target_language=request.query.target_language,  # type: ignore
    )


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
    value = request.json.get("value")  # type: ignore
    language = request.json.get("language")  # type: ignore
    if not key:
        abort(400, "Require key")
    if not isinstance(key, str):
        abort(400, "Key must be string")
    if value is not None and not isinstance(value, str):
        abort(400, "Value must be null or string")
    if not language:
        language = get_default_language()
    if language not in LanguageNames:
        abort(400, "Invalid language")
    # Add or delete the translation
    if value:
        gTranslationManager.add(key, value, language)
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
    gTranslationManager.build(gBuildOutputPath, gName)


@get("/<path:path>")
def handle_static_file(path):
    """Bottle: Get static file
    """
    return static_file(path, root=StaticRootPath)


def render_index(target_language: str | None = None):
    """Render index
    """
    assert gTranslationManager

    render_args: Dict[str, Any] = {
        "languages": LanguageNames
    }

    # Target language
    if not target_language:
        target_language = gDefaultTargetLanguage
    if not target_language or (target_language and target_language not in LanguageNames):
        target_language = get_default_language()
    render_args["target_language"] = target_language

    # Keys
    new_keys, changed_keys, done_keys = gTranslationManager.get_keys(target_language)
    render_args["new_keys"] = new_keys
    render_args["changed_keys"] = changed_keys
    render_args["done_keys"] = done_keys

    return template("index", **render_args)


def get_default_language():
    """Get default language
    """
    return gDefaultTargetLanguage or "simp_chinese"  # Hard code chinese as fallback language


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--name", dest="name", required=True, help="Name of this translation. This name will be used in building progress.")
    parser.add_argument("--source-dir", dest="source_dir", required=True,
                        help="The source directory. Usually [localisation] directory of a mod or a sub directory of a specific language. You MUST ONLY load files for 1 language.")
    parser.add_argument("--data-file", dest="data_file", required=True, help="The file which stores the translation data")
    parser.add_argument("--default-target-language", dest="default_target_language",
                        default="simp_chinese", choices=LanguageNames, help="Default target language")
    parser.add_argument("--build-dir", dest="build_dir", required=True, help="The build target directory. Usually [localisation] of your mod")
    parser.add_argument("--run-host", dest="run_host", default="0.0.0.0", help="Web server host, 0.0.0.0 by default")
    parser.add_argument("--run-port", dest="run_port", default=8080, type=int, help="Web server port, 8080 by default")

    def main() -> None:
        """The main entry
        """
        global gName
        global gTranslationManager
        global gDefaultTargetLanguage
        global gBuildOutputPath

        args = parser.parse_args()

        gName = args.name
        gDefaultTargetLanguage = args.default_target_language

        source_dir = os.path.abspath(args.source_dir)
        data_file = os.path.abspath(args.data_file)
        build_dir = os.path.abspath(args.build_dir)

        if not os.path.isdir(source_dir):
            raise ValueError("Source dir [%s] not exist" % source_dir)
        if not os.path.isdir(os.path.dirname(data_file)):
            raise ValueError("Parent directory of data file [%s] not exist" % data_file)
        if not os.path.isdir(os.path.dirname(build_dir)):
            raise ValueError("Build dir [%s] not exist" % build_dir)

        gBuildOutputPath = build_dir
        gTranslationManager = TranslationManager(source_dir, data_file)

        run(host=args.run_host, port=args.run_port)

    main()
