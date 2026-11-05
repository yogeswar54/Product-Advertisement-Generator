from __future__ import annotations

import argparse
from app.services.asset_storage import cleanup_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove expired generated assets and metadata records.")
    parser.add_argument("--days", type=int, default=30, help="Minimum asset age to remove, in days.")
    arguments = parser.parse_args()
    print(f"Removed {cleanup_assets(arguments.days)} asset(s).")


if __name__ == "__main__":
    main()
