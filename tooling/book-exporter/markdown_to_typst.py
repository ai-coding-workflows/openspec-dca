"""Small, dependency-free Markdown-to-Typst renderer for the book exporter."""

from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

BACKTICK = chr(96)
FENCE_RE = re.compile(r"^( {0,3})(" + BACKTICK + r"{3,}|~{3,})(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(" + BACKTICK + r"{3,}|~{3,})[ \t]*$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*#*\s*$")
LIST_RE = re.compile(r"^( *)([-+*]|\d+[.)])[ \t]+(.*)$")
ORDERED_RE = re.compile(r"^\d+[.)]$")
HR_RE = re.compile(r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
SPECIAL_TEXT_CHARS = set(r"\#$*_[]<>@~")


def typst_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return '"' + escaped + '"'


def escape_markup(value: str) -> str:
    return "".join("\\" + char if char in SPECIAL_TEXT_CHARS else char for char in value)


def slugify(value: str) -> str:
    value = re.sub(BACKTICK + r"([^" + BACKTICK + r"]*)" + BACKTICK, r"\1", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[*_~]", "", value).lower()
    value = re.sub(r"[^\w -]", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", "-", value).strip("-")


def _fence(line: str) -> tuple[str, int] | None:
    match = FENCE_RE.match(line)
    if not match:
        return None
    return match.group(2)[0], len(match.group(2))


def _is_closing_fence(line: str, marker: str, minimum: int) -> bool:
    match = FENCE_CLOSE_RE.match(line)
    return bool(match and match.group(1)[0] == marker and len(match.group(1)) >= minimum)


def _find_unescaped(text: str, needle: str, start: int) -> int:
    cursor = start
    while True:
        found = text.find(needle, cursor)
        if found < 0:
            return -1
        backslashes = 0
        check = found - 1
        while check >= 0 and text[check] == "\\":
            backslashes += 1
            check -= 1
        if backslashes % 2 == 0:
            return found
        cursor = found + len(needle)


def _read_link(text: str, start: int) -> tuple[int, str, str, bool] | None:
    image = text.startswith("![", start)
    opening = start + 1 if image else start
    if opening >= len(text) or text[opening] != "[":
        return None
    depth = 1
    cursor = opening + 1
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == "[":
            depth += 1
        elif text[cursor] == "]":
            depth -= 1
            if not depth:
                break
        cursor += 1
    if cursor + 1 >= len(text) or text[cursor + 1] != "(":
        return None
    label = text[opening + 1 : cursor]
    start_destination = cursor + 2
    depth = 1
    cursor = start_destination
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == "(":
            depth += 1
        elif text[cursor] == ")":
            depth -= 1
            if not depth:
                break
        cursor += 1
    if cursor >= len(text):
        return None
    raw = text[start_destination:cursor].strip()
    if raw.startswith("<") and ">" in raw:
        destination = raw[1 : raw.find(">")]
    else:
        destination = re.split(r"\s+[\"'(]", raw, maxsplit=1)[0]
    destination = destination.replace(r"\(", "(").replace(r"\)", ")")
    return cursor + 1, label, destination, image


def _heading_text(value: str) -> str:
    value = re.sub(BACKTICK + r"+([^" + BACKTICK + r"]+)" + BACKTICK + r"+", r"\1", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    return re.sub(r"[*_~]", "", value).strip()


class MarkdownToTypst:
    """Render the Markdown subset used by mdBook sources into Typst markup."""

    def __init__(self, label_prefix: str) -> None:
        self.label_prefix = "chapter-" + (slugify(label_prefix) or "book")
        self.heading_ids: dict[str, str] = {}
        self._render_heading_counts: dict[str, int] = {}

    def convert(self, markdown: str) -> str:
        lines = markdown.splitlines()
        self.heading_ids.clear()
        self._render_heading_counts.clear()
        fence = None
        counts: dict[str, int] = {}
        for line in lines:
            if fence:
                if _is_closing_fence(line, *fence):
                    fence = None
                continue
            fence = _fence(line)
            if fence:
                continue
            match = HEADING_RE.match(line)
            if match:
                slug = slugify(_heading_text(match.group(2))) or "section"
                count = counts.get(slug, 0)
                counts[slug] = count + 1
                suffix = f"-{count}" if count else ""
                self.heading_ids.setdefault(slug, f"{self.label_prefix}--{slug}{suffix}")
        return self._blocks(lines).strip() + "\n"

    def _blocks(self, lines: list[str]) -> str:
        result: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue

            fence = _fence(line)
            if fence:
                opening = FENCE_RE.match(line)
                assert opening is not None
                info = opening.group(3).strip()
                language = info.split(maxsplit=1)[0] if info else ""
                code: list[str] = []
                index += 1
                while index < len(lines) and not _is_closing_fence(lines[index], *fence):
                    code.append(lines[index])
                    index += 1
                if index < len(lines):
                    index += 1
                result.append(
                    "#raw("
                    + typst_string("\n".join(code))
                    + ", lang: "
                    + typst_string(language)
                    + ", block: true)"
                )
                continue

            heading = HEADING_RE.match(line)
            if heading:
                slug = slugify(_heading_text(heading.group(2))) or "section"
                occurrence = self._render_heading_counts.get(slug, 0)
                self._render_heading_counts[slug] = occurrence + 1
                suffix = f"-{occurrence}" if occurrence else ""
                label = f"{self.label_prefix}--{slug}{suffix}"
                result.append(
                    f"{'=' * len(heading.group(1))} {self.inline(heading.group(2).strip())} <{label}>"
                )
                index += 1
                continue

            if HR_RE.match(line):
                result.append("#line(length: 100%)")
                index += 1
                continue

            if line.lstrip().startswith(">"):
                quote_lines: list[str] = []
                while index < len(lines) and lines[index].lstrip().startswith(">"):
                    quote_lines.append(re.sub(r"^ {0,3}> ?", "", lines[index].lstrip()))
                    index += 1
                result.append("#quote(block: true)[\n" + self._blocks(quote_lines).rstrip() + "\n]")
                continue

            if self._is_table(lines, index):
                table, index = self._table(lines, index)
                result.append(table)
                continue

            if LIST_RE.match(line):
                items: list[str] = []
                while index < len(lines):
                    if LIST_RE.match(lines[index]):
                        items.append(lines[index])
                        index += 1
                    elif (
                        not lines[index].strip()
                        and index + 1 < len(lines)
                        and LIST_RE.match(lines[index + 1])
                    ):
                        items.append("")
                        index += 1
                    else:
                        break
                result.append(self._list(items))
                continue

            if line.lstrip().startswith("$$"):
                math_lines: list[str] = []
                opening_math = line.strip()[2:]
                if opening_math.endswith("$$") and len(opening_math) > 2:
                    result.append("$ " + opening_math[:-2].strip() + " $")
                    index += 1
                    continue
                if opening_math:
                    math_lines.append(opening_math)
                index += 1
                while index < len(lines) and "$$" not in lines[index]:
                    math_lines.append(lines[index])
                    index += 1
                if index < len(lines):
                    math_lines.append(lines[index].split("$$", 1)[0])
                    index += 1
                result.append("$ " + "\n".join(math_lines).strip() + " $")
                continue

            paragraph = [line]
            index += 1
            while index < len(lines) and lines[index].strip() and not self._starts_block(lines, index):
                paragraph.append(lines[index])
                index += 1
            result.append(self._paragraph(paragraph))
        return "\n\n".join(part for part in result if part)

    def _starts_block(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        return bool(
            _fence(line)
            or HEADING_RE.match(line)
            or HR_RE.match(line)
            or line.lstrip().startswith(">")
            or LIST_RE.match(line)
            or self._is_table(lines, index)
            or line.lstrip().startswith("$$")
        )

    def _paragraph(self, lines: list[str]) -> str:
        output: list[str] = []
        for line in lines:
            hard_break = line.endswith("  ") or line.endswith("\\")
            value = line.rstrip()
            if hard_break:
                value = value.rstrip(" \\")
            output.append(self.inline(value) + (" \\\\" if hard_break else ""))
        return " ".join(output)

    def _list(self, lines: list[str]) -> str:
        output: list[str] = []
        for line in lines:
            if not line:
                output.append("")
                continue
            match = LIST_RE.match(line)
            if not match:
                output.append(line)
                continue
            indent, marker, text = match.groups()
            typst_marker = "+" if ORDERED_RE.match(marker) else "-"
            task = re.match(r"^\[([ xX])\][ \t]*(.*)$", text)
            if task:
                state, body = task.groups()
                checkbox = "[x]" if state.lower() == "x" else "[ ]"
                rendered = checkbox + " " + self.inline(body)
            else:
                rendered = self.inline(text)
            output.append(f"{indent}{typst_marker} {rendered}".rstrip())
        return "\n".join(output)

    @staticmethod
    def _split_row(line: str) -> list[str]:
        value = line.strip()
        if value.startswith("|"):
            value = value[1:]
        if value.endswith("|"):
            value = value[:-1]
        return [cell.strip() for cell in value.split("|")]

    def _is_table(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines) or "|" not in lines[index]:
            return False
        cells = self._split_row(lines[index + 1])
        return bool(cells) and all(TABLE_SEPARATOR_RE.fullmatch(cell) for cell in cells)

    def _table(self, lines: list[str], start: int) -> tuple[str, int]:
        rows = [self._split_row(lines[start])]
        index = start + 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            rows.append(self._split_row(lines[index]))
            index += 1
        width = max((len(row) for row in rows), default=1)
        cells: list[str] = []
        for row in rows:
            for cell in (row + [""] * width)[:width]:
                cells.append("[" + self.inline(cell) + "]")
        table = (
            f"#table(columns: {width}, inset: 5pt, stroke: 0.5pt + luma(75%),\n  "
            + ",\n  ".join(cells)
            + "\n)"
        )
        return table, index

    def _link_target(self, destination: str) -> str:
        parsed = urlsplit(destination)
        if not parsed.path and parsed.fragment and not parsed.scheme:
            fragment = slugify(unquote(parsed.fragment))
            if fragment.startswith("chapter-"):
                return "<" + fragment + ">"
            return "<" + self.heading_ids.get(
                fragment, f"{self.label_prefix}--{fragment}"
            ) + ">"
        return destination

    def inline(self, text: str) -> str:
        output: list[str] = []
        index = 0
        while index < len(text):
            if text[index] == "\\" and index + 1 < len(text):
                output.append(escape_markup(text[index + 1]))
                index += 2
                continue

            if text.startswith("![", index) or text[index] == "[":
                link = _read_link(text, index)
                if link:
                    end, label, destination, image = link
                    output.append(
                        "#image("
                        + typst_string(unquote(destination))
                        + ", alt: "
                        + typst_string(label)
                        + ")"
                        if image
                        else "#link("
                        + (
                            self._link_target(destination)
                            if self._link_target(destination).startswith("<")
                            else typst_string(self._link_target(destination))
                        )
                        + ")["
                        + self.inline(label)
                        + "]"
                    )
                    index = end
                    continue

            if text[index] == BACKTICK:
                size = 1
                while index + size < len(text) and text[index + size] == BACKTICK:
                    size += 1
                delimiter = BACKTICK * size
                closing = _find_unescaped(text, delimiter, index + size)
                if closing >= 0:
                    code = text[index + size : closing].replace("\n", " ")
                    if len(code) >= 2 and code.startswith(" ") and code.endswith(" ") and code.strip():
                        code = code[1:-1]
                    output.append("#raw(" + typst_string(code) + ")")
                    index = closing + size
                    continue

            delimiter = None
            function = None
            for marker, name in (("**", "strong"), ("__", "strong"), ("~~", "strike")):
                if text.startswith(marker, index):
                    delimiter, function = marker, name
                    break
            if delimiter is None and text[index] in "*_":
                delimiter, function = text[index], "emph"
            if delimiter:
                closing = _find_unescaped(text, delimiter, index + len(delimiter))
                if closing > index + len(delimiter):
                    inner = self.inline(text[index + len(delimiter) : closing])
                    output.append("#" + function + "[" + inner + "]")
                    index = closing + len(delimiter)
                    continue

            if text.startswith("<https://", index) or text.startswith("<http://", index):
                close = text.find(">", index + 1)
                if close > index:
                    url = text[index + 1 : close]
                    output.append("#link(" + typst_string(url) + ")[" + escape_markup(url) + "]")
                    index = close + 1
                    continue

            if text[index : index + 4].lower() == "<br>" or text[index : index + 5].lower() == "<br/>":
                length = 4 if text[index : index + 4].lower() == "<br>" else 5
                output.append("#linebreak()")
                index += length
                continue

            if text.startswith("$$", index):
                closing = _find_unescaped(text, "$$", index + 2)
                if closing >= 0:
                    output.append("$ " + text[index + 2 : closing].strip() + " $")
                    index = closing + 2
                    continue
            if text[index] == "$":
                closing = _find_unescaped(text, "$", index + 1)
                if closing > index + 1:
                    output.append("$" + text[index + 1 : closing] + "$")
                    index = closing + 1
                    continue

            output.append(escape_markup(text[index]))
            index += 1
        return "".join(output)
