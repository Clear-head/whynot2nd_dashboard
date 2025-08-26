import pymysql
from sqlalchemy import create_engine, text
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
import time as _time

# DB 연결 함수
def make_engine(
    user: str = "root",
    password: str = "1234",
    host: str = "localhost",
    port: int = 3306,
    db: str = "roadkill_db",
    charset: str = "utf8mb4",
):
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset={charset}"
    return create_engine(url, pool_pre_ping=True)

# 데이터 전처리 
# csv 읽어오기 -> 컬럼이름 정리/이름 변경 -> dtype 보정 (나중에 sql가서 오류 안나게) 
# -> (status 임시 생성) -> 추정치 빈 문자열 생성 -> mysql에 적재 가능한 DF로 변환
def make_roadkill_info(
    csv_path: str,
    *,
    encoding: str = "cp949",
    seed: int | None = 42,
    start_dt: str | None = None,     
    time_as_string: bool = True,     # 결과 time을 문자열로
    apply_rules: bool = True         # 중복 좌표 상태 규칙 적용
) -> pd.DataFrame:
    # CSV 로드, 컬럼 정리
    df = pd.read_csv(csv_path, encoding=encoding)
    df.columns = df.columns.str.replace("\ufeff","",regex=True).str.strip()

    # 컬럼 이름 변경 
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
    # (0=발견,1=재발견,2=죽음)
    if seed is not None:
        np.random.seed(seed)
    df["status"] = np.random.choice([0,1,2], size=len(df)).astype("int8")

    # 추정치 빈 컬럼
    df["추정치"] = ""
    # 최종 컬럼 순서
    df = df[["head","branch","line","direction","freq","lat","lon","status","추정치"]]
    return df

# 테이블 생성 
def ensure_table_roadkill_info(engine, table="roadkill_info"):
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        head        VARCHAR(255) NOT NULL,
        branch      VARCHAR(255) NOT NULL,
        line        VARCHAR(255) NOT NULL,
        direction   VARCHAR(50)  NOT NULL,
        freq        INT UNSIGNED NOT NULL,
        lat         float NOT NULL,$
        lon         float NOT NULL,
        status      TINYINT NOT NULL COMMENT '0=발견,1=재발견,2=죽음',
        time        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
        `추정치`     VARCHAR(200) NULL,
        INDEX idx_ts (time),
        INDEX idx_head (head),
        INDEX idx_branch (branch),
        INDEX idx_line (line)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))

    return engine


# 한 row씩 적재
def stream_rows(df, engine, table="roadkill_info", sleep_sec=1.0):
    sql = text(f"""
        INSERT IGNORE INTO {table}
        (head, branch, line, direction, freq, lat, lon, status, `추정치`)
        VALUES (:head, :branch, :line, :direction, :freq, :lat, :lon, :status, :추정치)
    """)
    with engine.begin() as conn:
        for _, r in enumerate(df.itertuples(index=False), 1):
            params = {
                "head": r.head, "branch": r.branch, "line": r.line, "direction": r.direction,
                "freq": int(r.freq), "lat": float(r.lat), "lon": float(r.lon),
                "status": int(r.status), "추정치": getattr(r, "추정치", ""),
            }
        conn.execute(sql, params)
        if sleep_sec:
            _time.sleep(sleep_sec)



def lat_lon_stat(df):
    # 위도 경도 상태 -> tuple로 리턴 
    col_tuples = ((df['lat'], df['lon'], df['status']))
    
# select을 했을때 위도 경도 상태 -> tuple로 리턴, 나머지 

# 쿼리 뽑기 
def day_frequency(df):
    sql = """
    SELECT , 
            DATE(time) as dt,
            SUM(freq) as total_freq
    FROM roadkill_info
    GROUP BY branch, DATE(time)
    ORDER BY branch
    """
    
    with engine.begin() as conn:
        for row in conn.execute(text(sql)).mappings():
            return(row["branch"], row[ "dt"], row["total_freq"])


# tuple 
def lat_lon_stat_info(df):
    sql = """
    SELECT head,
            branch,
            line, 
            direction,
            lat,
            lon,
            status,
            time 
    FROM roadkill_info
    """
    with engine.begin() as conn:
        for row in conn.execute(text(sql)).mappings():
            dt = row["time"] 
            time_str = f"{dt.year}-{dt.month}-{dt.day} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

            coord = (row["lat"], row["lon"], row["status"])
            meta  = [row["head"], row["branch"], row["line"], row["direction"], time_str]

            return(coord, meta)   
        
# 실행 코드
df = make_roadkill_info("C:\githome\hipython_rep\whynot2nd_dashboard\src\database\한국도로공사_로드킬 데이터 정보_20250501.csv", encoding="cp949")
engine = make_engine(
    user: str = "root",
    password: str = "1234",
    host: str = "localhost",
    port: int = 3306,
    db: str = "roadkill_db",
    charset: str = "utf8mb4")

# 테이블 생성 실행 함수
ensure_table_roadkill_info(engine, table="roadkill_info")
# 한 줄씩 적재       
stream_rows(df, engine, table="roadkill_info", sleep_sec=0.5)
day_frequency(df)
lat_lon_stat_info(df)