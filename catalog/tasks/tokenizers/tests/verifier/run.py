"""Private deterministic tokenizers contract executed outside the candidate tree."""

from __future__ import annotations

import json
from typing import Any

from nl2repobench.verification.candidate_client import execute_script, metadata_requires


def _case(leaf_id: str, source: str, expected: Any) -> dict[str, str]:
    observed = execute_script(source, timeout_sec=25.0)
    if observed.ok and observed.value == expected:
        return {"id": leaf_id, "status": "passed"}
    detail = observed.exception_message if not observed.ok else repr(observed.value)
    return {"id": leaf_id, "status": "failed", "message": f"expected {expected!r}; got {detail}"}


def _metadata_case() -> dict[str, str]:
    observed = metadata_requires("tokenizers")
    expected = ["huggingface_hub>=0.16.4,<2.0"]
    if observed.ok and observed.value == expected:
        return {"id": "metadata-dependencies", "status": "passed"}
    detail = observed.exception_message if not observed.ok else repr(observed.value)
    return {"id": "metadata-dependencies", "status": "failed", "message": detail}


def main() -> None:
    cases: list[dict[str, str]] = [_metadata_case()]
    cases.extend(
        [
            _case(
                "packaging-surface",
                "import tokenizers\nresult = [tokenizers.__version__, all(hasattr(tokenizers, n) for n in ('Tokenizer', 'Encoding', 'AddedToken', 'models', 'normalizers', 'pre_tokenizers', 'processors', 'trainers', 'decoders'))]",
                ["0.23.2-dev.0", True],
            ),
            _case(
                "module-reexports",
                "import tokenizers\nfrom tokenizers.models import BPE, WordLevel, WordPiece, Unigram\nfrom tokenizers.implementations import CharBPETokenizer, ByteLevelBPETokenizer, SentencePieceBPETokenizer, SentencePieceUnigramTokenizer, BertWordPieceTokenizer\nresult = all(callable(x) for x in (BPE, WordLevel, WordPiece, Unigram, CharBPETokenizer, ByteLevelBPETokenizer, SentencePieceBPETokenizer, SentencePieceUnigramTokenizer, BertWordPieceTokenizer))",
                True,
            ),
            _case(
                "wordlevel-encoding",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, 'world': 2, '!': 3}, unk_token='[UNK]'))\nt.pre_tokenizer = Whitespace()\ne = t.encode('hello world!')\nresult = {'ids': e.ids, 'tokens': e.tokens}",
                {"ids": [1, 2, 3], "tokens": ["hello", "world", "!"]},
            ),
            _case(
                "encoding-fields",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1, 'b': 2}, unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); e = t.encode('a b')\nresult = {'type_ids': e.type_ids, 'attention_mask': e.attention_mask, 'special_tokens_mask': e.special_tokens_mask, 'offsets': e.offsets, 'word_ids': e.word_ids, 'sequence_ids': e.sequence_ids}",
                {"type_ids": [0, 0], "attention_mask": [1, 1], "special_tokens_mask": [0, 0], "offsets": [[0, 1], [2, 3]], "word_ids": [0, 1], "sequence_ids": [0, 0]},
            ),
            _case(
                "unknown-token",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'known': 1}, unk_token='[UNK]')); result = t.encode('missing').tokens",
                ["[UNK]"],
            ),
            _case(
                "pretokenized",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, 'world': 2}, unk_token='[UNK]')); result = t.encode(['hello', 'world'], is_pretokenized=True).tokens",
                ["hello", "world"],
            ),
            _case(
                "pair-processing",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.processors import TemplateProcessing\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, 'world': 2, '[SEP]': 3}, unk_token='[UNK]')); t.post_processor = TemplateProcessing(single=['$A'], pair=['$A', '[SEP]', '$B'], special_tokens=[('[SEP]', 3)]); a = t.encode('hello', 'world'); result = {'ids': a.ids, 'type_ids': a.type_ids, 'special': a.special_tokens_mask}",
                {"ids": [1, 3, 2], "type_ids": [0, 0, 0], "special": [0, 1, 0]},
            ),
            _case(
                "batch-order",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1, 'b': 2}, unk_token='[UNK]')); result = [e.tokens for e in t.encode_batch(['b', 'a'])]",
                [["b"], ["a"]],
            ),
            _case(
                "decode",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, 'world': 2}, unk_token='[UNK]')); result = t.decode([1, 2])",
                "hello world",
            ),
            _case(
                "padding",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1, 'b': 2}, unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); t.enable_padding(pad_id=0, pad_token='[PAD]'); e = t.encode_batch(['a', 'a b']); result = [{'ids': x.ids, 'tokens': x.tokens, 'attention_mask': x.attention_mask} for x in e]",
                [{"ids": [1, 0], "tokens": ["a", "[PAD]"], "attention_mask": [1, 0]}, {"ids": [1, 2], "tokens": ["a", "b"], "attention_mask": [1, 1]}],
            ),
            _case(
                "padding-multiple",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1}, unk_token='[UNK]')); t.enable_padding(pad_to_multiple_of=4, pad_id=0, pad_token='[PAD]'); e = t.encode_batch(['a']); result = {'length': len(e[0].ids), 'padding': t.padding['pad_to_multiple_of']} ",
                {"length": 4, "padding": 4},
            ),
            _case(
                "truncation",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1, 'b': 2, 'c': 3}, unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); t.enable_truncation(2); e = t.encode('a b c'); result = {'ids': e.ids, 'max_length': t.truncation['max_length']} ",
                {"ids": [1, 2], "max_length": 2},
            ),
            _case(
                "serialization",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1}, unk_token='[UNK]')); s = t.to_str(); u = Tokenizer.from_str(s); result = {'same': u.to_str() == s, 'tokens': u.encode('hello').tokens}",
                {"same": True, "tokens": ["hello"]},
            ),
            _case(
                "added-tokens",
                "from tokenizers import Tokenizer, AddedToken\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, '<x>': 2}, unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); n = t.add_tokens([AddedToken('<x>', single_word=True)]); result = {'added': n, 'tokens': t.encode('hello <x>').tokens}",
                {"added": 1, "tokens": ["hello", "<x>"]},
            ),
            _case(
                "special-tokens",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1}, unk_token='[UNK]')); n = t.add_special_tokens(['[CLS]']); result = {'added': n, 'id': t.token_to_id('[CLS]'), 'decoded': t.decode([t.token_to_id('[CLS]'), 1])}",
                {"added": 1, "id": 2, "decoded": "hello"},
            ),
            _case(
                "async-batch",
                "import asyncio\nfrom tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1, 'b': 2}, unk_token='[UNK]'))\nasync def f(): return (await t.async_encode_batch(['b', 'a']))[0].tokens\nresult = asyncio.run(f()) == ['b']",
                True,
            ),
            _case(
                "vocabulary-api",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1}, unk_token='[UNK]')); result = {'size': t.get_vocab_size(), 'a': t.token_to_id('a'), 'zero': t.id_to_token(0), 'vocab': t.get_vocab()}",
                {"size": 2, "a": 1, "zero": "[UNK]", "vocab": {"[UNK]": 0, "a": 1}},
            ),
            _case(
                "invalid-input",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0}, unk_token='[UNK]'))\ntry: t.encode(None)\nexcept Exception as e: result = type(e).__name__\nelse: result = 'no-error'",
                "TypeError",
            ),
            _case(
                "local-save-load",
                "import tempfile, pathlib\nfrom tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nt = Tokenizer(WordLevel({'[UNK]': 0, 'a': 1}, unk_token='[UNK]'))\np = pathlib.Path(tempfile.mkdtemp()) / 'tok.json'; t.save(str(p)); u = Tokenizer.from_file(str(p)); result = p.is_file() and u.encode('a').ids == [1]",
                True,
            ),
            _case(
                "normalizer",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.normalizers import Lowercase\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1}, unk_token='[UNK]')); t.normalizer = Lowercase(); result = t.encode('Hello').tokens",
                ["hello"],
            ),
            _case(
                "pretokenizer",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nt = Tokenizer(WordLevel({'[UNK]': 0, 'hello': 1, ',': 2}, unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); result = t.pre_tokenizer.pre_tokenize_str('hello,')",
                [["hello", [0, 5]], [",", [5, 6]]],
            ),
            _case(
                "wordpiece",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordPiece\nfrom tokenizers.pre_tokenizers import BertPreTokenizer\nt = Tokenizer(WordPiece({'[UNK]': 0, 'hello': 1, 'world': 2, '##s': 3}, unk_token='[UNK]')); t.pre_tokenizer = BertPreTokenizer(); result = t.encode('hello worlds').tokens",
                ["hello", "world", "##s"],
            ),
            _case(
                "bert-wrapper",
                "from tokenizers.implementations import BertWordPieceTokenizer\nt = BertWordPieceTokenizer({'[UNK]': 0, '[CLS]': 1, '[SEP]': 2, 'hello': 3, 'world': 4}, lowercase=True); result = {'tokens': t.encode('Hello world').tokens, 'size': t.get_vocab_size()}",
                {"tokens": ["[CLS]", "hello", "world", "[SEP]"], "size": 5},
            ),
            _case(
                "bytelevel-wrapper",
                "from tokenizers.implementations import ByteLevelBPETokenizer\nt = ByteLevelBPETokenizer(); result = t.pre_tokenizer is not None and t.decoder is not None and t.post_processor is not None",
                True,
            ),
            _case(
                "char-wrapper",
                "from tokenizers.implementations import CharBPETokenizer\nt = CharBPETokenizer(); t.train_from_iterator(['hello world', 'hello there'], vocab_size=20, show_progress=False); result = t.get_vocab_size() > 1 and len(t.encode('hello').tokens) > 0",
                True,
            ),
            _case(
                "unigram-wrapper",
                "from tokenizers.implementations import SentencePieceUnigramTokenizer\nt = SentencePieceUnigramTokenizer(); t.train_from_iterator(['hello world', 'hello there'], vocab_size=12, show_progress=False); result = t.get_vocab_size() > 1 and len(t.encode('hello').tokens) > 0",
                True,
            ),
            _case(
                "wordlevel-training",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nfrom tokenizers.trainers import WordLevelTrainer\nt = Tokenizer(WordLevel(unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); t.train_from_iterator(['hello world', 'hello there'], trainer=WordLevelTrainer(vocab_size=10, special_tokens=['[UNK]'])); result = {'size': t.get_vocab_size(), 'tokens': t.encode('hello world').tokens}",
                {"size": 4, "tokens": ["hello", "world"]},
            ),
            _case(
                "bpe-training",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import BPE\nfrom tokenizers.pre_tokenizers import Whitespace\nfrom tokenizers.trainers import BpeTrainer\nt = Tokenizer(BPE(unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); t.train_from_iterator(['hello world', 'hello there'], trainer=BpeTrainer(vocab_size=20, special_tokens=['[UNK]'])); result = t.encode('hello world').tokens == ['hello', 'world'] and t.get_vocab_size() == 20",
                True,
            ),
            _case(
                "unigram-training",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import Unigram\nfrom tokenizers.pre_tokenizers import Whitespace\nfrom tokenizers.trainers import UnigramTrainer\nt = Tokenizer(Unigram()); t.pre_tokenizer = Whitespace(); t.train_from_iterator(['hello world', 'hello there'], trainer=UnigramTrainer(vocab_size=12, special_tokens=['<unk>'])); result = t.get_vocab_size() >= 2 and len(t.encode('hello world').tokens) > 0",
                True,
            ),
            _case(
                "trainer-special-tokens",
                "from tokenizers import Tokenizer\nfrom tokenizers.models import WordLevel\nfrom tokenizers.pre_tokenizers import Whitespace\nfrom tokenizers.trainers import WordLevelTrainer\nt = Tokenizer(WordLevel(unk_token='[UNK]')); t.pre_tokenizer = Whitespace(); t.train_from_iterator(['a b'], trainer=WordLevelTrainer(vocab_size=5, special_tokens=['[PAD]', '[UNK]'])); result = [t.token_to_id(x) for x in ['[PAD]', '[UNK]']] == [0, 1]",
                True,
            ),
            _case(
                "component-reexports",
                "from tokenizers.normalizers import Lowercase, NFKC, Sequence\nfrom tokenizers.pre_tokenizers import Whitespace, ByteLevel, Metaspace\nfrom tokenizers.processors import TemplateProcessing, BertProcessing\nfrom tokenizers.trainers import BpeTrainer, WordLevelTrainer, WordPieceTrainer, UnigramTrainer\nresult = all(callable(x) for x in (Lowercase, NFKC, Sequence, Whitespace, ByteLevel, Metaspace, TemplateProcessing, BertProcessing, BpeTrainer, WordLevelTrainer, WordPieceTrainer, UnigramTrainer))",
                True,
            ),
        ]
    )
    print(json.dumps({"schema_version": "1.0", "leaves": cases}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
