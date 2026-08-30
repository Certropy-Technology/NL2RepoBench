from __future__ import annotations

import re


class CoreBPE:
    def __init__(self, mergeable_ranks: dict[bytes, int], special_tokens: dict[str, int], pat_str: str):
        self.ranks = dict(mergeable_ranks)
        self.special = dict(special_tokens)
        self.decoder = {value: key for key, value in self.ranks.items()}
        self.decoder.update({value: key.encode() for key, value in self.special.items()})
        try:
            import regex
            self.pattern = regex.compile(pat_str)
        except ImportError:
            self.pattern = re.compile(pat_str)

    def _piece(self, value: bytes) -> list[int]:
        parts = [bytes([byte]) for byte in value]
        while len(parts) > 1:
            choice = None
            for index, pair in enumerate(zip(parts, parts[1:])):
                rank = self.ranks.get(pair[0] + pair[1])
                if rank is not None and (choice is None or rank < choice[0]):
                    choice = (rank, index)
            if choice is None:
                break
            _, index = choice
            parts[index:index + 2] = [parts[index] + parts[index + 1]]
        return [self.ranks[part] for part in parts]

    def encode_ordinary(self, text: str) -> list[int]:
        return [token for match in self.pattern.findall(text) for token in self._piece(match.encode())]

    def encode(self, text: str, allowed_special: set[str]) -> list[int]:
        if not allowed_special:
            return self.encode_ordinary(text)
        pattern = re.compile("|".join(re.escape(token) for token in sorted(allowed_special, key=len, reverse=True)))
        result = []
        cursor = 0
        for match in pattern.finditer(text):
            result.extend(self.encode_ordinary(text[cursor:match.start()]))
            result.append(self.special[match.group()])
            cursor = match.end()
        result.extend(self.encode_ordinary(text[cursor:]))
        return result

    def encode_with_unstable(self, text: str, allowed_special: set[str]) -> tuple[list[int], list[list[int]]]:
        return self.encode(text, allowed_special), []

    def encode_single_token(self, value: bytes) -> int:
        return self.ranks[value]

    def decode_bytes(self, tokens: list[int]) -> bytes:
        return b"".join(self.decoder[token] for token in tokens)

    def decode_single_token_bytes(self, token: int) -> bytes:
        return self.decoder[token]

    def token_byte_values(self) -> list[bytes]:
        return [self.decoder[index] for index in sorted(self.decoder)]
