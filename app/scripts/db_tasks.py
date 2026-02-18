from __future__ import annotations

import argparse

from app.db.Connection import create_db_and_tables, seed_catalog_items


def run_setup() -> None:
    create_db_and_tables()
    print("Database tables created (if missing).")


def run_seed() -> None:
    seed_catalog_items()
    print("Catalog seed complete (skips when data already exists).")


def run_init() -> None:
    run_setup()
    run_seed()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database setup and seed tasks.")
    parser.add_argument(
        "command",
        choices=("setup", "seed", "init"),
        help="Task to run: setup tables, seed data, or both.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "setup":
        run_setup()
        return
    if args.command == "seed":
        run_seed()
        return
    run_init()


if __name__ == "__main__":
    main()
