"""Create the initial approved administrator if it does not already exist."""

import bcrypt
from sqlalchemy import select

from database import SessionLocal, User, init_db


ADMIN_NAME = "KelvineChen"
USERNAME = "KelvineChen"
EMAIL = "kelvinechen@example.com"
SCHOOL = "ECNU"
MAJOR = "DataScience"


def main() -> None:
    init_db()

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(
                (User.admin_name == ADMIN_NAME) | (User.username == USERNAME)
            )
        )
        if existing:
            print(f"管理员已存在，跳过插入：{ADMIN_NAME}")
            return

        admin = User(
            admin_name=ADMIN_NAME,
            username=USERNAME,
            email=EMAIL,
            admin_password_hash=bcrypt.hashpw(
                b"111AAA",
                bcrypt.gensalt(),
            ).decode("utf-8"),
            user_password_hash=bcrypt.hashpw(
                b"Cqz070806",
                bcrypt.gensalt(),
            ).decode("utf-8"),
            role="admin",
            admin_status="approved",
            school=SCHOOL,
            major=MAJOR,
        )
        db.add(admin)
        db.commit()
        print(f"初始管理员插入成功：{ADMIN_NAME}")


if __name__ == "__main__":
    main()
