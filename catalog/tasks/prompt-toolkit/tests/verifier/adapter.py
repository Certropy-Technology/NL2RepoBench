"""Private child adapter for the prompt_toolkit headless contract.

The verifier supplies only a fixed operation name. Candidate code is imported
solely in this unprivileged process, and every observation is JSON-safe.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys


def _completion(value):
    return {
        "display_meta_text": value.display_meta_text,
        "display_text": value.display_text,
        "selected_style": value.selected_style,
        "start_position": value.start_position,
        "style": value.style,
        "text": value.text,
    }


def _document() -> dict[str, object]:
    from prompt_toolkit.document import Document

    document = Document("alpha\nbeta gamma\n", cursor_position=8)
    return {
        "char_before_cursor": document.char_before_cursor,
        "current_char": document.current_char,
        "current_line": document.current_line,
        "current_line_after_cursor": document.current_line_after_cursor,
        "current_line_before_cursor": document.current_line_before_cursor,
        "cursor_position": document.cursor_position,
        "cursor_position_col": document.cursor_position_col,
        "cursor_position_row": document.cursor_position_row,
        "find_a": document.find("a", include_current_position=True),
        "find_backwards_a": document.find_backwards("a"),
        "line_count": document.line_count,
        "lines": list(document.lines),
        "text_after_cursor": document.text_after_cursor,
        "text_before_cursor": document.text_before_cursor,
        "translate_index": list(document.translate_index_to_position(11)),
        "translate_row_col": document.translate_row_col_to_index(1, 99),
        "word_before_cursor": document.get_word_before_cursor(),
    }


def _buffer_editing() -> dict[str, object]:
    from prompt_toolkit.buffer import Buffer, EditReadOnlyBuffer
    from prompt_toolkit.completion import Completion
    from prompt_toolkit.document import Document

    buffer = Buffer()
    buffer.insert_text("some_text")
    buffer.cursor_left(3)
    buffer.cursor_right()
    buffer.insert_text("A")
    inserted = {"cursor": buffer.cursor_position, "text": buffer.text}
    deleted = buffer.delete_before_cursor(2)
    after_delete = {"cursor": buffer.cursor_position, "text": buffer.text}

    undo = Buffer()
    undo.insert_text("abcd")
    undo.save_to_undo_stack()
    undo.cursor_left(2)
    undo.insert_text("XY")
    before_undo = {"cursor": undo.cursor_position, "text": undo.text}
    undo.undo()
    after_undo = {"cursor": undo.cursor_position, "text": undo.text}
    undo.redo()
    after_redo = {"cursor": undo.cursor_position, "text": undo.text}

    completion = Buffer(document=Document("hello wo", cursor_position=8))
    completion.apply_completion(Completion("world", start_position=-2))

    readonly = Buffer(read_only=True)
    try:
        readonly.insert_text("blocked")
    except EditReadOnlyBuffer as error:
        readonly_error = type(error).__name__
    else:
        readonly_error = None

    return {
        "after_delete": after_delete,
        "after_redo": after_redo,
        "after_undo": after_undo,
        "applied_completion": {
            "cursor": completion.cursor_position,
            "text": completion.text,
        },
        "before_undo": before_undo,
        "deleted": deleted,
        "inserted": inserted,
        "readonly_error": readonly_error,
    }


def _completion_data() -> dict[str, object]:
    from prompt_toolkit.completion import Completion

    completion = Completion(
        "archive",
        start_position=-2,
        display=[("class:name", "Archive")],
        display_meta="cached",
        style="class:item",
        selected_style="class:selected",
    )
    return {
        "completion": _completion(completion),
        "position_minus_one": _completion(completion.new_completion_from_position(-1)),
    }


def _word_completion() -> dict[str, object]:
    from prompt_toolkit.completion import CompleteEvent, WordCompleter
    from prompt_toolkit.document import Document

    words = ["alpha", "Alpine", "beta", "alphabet"]
    exact = WordCompleter(words)
    insensitive = WordCompleter(words, ignore_case=True)
    sentence = WordCompleter(["show version", "show value", "exit"], sentence=True)
    event = CompleteEvent(completion_requested=True)
    return {
        "case_sensitive_a": [
            value.text for value in exact.get_completions(Document("a"), event)
        ],
        "case_sensitive_A": [
            value.text for value in exact.get_completions(Document("A"), event)
        ],
        "case_insensitive_A": [
            value.text for value in insensitive.get_completions(Document("A"), event)
        ],
        "sentence": [
            value.text
            for value in sentence.get_completions(Document("show v"), event)
        ],
    }


def _nested_completion() -> dict[str, object]:
    from prompt_toolkit.completion import (
        CompleteEvent,
        NestedCompleter,
        WordCompleter,
        merge_completers,
    )
    from prompt_toolkit.document import Document

    event = CompleteEvent(completion_requested=True)
    nested = NestedCompleter.from_nested_dict(
        {
            "show": {"version": None, "value": None},
            "exit": None,
        }
    )
    deduplicated = merge_completers(
        [WordCompleter(["alpha", "beta"]), WordCompleter(["beta", "gamma"])],
        deduplicate=True,
    )
    return {
        "nested_root": [
            value.text for value in nested.get_completions(Document(""), event)
        ],
        "nested_child": [
            value.text
            for value in nested.get_completions(Document("show v"), event)
        ],
        "deduplicated": [
            value.text
            for value in deduplicated.get_completions(Document(""), event)
        ],
    }


async def _history_items(history) -> list[str]:
    return [item async for item in history.load()]


def _history_clipboard() -> dict[str, object]:
    from prompt_toolkit.clipboard import ClipboardData, InMemoryClipboard
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.selection import SelectionState, SelectionType

    history = InMemoryHistory(["first", "second"])
    history.append_string("third")

    clipboard = InMemoryClipboard(
        ClipboardData("first", SelectionType.CHARACTERS), max_size=3
    )
    clipboard.set_data(ClipboardData("line", SelectionType.LINES))
    clipboard.set_text("plain")
    current = clipboard.get_data()
    clipboard.rotate()
    rotated = clipboard.get_data()

    selection = SelectionState(7, SelectionType.BLOCK)
    selection.enter_shift_mode()
    return {
        "clipboard_current": {"text": current.text, "type": current.type.value},
        "clipboard_rotated": {"text": rotated.text, "type": rotated.type.value},
        "history_loaded": asyncio.run(_history_items(history)),
        "history_strings": history.get_strings(),
        "selection": {
            "original_cursor_position": selection.original_cursor_position,
            "shift_mode": selection.shift_mode,
            "type": selection.type.value,
        },
    }


def _validation() -> dict[str, object]:
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.validation import Validator

    validator = Validator.from_callable(
        lambda text: text == "accepted",
        error_message="expected accepted",
        move_cursor_to_end=True,
    )
    invalid = Buffer(document=Document("no", cursor_position=0), validator=validator)
    valid = Buffer(document=Document("accepted"), validator=validator)
    invalid_result = invalid.validate(set_cursor=True)
    valid_result = valid.validate(set_cursor=True)
    return {
        "invalid": {
            "cursor": invalid.cursor_position,
            "error_cursor": invalid.validation_error.cursor_position
            if invalid.validation_error
            else None,
            "error_message": invalid.validation_error.message
            if invalid.validation_error
            else None,
            "result": invalid_result,
        },
        "valid": {
            "error": valid.validation_error is None,
            "result": valid_result,
        },
    }


def _key_bindings() -> dict[str, object]:
    from prompt_toolkit.application import Application
    from prompt_toolkit.application.current import set_app
    from prompt_toolkit.input.defaults import create_pipe_input
    from prompt_toolkit.key_binding.key_bindings import KeyBindings
    from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.layout import Layout, Window
    from prompt_toolkit.output import DummyOutput

    calls: list[str] = []
    with create_pipe_input() as pipe_input:
        app = Application(
            layout=Layout(Window()),
            output=DummyOutput(),
            input=pipe_input,
        )

        def create_background_task(coroutine, **_kwargs):
            coroutine.close()
            return None

        app.create_background_task = create_background_task
        app.invalidate = lambda: None
        with set_app(app):
            bindings = KeyBindings()

            @bindings.add(Keys.ControlX)
            def control_x(_event):
                calls.append("control-x")

            @bindings.add(Keys.ControlX, Keys.ControlC)
            def control_x_control_c(_event):
                calls.append("control-x-control-c")

            @bindings.add(Keys.ControlD)
            def control_d(_event):
                calls.append("control-d")

            @bindings.add(Keys.ControlSquareClose, Keys.Any)
            def any_after_square_close(event):
                calls.append("any:" + event.key_sequence[-1].data)

            processor = KeyProcessor(bindings)
            processor.feed(KeyPress(Keys.ControlX, "\x18"))
            processor.process_keys()
            pending_after_prefix = [value.key.value for value in processor.key_buffer]
            processor.feed(KeyPress(Keys.ControlD, "\x04"))
            processor.process_keys()
            processor.feed(KeyPress(Keys.ControlX, "\x18"))
            processor.feed(KeyPress(Keys.ControlC, "\x03"))
            processor.process_keys()
            processor.feed(KeyPress(Keys.ControlSquareClose, "\x1d"))
            processor.feed(KeyPress("z", "z"))
            processor.process_keys()
            return {
                "calls": calls,
                "pending_after_prefix": pending_after_prefix,
                "specific_match_count": len(
                    bindings.get_bindings_for_keys((Keys.ControlX, Keys.ControlC))
                ),
                "prefix_match_count": len(
                    bindings.get_bindings_starting_with_keys((Keys.ControlX,))
                ),
            }


def _api_surface() -> dict[str, object]:
    import prompt_toolkit
    from prompt_toolkit.completion import Completion, NestedCompleter, WordCompleter
    from prompt_toolkit.document import Document
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding.key_bindings import KeyBindings
    from prompt_toolkit.keys import Keys


    root_exports = [
        "Application",
        "prompt",
        "choice",
        "PromptSession",
        "print_formatted_text",
        "HTML",
        "ANSI",
        "__version__",
        "VERSION",
    ]
    return {
        "all": list(prompt_toolkit.__all__),
        "root_exports": {
            name: hasattr(prompt_toolkit, name) for name in root_exports
        },
        "types": {
            "Completion": Completion.__name__,
            "Document": Document.__name__,
            "InMemoryHistory": InMemoryHistory.__name__,
            "KeyBindings": KeyBindings.__name__,
            "Keys": Keys.__name__,
            "NestedCompleter": NestedCompleter.__name__,
            "WordCompleter": WordCompleter.__name__,
        },
        "version": prompt_toolkit.__version__,
        "version_tuple": list(prompt_toolkit.VERSION),
    }


OPERATIONS = {
    "api_surface": _api_surface,
    "buffer_editing": _buffer_editing,
    "completion_data": _completion_data,
    "document": _document,
    "history_clipboard": _history_clipboard,
    "key_bindings": _key_bindings,
    "nested_completion": _nested_completion,
    "validation": _validation,
    "word_completion": _word_completion,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    sys.path.insert(
        0,
        os.environ.get(
            "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
        ),
    )
    sys.path.insert(0, args.candidate_site)
    request = json.loads(args.request)
    if set(request) != {"operation", "schema_version"}:
        raise ValueError("invalid request fields")
    if request["schema_version"] != "prompt-toolkit-headless-v1":
        raise ValueError("unsupported fixture schema")
    operation = request["operation"]
    if operation not in OPERATIONS:
        raise ValueError("unsupported operation")
    print(
        json.dumps(
            {"ok": True, "value": OPERATIONS[operation]()},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


try:
    main()
except BaseException as error:
    print(
        json.dumps(
            {
                "exception_message": str(error),
                "exception_type": type(error).__module__ + "." + type(error).__qualname__,
                "ok": False,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
