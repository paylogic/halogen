"""Generate .pyi stubs for Schema subclasses in a module."""

from __future__ import annotations

import argparse
import importlib
import inspect
from pathlib import Path
from typing import Any, get_args, get_origin

import halogen


def _is_typed_dict(obj: Any) -> bool:
    return (
        isinstance(obj, type)
        and issubclass(obj, dict)
        and hasattr(obj, "__annotations__")
        and hasattr(obj, "__total__")
    )


def _type_to_str(tp: Any) -> str:
    if isinstance(tp, str):
        return tp

    if _is_typed_dict(tp):
        return tp.__name__

    origin = get_origin(tp)
    if origin is None:
        if tp is None or tp is type(None):
            return "None"
        if isinstance(tp, type):
            return tp.__name__
        return repr(tp)

    args = get_args(tp)

    if origin is list:
        return f"list[{_type_to_str(args[0])}]"
    if origin is dict:
        return f"dict[{_type_to_str(args[0])}, {_type_to_str(args[1])}]"
    if origin is tuple:
        return f"tuple[{', '.join(_type_to_str(a) for a in args)}]"

    if str(origin).endswith("typing.Optional"):
        return f"Optional[{_type_to_str(args[0])}]"

    if str(origin).endswith("typing.NotRequired"):
        return f"NotRequired[{_type_to_str(args[0])}]"

    if str(origin).endswith("typing.Required"):
        return f"Required[{_type_to_str(args[0])}]"

    return f"{origin}[{', '.join(_type_to_str(a) for a in args)}]"


def _collect_typed_dicts(tp: Any, acc: dict[str, type]) -> None:
    if _is_typed_dict(tp):
        if tp.__name__ in acc:
            return
        acc[tp.__name__] = tp
        for value in tp.__annotations__.values():
            _collect_typed_dicts(value, acc)
        return

    origin = get_origin(tp)
    if origin is not None:
        for arg in get_args(tp):
            _collect_typed_dicts(arg, acc)


def _emit_typed_dict(td: type) -> str:
    lines = [f"class {td.__name__}(TypedDict, total={td.__total__}):"]
    if not td.__annotations__:
        lines.append("    pass")
        return "\n".join(lines)

    for name, tp in td.__annotations__.items():
        lines.append(f"    {name}: {_type_to_str(tp)}")
    return "\n".join(lines)


def generate(module_name: str, output_path: str | None = None) -> Path:
    module = importlib.import_module(module_name)

    schema_classes = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module.__name__:
            continue
        if issubclass(obj, halogen.Schema):
            schema_classes.append(obj)

    if not schema_classes:
        raise SystemExit(f"No Schema subclasses found in {module_name}.")

    if output_path is None:
        output_path = str(Path(module.__file__).with_suffix(".pyi"))

    typed_dicts: dict[str, type] = {}
    for schema_cls in schema_classes:
        td = getattr(schema_cls, "__output_type__", None)
        if td is not None:
            _collect_typed_dicts(td, typed_dicts)

    lines = [
        "from __future__ import annotations",
        "from typing import TypedDict, Optional, NotRequired, Required",
        "import halogen",
        "",
    ]

    for td in typed_dicts.values():
        lines.append(_emit_typed_dict(td))
        lines.append("")

    for schema_cls in schema_classes:
        lines.append(f"class {schema_cls.__name__}(halogen.Schema):")
        td = getattr(schema_cls, "__output_type__", None)
        if td is None:
            lines.append("    ...")
            lines.append("")
            continue

        lines.append("    @classmethod")
        lines.append(
            f"    def serialize(cls, value, **kwargs) -> {td.__name__}: ..."
        )
        lines.append("    @classmethod")
        lines.append(
            f"    def deserialize(cls, value, output=None, **kwargs) -> dict: ..."
        )
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    path = Path(output_path)
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate .pyi stubs for Schema subclasses in a module."
    )
    parser.add_argument("module", help="Module path containing Schema subclasses")
    parser.add_argument("--out", help="Output .pyi path (default: module path)")
    args = parser.parse_args()

    path = generate(args.module, args.out)
    print(path)


if __name__ == "__main__":
    main()
