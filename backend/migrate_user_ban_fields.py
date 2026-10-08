"""Safely add user ban fields to an existing database."""

from database import DATABASE_URL, init_db


def main() -> None:
    init_db()
    print(f"User ban field migration completed for {DATABASE_URL}")


if __name__ == "__main__":
    main()
