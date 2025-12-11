import logging
from typing import List
import psycopg
from pymongo import MongoClient
from config.logging import setup_logging
from config.settings import POSTGRES_DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, MONGO_URL, MONGO_DB_NAME

logger = setup_logging()


def get_db_connection():
    try:
        conn = psycopg.connect(
            dbname=POSTGRES_DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise


def get_mongo_connection():
    try:
        client = MongoClient(MONGO_URL)
        db = client[MONGO_DB_NAME]
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


def fetch_mcqs(language: str, difficulty: str) -> List[dict]:
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT mcq_id, question_text, option_a, option_b, option_c, option_d, correct_answer
        FROM mcq_questions
        WHERE language = %s AND difficulty_level = %s
        ORDER BY mcq_id;
    """
    cur.execute(query, (language, difficulty))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    mcqs = []
    for row in rows:
        mcqs.append({
            "mcq_id": row[0],
            "question_text": row[1],
            "option_a": row[2],
            "option_b": row[3],
            "option_c": row[4],
            "option_d": row[5],
            "correct_answer": row[6],
        })
    return mcqs


def fetch_coding_questions(title: str | None, labels: List[str] | None, difficulty: str | None) -> List[dict]:
    db = get_mongo_connection()
    collection = db["coding_questions"]

    query = {"$or": []}

    if title:
        query["$or"].append({"title": {"$regex": title, "$options": "i"}})

    if labels and len(labels) > 0:
        query["$or"].append({"labels": {"$in": labels}})

    if difficulty:
        query["$or"].append({"difficulty": difficulty})

    if len(query["$or"]) == 0:
        query = {}

    results = list(collection.find(query, {"_id": 0}))
    return results
