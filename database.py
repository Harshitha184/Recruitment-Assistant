import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from pgvector.psycopg2 import register_vector
from pgvector import Vector

load_dotenv()
def get_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
        sslmode="require"
    )

    register_vector(conn)
    return conn



def _safe(val):
    if val is None:
        return ""

    try:
        return str(val)
    except Exception:
        return ""


def save_candidates(results):

    conn = get_conn()
    cur = conn.cursor()

    now = datetime.now()

    for r in results:

        embedding = None

        if "Embedding" in r and r["Embedding"] is not None:
            embedding = Vector(r["Embedding"])

        cur.execute(
            """
            INSERT INTO candidates
            (
                name,
                email,
                file_name,
                score,
                status,
                matched_skills,
                missing_skills,
                screened_at,
                embedding
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s,%s,%s
            )
            """,
            (
                r["Candidate"],
                r["Email"],
                r["File"],
                r["Score"],
                r["Status"],
                r["Matched Skills"],
                r["Missing Skills"],
                now,
                embedding
            )
        )

    conn.commit()
    cur.close()
    conn.close()


def save_email(
    candidate_name,
    candidate_email,
    status,
    email_body
):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO emails
        (
            candidate_name,
            candidate_email,
            status,
            email_body,
            sent_at
        )
        VALUES
        (
            %s,%s,%s,%s,%s
        )
        """,
        (
            candidate_name,
            candidate_email,
            status,
            email_body,
            datetime.now()
        )
    )

    conn.commit()
    cur.close()
    conn.close()


def get_all_candidates():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            name,
            email,
            file_name,
            score,
            status,
            matched_skills,
            missing_skills,
            screened_at
        FROM candidates
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        (
            _safe(r[0]),
            _safe(r[1]),
            _safe(r[2]),
            r[3],
            _safe(r[4]),
            _safe(r[5]),
            _safe(r[6]),
            _safe(r[7])
        )
        for r in rows
    ]


def get_all_emails():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            candidate_name,
            candidate_email,
            status,
            email_body,
            sent_at
        FROM emails
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        (
            _safe(r[0]),
            _safe(r[1]),
            _safe(r[2]),
            _safe(r[3]),
            _safe(r[4])
        )
        for r in rows
    ]


def clear_db():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM emails")
    cur.execute("DELETE FROM candidates")

    conn.commit()

    cur.close()
    conn.close()