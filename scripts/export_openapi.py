from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.main import app


def export_openapi(output_path: Path) -> None:
    """Generate the OpenAPI schema and write it to ``output_path``."""

    schema = app.openapi()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, indent=2))
    print(f"OpenAPI schema written to {output_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the FastAPI OpenAPI schema to a file")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("openapi.json"),
        help="Destination path for the generated OpenAPI document",
    )
    args = parser.parse_args()

    export_openapi(args.output)


if __name__ == "__main__":
    main()
