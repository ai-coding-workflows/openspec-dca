"""Validate, select, and render the project guidance proposal (stdlib only)."""

import re

IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RESIDUAL = re.compile(r"\{\{/?(?:groups?|hook|slot|schema-name)\b")


def identifier(value):
    return isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None


def title(value):
    return (isinstance(value, str) and bool(value.strip())
            and not any(ord(char) < 32 for char in value))


def source(value, *, allow_base=False):
    if allow_base and isinstance(value, str) and value.startswith("base:"):
        value = value[len("base:"):]
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or value.startswith("/") or any(ord(char) < 32 for char in value)
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError(f"Unsafe guidance source: {value!r}")


def plan(config, manifest_guidance=()):
    """Return a render context with ordered active groups, fragments, and packages.

    manifest_guidance is an iterable of optional manifest guidance objects in
    dependency selection order. Shared package manifests must not feed this plan.
    Source existence and symlink checks belong to the caller's source resolver.
    """
    if (not isinstance(config, dict) or set(config) != {"intro", "groups"}
            or not isinstance(config["groups"], list)):
        raise ValueError("Invalid guidance configuration")
    source(config["intro"])
    groups = {}
    for group in config["groups"]:
        if (not isinstance(group, dict) or not {"id", "title"}.issubset(group)
                or set(group) - {"id", "title", "parent", "always", "source", "packages"}
                or not identifier(group["id"]) or not title(group["title"])
                or ("parent" in group and not identifier(group["parent"]))
                or ("always" in group and not isinstance(group["always"], bool))):
            raise ValueError(f"Invalid guidance group: {group!r}")
        if group["id"] in groups:
            raise ValueError(f"Duplicate guidance group: {group['id']}")
        if "source" in group:
            source(group["source"], allow_base=True)
        packages = group.get("packages", [])
        if (not isinstance(packages, list) or any(not identifier(item) for item in packages)
                or len(set(packages)) != len(packages)):
            raise ValueError(f"Invalid guidance packages: {group['id']}")
        groups[group["id"]] = dict(group)

    levels = {}

    def level(name, visiting):
        if name not in groups:
            raise ValueError(f"Unknown guidance group: {name}")
        if name in visiting:
            raise ValueError(f"Guidance parent cycle: {name}")
        if len(visiting) >= 5:
            raise ValueError(f"Guidance heading depth exceeds six: {name}")
        if name not in levels:
            parent = groups[name].get("parent")
            levels[name] = 2 if parent is None else level(parent, visiting | {name}) + 1
            if levels[name] > 6:
                raise ValueError(f"Guidance heading depth exceeds six: {name}")
        return levels[name]

    for name in groups:
        level(name, set())
    active = set()

    def activate(name):
        while name is not None:
            active.add(name)
            name = groups[name].get("parent")

    for name, group in groups.items():
        if group.get("always", False):
            activate(name)
    fragments = {name: [] for name in groups}
    for fragment in manifest_guidance:
        if fragment is None:
            continue
        if (not isinstance(fragment, dict) or set(fragment) != {"group", "title", "source"}
                or not identifier(fragment["group"]) or not title(fragment["title"])):
            raise ValueError(f"Invalid manifest guidance: {fragment!r}")
        source(fragment["source"])
        name = fragment["group"]
        if name not in groups:
            raise ValueError(f"Unknown guidance group: {name}")
        if levels[name] + 1 > 6:
            raise ValueError(f"Guidance component heading depth exceeds six: {name}")
        fragments[name].append(dict(fragment))
        activate(name)
    packages = []
    for name, group in groups.items():
        if name in active:
            for package in group.get("packages", []):
                if package not in packages:
                    packages.append(package)
    return {"intro": config["intro"], "groups": [group for name, group in groups.items()
            if name in active], "fragments": fragments, "levels": levels, "packages": packages}


def rebase(text, minimum=None):
    """Nest headings below a section, or only validate them; preserve fenced code."""
    lines = text.splitlines()
    headings = []
    fence = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", line):
                fence = None
            index += 1
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening and (opening[1][0] != "`" or "`" not in opening[2]):
            fence = (opening[1][0], len(opening[1]))
            index += 1
            continue
        heading = re.match(r"^( {0,3})(#+)(?:[ \t]+|$)(.*)$", line)
        if heading:
            headings.append((index, len(heading[2]), heading[1], heading[3], False))
        elif (line.strip() and not line.startswith(("    ", "\t"))
              and index + 1 < len(lines)
              and re.fullmatch(r" {0,3}(?:=+|-+)\s*", lines[index + 1])):
            headings.append((index, 1 if lines[index + 1].lstrip().startswith("=") else 2,
                             "", line.strip(), True))
            index += 1
        index += 1
    if headings:
        lowest = min(item[1] for item in headings)
        for index, depth, indentation, content, setext in headings:
            target = depth if minimum is None else depth + minimum - lowest
            if depth > 6 or target > 6:
                raise ValueError("Guidance source heading depth exceeds six")
            if minimum is not None:
                lines[index] = indentation + "#" * target + " " + content
                if setext:
                    lines[index + 1] = None
    return "\n".join(line for line in lines if line is not None).strip()


def render(context, read_source, schema_name):
    """Render a plan as Markdown; read_source also resolves base: schema sources."""
    def text(value):
        return value.replace("openspec-ddd", schema_name).replace("{{schema-name}}", schema_name)

    blocks = [rebase(text(read_source(context["intro"])))]

    def emit(group):
        depth = context["levels"][group["id"]]
        blocks.append("#" * depth + " " + text(group["title"]))
        if "source" in group:
            blocks.append(rebase(text(read_source(group["source"])), depth + 1))
        for fragment in context["fragments"][group["id"]]:
            blocks.append("#" * (depth + 1) + " " + text(fragment["title"]))
            blocks.append(rebase(text(read_source(fragment["source"])), depth + 2))
        for child in context["groups"]:
            if child.get("parent") == group["id"]:
                emit(child)

    for group in context["groups"]:
        if "parent" not in group:
            emit(group)
    result = "\n\n".join(block for block in blocks if block) + "\n"
    if RESIDUAL.search(result):
        raise ValueError("Unresolved guidance placeholder")
    return result
