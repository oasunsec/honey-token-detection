from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets

from .config import Settings
from .db import Database
from .decoys import callback_url, create_docx_decoy, create_html_decoy, validate_filename


def main() -> None:
    parser = argparse.ArgumentParser(description="Create honeytokens and decoy documents")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a token and decoy file")
    create.add_argument("--name", required=True)
    create.add_argument("--filename", default="Synthetic_Forecast.docx")
    create.add_argument("--format", choices=["html", "docx"], default="docx")
    create.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="high")
    create.add_argument("--output", default="decoys")
    create.add_argument("--notes", default="")

    args = parser.parse_args()
    settings = Settings()
    db = Database(settings.db_path)

    if args.command == "create":
        validate_filename(args.filename)
        token_id = secrets.token_urlsafe(18)
        db.create_token(token_id, args.name, args.filename, args.severity, args.notes)
        url = callback_url(settings.base_url, token_id)
        output = Path(args.output)
        if args.format == "docx":
            filename = args.filename if args.filename.lower().endswith(".docx") else Path(args.filename).stem + ".docx"
            path = create_docx_decoy(output, filename, url)
        else:
            filename = args.filename if args.filename.lower().endswith((".html", ".htm")) else Path(args.filename).stem + ".html"
            path = create_html_decoy(output, filename, url)
        print(json.dumps({"token_id": token_id, "callback_url": url, "decoy": str(path)}, indent=2))


if __name__ == "__main__":
    main()
