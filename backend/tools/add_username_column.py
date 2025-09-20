import sqlite3, re, pathlib
# 1) 기본값: backend 폴더의 app.db
db_path = pathlib.Path("app.db")

# 2) app/db.py에서 실제 DB 파일명 추론 시도 (sqlite+aiosqlite:///./파일명 형태)
try:
    txt = pathlib.Path("app/db.py").read_text(encoding="utf-8")
    m = re.search(r"sqlite\+aiosqlite:///\.?/?([^\"'\n]+)", txt)
    if m:
        db_path = pathlib.Path(m.group(1))
except FileNotFoundError:
    pass

if not db_path.exists():
    print(f"[X] DB 파일을 찾을 수 없습니다: {db_path.resolve()}")
    raise SystemExit(1)

con = sqlite3.connect(db_path)
cur = con.cursor()

# users 테이블 컬럼 조회
cur.execute("PRAGMA table_info(users)")
cols = [row[1] for row in cur.fetchall()]

if "username" not in cols:
    # 컬럼 추가
    cur.execute("ALTER TABLE users ADD COLUMN username TEXT")
    # 기존 데이터 보존을 위해 email을 임시 username으로 채움(필요시 수정)
    cur.execute("UPDATE users SET username = COALESCE(username, email)")
    # 유니크 인덱스(있으면 무시)
    try:
        cur.execute("CREATE UNIQUE INDEX ix_users_username ON users(username)")
    except sqlite3.OperationalError:
        pass
    con.commit()
    print("[✓] username 컬럼 추가 완료")
else:
    print("[=] username 컬럼이 이미 존재합니다.")

con.close()
