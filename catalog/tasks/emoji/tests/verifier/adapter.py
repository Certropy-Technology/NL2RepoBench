from __future__ import annotations

import inspect
import json
import os
import sys


CANDIDATE_SITE = os.environ.get(
    "NL2REPO_EMOJI_CANDIDATE_SITE", "/tmp/candidate-site"
)
if CANDIDATE_SITE not in sys.path:
    sys.path.insert(0, CANDIDATE_SITE)

import emoji
from emoji import tokenizer, unicode_codes


def error_name(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__
    return None


def parameter_contract(callable_):
    result = []
    for parameter in inspect.signature(callable_).parameters.values():
        default = (
            "required"
            if parameter.default is inspect.Parameter.empty
            else repr(parameter.default)
        )
        result.append([parameter.name, default])
    return result


def summarize_token(token):
    value = token.value
    if isinstance(value, tokenizer.EmojiMatch):
        return {
            "chars": token.chars,
            "kind": type(value).__name__,
            "emoji": value.emoji,
            "start": value.start,
            "end": value.end,
            "is_zwj": value.is_zwj(),
        }
    return {"chars": token.chars, "kind": "text", "value": value}


def package_identity():
    return {
        "version": emoji.__version__,
        "author": emoji.__author__,
        "license_marker": "New BSD License" in emoji.__license__,
        "languages": list(emoji.LANGUAGES),
        "status": dict(emoji.STATUS),
    }


def public_exports():
    return {
        "all": list(emoji.__all__),
        "callables": {
            name: callable(getattr(emoji, name))
            for name in (
                "emojize",
                "demojize",
                "analyze",
                "emoji_list",
                "distinct_emoji_list",
                "emoji_count",
                "replace_emoji",
                "is_emoji",
                "purely_emoji",
                "version",
            )
        },
        "data_type": type(emoji.EMOJI_DATA).__name__,
    }


def api_signatures():
    return {
        name: parameter_contract(getattr(emoji, name))
        for name in (
            "emojize",
            "demojize",
            "analyze",
            "emoji_list",
            "distinct_emoji_list",
            "emoji_count",
            "replace_emoji",
            "is_emoji",
            "purely_emoji",
            "version",
        )
    }


def english_conversion():
    text = "Python :thumbs_up: :red_heart: :does_not_exist:"
    rendered = emoji.emojize(text)
    return {
        "rendered": rendered,
        "round_trip": emoji.demojize(rendered),
        "adjacent": emoji.emojize(":snake::butterfly:"),
    }


def aliases_and_variants():
    return {
        "alias": emoji.emojize(":thumbsup:", language="alias"),
        "english_unknown": emoji.emojize(":thumbsup:"),
        "demojize_alias": emoji.demojize("👍", language="alias"),
        "heart_base": emoji.emojize(":red_heart:"),
        "heart_text": emoji.emojize(":red_heart:", variant="text_type"),
        "heart_emoji": emoji.emojize(":red_heart:", variant="emoji_type"),
    }


def multilingual_conversion():
    return {
        "spanish": emoji.emojize(":cohete:", language="es"),
        "spanish_back": emoji.demojize("🚀", language="es"),
        "french": emoji.emojize(":fusée:", language="fr"),
        "japanese": emoji.emojize(":ロケット:", language="ja"),
        "german_back": emoji.demojize("🐍", language="de"),
    }


def custom_delimiters():
    rendered = emoji.emojize("A {snake} B {butterfly}", delimiters=("{", "}"))
    return {
        "rendered": rendered,
        "demojized": emoji.demojize(rendered, delimiters=("<", ">")),
        "multi_character": emoji.emojize(
            "[[snake]]", delimiters=("[[", "]]"), language="en"
        ),
    }


def version_filter_emojize():
    calls = []

    def handler(value, data):
        calls.append(
            [value, data["E"], data["match_start"], data["match_end"]]
        )
        return "[new]"

    return {
        "below": emoji.emojize(":bowl_with_spoon:", version=4),
        "at": emoji.emojize(":bowl_with_spoon:", version=5),
        "string_handler": emoji.emojize(
            "x:bowl_with_spoon:y", version=4, handle_version="[unsupported]"
        ),
        "callable_handler": emoji.emojize(
            "x:bowl_with_spoon:y", version=4, handle_version=handler
        ),
        "calls": calls,
    }


def version_filter_demojize():
    calls = []

    def handler(value, data):
        calls.append(
            [value, data["E"], data["match_start"], data["match_end"]]
        )
        return "[new]"

    return {
        "below": emoji.demojize("A 🦖 B", version=3),
        "at": emoji.demojize("A 🦖 B", version=5),
        "string_handler": emoji.demojize(
            "A 🦖 B", version=3, handle_version="[unsupported]"
        ),
        "callable_handler": emoji.demojize(
            "A 🦖 B", version=3, handle_version=handler
        ),
        "calls": calls,
    }


def replace_behavior():
    calls = []

    def handler(value, data):
        calls.append(
            [value, data["en"], data["E"], data["match_start"], data["match_end"]]
        )
        return f"<{data['en'][1:-1]}>"

    source = "A 🐍 meets 🧠"
    return {
        "remove_all": emoji.replace_emoji(source),
        "constant": emoji.replace_emoji(source, "X"),
        "newer_than_3": emoji.replace_emoji(source, "N", version=3),
        "callable": emoji.replace_emoji(source, handler),
        "calls": calls,
    }


def list_and_count():
    source = "A😀😀B👨‍👩‍👧‍👦C"
    return {
        "list": emoji.emoji_list(source),
        "distinct_sorted": sorted(emoji.distinct_emoji_list(source)),
        "count": emoji.emoji_count(source),
        "unique_count": emoji.emoji_count(source, unique=True),
    }


def predicates():
    return {
        "is_emoji": [
            emoji.is_emoji("😀"),
            emoji.is_emoji("👨‍👩‍👧‍👦"),
            emoji.is_emoji("😀😀"),
            emoji.is_emoji("plain"),
        ],
        "purely": [
            emoji.purely_emoji("😀👍"),
            emoji.purely_emoji("❤️"),
            emoji.purely_emoji("😀 text"),
            emoji.purely_emoji(""),
        ],
    }


def version_lookup():
    return {
        "unicode": emoji.version("😁"),
        "name": emoji.version(":butterfly:"),
        "text_unicode": emoji.version("before 🧠 after 🐍"),
        "text_alias": emoji.version("use :thumbsup:",),
        "missing_error": error_name(emoji.version, "no symbol here"),
    }


def analyze_positions():
    return [summarize_token(item) for item in emoji.analyze("A😀B❤️C")]


def analyze_non_emoji():
    return [
        summarize_token(item)
        for item in emoji.analyze("x😀!", non_emoji=True, join_emoji=True)
    ]


def rgi_zwj():
    family = "👨‍👩‍👧‍👦"
    token = next(emoji.analyze(family))
    match = token.value
    split = match.split()
    return {
        "token": summarize_token(token),
        "split_kind": type(split).__name__,
        "parts": [
            [part.emoji, part.start, part.end, part.data is not None]
            for part in split.emojis
        ],
        "joined": split.join(),
        "demojized": emoji.demojize(family),
        "round_trip": emoji.emojize(emoji.demojize(family)),
    }


def non_rgi_zwj():
    value = "👨‍👩🏿‍👧🏻‍👦🏾"
    old = emoji.config.demojize_keep_zwj
    try:
        emoji.config.demojize_keep_zwj = True
        kept = emoji.demojize(value)
        emoji.config.demojize_keep_zwj = False
        removed = emoji.demojize(value)
    finally:
        emoji.config.demojize_keep_zwj = old
    analyzed_joined = [summarize_token(item) for item in emoji.analyze(value)]
    analyzed_split = [
        summarize_token(item) for item in emoji.analyze(value, join_emoji=False)
    ]
    return {
        "kept": kept,
        "removed": removed,
        "kept_round_trip": emoji.emojize(kept) == value,
        "joined": analyzed_joined,
        "split": analyzed_split,
    }


def skin_tone_and_flags():
    source = "👍🏽🇫🇷1️⃣"
    return {
        "list": emoji.emoji_list(source),
        "demojized": emoji.demojize(source),
        "round_trip": emoji.emojize(emoji.demojize(source)) == source,
        "versions": [
            emoji.version("👍🏽"),
            emoji.version("🇫🇷"),
            emoji.version("1️⃣"),
        ],
    }


def direct_lookup():
    return {
        "english": unicode_codes.get_emoji_by_name(":snake:", "en"),
        "alias": unicode_codes.get_emoji_by_name(":thumbsup:", "alias"),
        "unknown": unicode_codes.get_emoji_by_name(":missing:", "en"),
        "wrong_case": unicode_codes.get_emoji_by_name(":Snake:", "en"),
    }


def metadata():
    fields = {}
    for value in ("😀", "❤️", "🐍", "🧠", "👨‍👩‍👧‍👦"):
        data = emoji.EMOJI_DATA[value]
        fields[value] = {
            "en": data["en"],
            "E": data["E"],
            "status": data["status"],
            "variant": data.get("variant"),
            "aliases": data.get("alias", []),
        }
    return fields


def language_loading():
    emoji.config.load_language(["fr", "es", "ja"])
    return {
        "rocket": {
            key: emoji.EMOJI_DATA["🚀"][key] for key in ("en", "fr", "es", "ja")
        },
        "repeat": emoji.config.load_language("fr"),
        "unsupported_error": error_name(emoji.config.load_language, "xx"),
    }


def tokenize_behavior():
    source = "x❤️y👍🏽z"
    return {
        "keep": [summarize_token(item) for item in tokenizer.tokenize(source, True)],
        "remove": [
            summarize_token(item) for item in tokenizer.tokenize(source, False)
        ],
    }


def match_object():
    base = tokenizer.EmojiMatch("😀", 2, 3, emoji.EMOJI_DATA["😀"])
    plain = tokenizer.EmojiMatch("x", 4, 5, None)
    return {
        "repr": repr(base),
        "copy": {
            key: base.data_copy()[key]
            for key in ("en", "E", "status", "match_start", "match_end")
        },
        "plain_copy": plain.data_copy(),
        "base_split_identity": base.split() is base,
        "base_is_zwj": base.is_zwj(),
    }


def error_contracts():
    return {
        "variant": error_name(emoji.emojize, ":heart_suit:", variant="invalid"),
        "emojize_language": error_name(emoji.emojize, ":snake:", language="xx"),
        "demojize_language": error_name(emoji.demojize, "🐍", language="xx"),
        "load_language": error_name(unicode_codes.load_from_json, "xx"),
        "missing_metadata": error_name(lambda: emoji.EMOJI_DATA["not emoji"]),
    }


def empty_and_plain():
    return {
        "emojize_empty": emoji.emojize(""),
        "demojize_empty": emoji.demojize(""),
        "replace_plain": emoji.replace_emoji("plain text", "X"),
        "emoji_list_plain": emoji.emoji_list("plain text"),
        "analyze_plain": list(emoji.analyze("plain text")),
        "counts": [emoji.emoji_count(""), emoji.emoji_count("plain text")],
    }


OPERATIONS = {
    name: value
    for name, value in globals().copy().items()
    if callable(value) and name in {
        "package_identity",
        "public_exports",
        "api_signatures",
        "english_conversion",
        "aliases_and_variants",
        "multilingual_conversion",
        "custom_delimiters",
        "version_filter_emojize",
        "version_filter_demojize",
        "replace_behavior",
        "list_and_count",
        "predicates",
        "version_lookup",
        "analyze_positions",
        "analyze_non_emoji",
        "rgi_zwj",
        "non_rgi_zwj",
        "skin_tone_and_flags",
        "direct_lookup",
        "metadata",
        "language_loading",
        "tokenize_behavior",
        "match_object",
        "error_contracts",
        "empty_and_plain",
    }
}


def main():
    for line in sys.stdin:
        request = {}
        try:
            request = json.loads(line)
            request_id = request["id"]
            operation = request["operation"]
            if operation not in OPERATIONS:
                raise ValueError("unknown operation")
            response = {
                "id": request_id,
                "ok": True,
                "result": OPERATIONS[operation](),
            }
        except Exception as exc:
            response = {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": type(exc).__name__,
            }
        print(json.dumps(response, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
