import pymysql
from sqlalchemy import create_engine, text
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
import time

# 데이터 전처리 
# 전처리 
def make_roadkill_info(
    csv_path: str,
    *,
    encoding: str = "cp949",
    seed: int | None = 42,
    start_dt: str | None = None,     
    step_seconds: int = 240,         # time 설정해둔거, 실제 데이터 들어오면 필요없음 
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
    if seed is not None:
        np.random.seed(seed)
    df["status"] = np.random.choice([0,1,2], size=len(df)).astype("int8")

    # 4분 간격 timestamp - 이것도 나중엔 필요없음
    base = datetime.now().replace(microsecond=0) if start_dt is None else pd.to_datetime(start_dt).to_pydatetime()
    times = [base + timedelta(seconds=i*step_seconds) for i in range(len(df))]
    ts = pd.to_datetime(times)
    df["time"] = ts.strftime("%Y-%m-%d %H:%M:%S") if time_as_string else ts

    if apply_rules:
        work = df.copy()
        work["time"] = pd.to_datetime(work["time"], errors="coerce")
        sizes = work.groupby(["lat","lon"], sort=False)["time"].transform("size")
        dup = work.loc[sizes>=2].sort_values(["lat","lon","time"]).copy()
        if not dup.empty:
            H1  = pd.Timedelta(hours=1).value
            H24 = pd.Timedelta(hours=24).value
            def assign(g: pd.DataFrame) -> pd.DataFrame:
                ts = g["time"].to_numpy("datetime64[ns]")
                st = g["status"].to_numpy(copy=True)
                if len(g)>0: st[0]=0
                if len(g)>=2:
                    d = (ts-ts[0]).astype("timedelta64[ns]").astype("int64")
                    within_1h = (d>0) & (d<=H1)
                    st[within_1h] = 1
                    idx1 = np.flatnonzero(within_1h)
                    if idx1.size>0:
                        i1 = idx1[0]
                        d2 = (ts-ts[i1]).astype("timedelta64[ns]").astype("int64")
                        i2 = np.searchsorted(d2, H24, side="left")
                        if i2 < len(g): st[i2:] = 2
                g["status"] = st.astype("int8"); return g
            dup = dup.groupby(["lat","lon"], group_keys=False, sort=False).apply(assign)
            df.loc[dup.index, "status"] = dup["status"].astype("int8")

    # 추정치 빈 컬럼
    df["추정치"] = ""
    # 최종 컬럼 순서
    df = df[["head","branch","line","direction","freq","lat","lon","status","time","추정치"]]
    return df

# 테이블 생성 
def ensure_table_roadkill_info(engine, table="roadkill_info"):
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        head        VARCHAR(100) NOT NULL,
        branch      VARCHAR(100) NOT NULL,
        line        VARCHAR(120) NOT NULL,
        direction   VARCHAR(50)  NOT NULL,
        freq        INT UNSIGNED NOT NULL,
        lat         DOUBLE NOT NULL,
        lon         DOUBLE NOT NULL,
        status      TINYINT NOT NULL COMMENT '0=발견,1=재발견,2=죽음',
        time        DATETIME NOT NULL,
        `추정치`       VARCHAR(200) NULL,
        PRIMARY KEY (lat, lon, status, time),
        INDEX idx_ts (time),
        INDEX idx_head (head),
        INDEX idx_branch (branch),
        INDEX idx_line (line)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


# 한 row씩 적재
def stream_rows(df, engine, table="roadkill_info", sleep_sec=1.0):
    sql = text(f"""
        INSERT IGNORE INTO {table}
        (head, branch, line, direction, freq, lat, lon, status, time, `추정치`)
        VALUES (:head, :branch, :line, :direction, :freq, :lat, :lon, :status, :time, :추정치)
    """)
    df2 = df.copy()
    df2["time"] = pd.to_datetime(df2["time"], errors="coerce")  # 안전하게만

    for i, r in enumerate(df2.itertuples(index=False), 1):
        params = {
            "head": r.head, "branch": r.branch, "line": r.line, "direction": r.direction,
            "freq": int(r.freq), "lat": float(r.lat), "lon": float(r.lon),
            "status": int(r.status), "time": pd.Timestamp(r.time).to_pydatetime(),
            "추정치": getattr(r, "추정치", ""),
        }
        with engine.begin() as conn:
            conn.execute(sql, params)
        time.sleep(sleep_sec)


df = make_roadkill_info("C:\githome\hipython_rep\whynot2nd_dashboard\src\database\한국도로공사_로드킬 데이터 정보_20250501.csv", encoding="cp949")
engine = create_engine("mysql+pymysql://root:1234@localhost/roadkill_db?charset=utf8", pool_pre_ping=True)

# 테이블 생성 실행 함수
ensure_table_roadkill_info(engine, table="roadkill_info")
        
stream_rows(df, engine, table="roadkill_info", sleep_sec=0.5)