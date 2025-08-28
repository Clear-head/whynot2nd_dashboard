import asyncio
from sqlalchemy import create_engine, text
import pandas as pd 
import numpy as np
import uuid


# 데이터 전처리 
# 전처리 
def make_roadkill_info(
    csv_path: str,
    *,
    encoding: str = "cp949",
    seed: int | None = 42
) -> pd.DataFrame:
    # CSV 로드, 컬럼 정리
    df = pd.read_csv(csv_path, encoding=encoding)
    df.columns = df.columns.str.replace("\ufeff","",regex=True).str.strip()

    # 컬럼 이름 변경
    # 본부명: head, 지사명:branch
    col_map = {
        "본부명":"head", "지사명":"branch", "노선명":"line",
        "방 향":"direction", "방향":"direction",
        "발생건수":"freq", "위도":"lat", "경도":"lon"
    }

    use_cols = [c for c in col_map if c in df.columns]
    df = df[use_cols].rename(columns=col_map).copy()

    # 타입 보정
    df["freq"] = pd.to_numeric(df["freq"], errors="coerce").fillna(0).astype("int64")
    df["lat"]  = pd.to_numeric(df["lat"],  errors="coerce")
    df["lon"]  = pd.to_numeric(df["lon"],  errors="coerce")

    # status 랜덤, - 나중엔 필요없음 
    if seed is not None:
        np.random.seed(seed)
    df["status"] = np.random.choice([0,1,2], size=len(df)).astype("int8")

    # 추정치 빈 컬럼
    df["추정치"] = ""
    # 최종 컬럼 순서
    df = df[["head","branch","line","direction","freq","lat","lon","status","추정치"]]
    return df


def conn_engine():
    """
        sqlalchemy connector
    :return:
    """
    engine = None
    try:
        engine = create_engine("mysql+pymysql://root:1234@localhost/roadkill_db?charset=utf8", pool_pre_ping=True)

        if engine is None:
            raise Exception(f"engine is None")

    except Exception as e:
        print(f"[database] connection error: {e}")
    return engine

# 테이블 생성 
def ensure_table_roadkill_info(engine, table="roadkill_info"):
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        `id`          VARCHAR(255) NOT NULL,
        `head`        VARCHAR(255) NOT NULL,
        `branch`      VARCHAR(255) NOT NULL,
        `line`        VARCHAR(255) NOT NULL,
        `direction`   VARCHAR(50)  NOT NULL,
        `freq`        INT UNSIGNED NOT NULL,
        `lat`         float NOT NULL,
        `lon`         float NOT NULL,
        `status`      TINYINT NOT NULL COMMENT '0=발견,1=재발견,2=죽음',
        `time`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
        `추정치`     VARCHAR(200) NULL,
        PRIMARY KEY (id),                 
        INDEX idx_ts (time),
        INDEX idx_head (head),
        INDEX idx_branch (branch),
        INDEX idx_line (line)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(ddl))
    except Exception as e:
        print(f"[database] ensure_table_roadkill_info error: {e}")
    
# 현재있는 id 집합
def fetch_existing_ids(engine, table="roadkill_info"):
    sql = text(f"SELECT id FROM {table}")
    try:
        with engine.begin() as conn:
            rows = conn.execute(sql).fetchall()
        # id들을 set으로 반환
    except Exception as e:
        print(f"[database] fetch_existing_ids error: {e}")
        raise e
    return {row[0] for row in rows}

# UUID 생성 
def get_uuid(existing_ids: set):
    new_id = uuid.uuid4()
    while str(new_id) in existing_ids:   # 문자열 PK라면 str로 맞춰줌
        new_id = uuid.uuid4()
    return str(new_id)


# 한 row씩 적재
async def stream_rows(engine, table="roadkill_info", sleep_sec=1.0):
    # 1) 현재 DB에 있는 ID들 가져오기
    df = make_roadkill_info("./database/한국도로공사_로드킬 데이터 정보_20250501.csv", encoding="cp949")
    existing_ids = fetch_existing_ids(engine, table)

    sql = text(f"""
        INSERT INTO {table} (
            id, head, branch, line, direction, freq, lat, lon, status, `추정치`
        ) VALUES (:id, :head, :branch, :line, :direction, :freq, :lat, :lon, :status, :추정치)
    """)
    try:

        for _, r in enumerate(df.itertuples(index=False), 1):
            params = {
                "id": get_uuid(existing_ids),   # 여기서 중복 없는 id 생성
                "head": r.head,
                "branch": r.branch,
                "line": r.line,
                "direction": r.direction,
                "freq": int(r.freq),
                "lat": float(r.lat),
                "lon": float(r.lon),
                "status": int(r.status),
                "추정치": getattr(r, "추정치", None),
            }
            with engine.begin() as conn:
                conn.execute(sql, params)

            existing_ids.add(params["id"])  # 새로 추가된 id도 캐시에 반영
            await asyncio.sleep(sleep_sec)
    except Exception as e:
        print(f"[database] stream_rows error: {e}")



# select을 했을때 위도 경도 상태 -> tuple로 리턴, 나머지 
from sqlalchemy import text
import datetime


def lat_lon_stat_info(engine):
    data = []

    # 1시간 전 시간을 datetime 객체로 생성
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=1)

    sql = """
          SELECT head,
                 branch,
                 line,
                 direction,
                 lat,
                 lon,
                 status, time
          FROM roadkill_info
          WHERE time >= :time_param
          """
    try:
        with engine.begin() as conn:
            for row in conn.execute(text(sql).bindparams(time_param=time_threshold)).mappings():
                dt = row["time"]
                time_str = f"{dt.year}-{dt.month}-{dt.day} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

                coord = (row["lat"], row["lon"], row["status"])
                meta = [row["head"], row["branch"], row["line"], row["direction"], time_str]
                data.append({"latitude": row["lat"], "longitude": row["lon"], "contents": ' '.join(meta),
                             "status": row["status"]})

        return data
    except Exception as e:
        print(f"[database] lat_lon_stat_info error: {e}")