import sqlite3
import json
import os
import numpy as np
from pathlib import Path

DB_PATH = Path(__file__).parent / "skills.db"

# Lazy-loaded embedding model
_model = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL DEFAULT '1.0.0',
            description TEXT NOT NULL,
            author TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',
            skill_md_content TEXT NOT NULL,
            permissions TEXT NOT NULL DEFAULT '{}',
            price_per_use REAL,
            license_fee REAL,
            risk_score INTEGER,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            action TEXT NOT NULL,
            proof_hash TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            skill_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            total_amount REAL NOT NULL,
            developer_share REAL NOT NULL,
            platform_share REAL NOT NULL,
            proof_hash TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
            skill_id, name, description, tags,
            content='skills',
            content_rowid='rowid'
        );
    """)
    conn.commit()
    conn.close()


def generate_embedding(text: str) -> bytes:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tobytes()


def cosine_similarity(a: bytes, b: bytes) -> float:
    vec_a = np.frombuffer(a, dtype=np.float32)
    vec_b = np.frombuffer(b, dtype=np.float32)
    return float(np.dot(vec_a, vec_b))


def insert_skill(skill: dict) -> str:
    conn = get_connection()
    embed_text = f"{skill['name']} {skill['description']} {' '.join(skill.get('tags', []))}"
    embedding = generate_embedding(embed_text)

    conn.execute(
        """INSERT OR REPLACE INTO skills
           (skill_id, name, version, description, author, tags, skill_md_content,
            permissions, price_per_use, license_fee, risk_score, embedding)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            skill["skill_id"],
            skill["name"],
            skill.get("version", "1.0.0"),
            skill["description"],
            skill["author"],
            json.dumps(skill.get("tags", [])),
            skill["skill_md_content"],
            json.dumps(skill.get("permissions", {})),
            skill.get("price_per_use"),
            skill.get("license_fee"),
            skill.get("risk_score"),
            embedding,
        ),
    )
    # Update FTS index
    conn.execute(
        "INSERT OR REPLACE INTO skills_fts (skill_id, name, description, tags) VALUES (?, ?, ?, ?)",
        (skill["skill_id"], skill["name"], skill["description"], json.dumps(skill.get("tags", []))),
    )
    conn.commit()
    conn.close()
    return skill["skill_id"]


def semantic_search(query: str, offset: int = 0, limit: int = 12) -> tuple[list[dict], int]:
    query_embedding = generate_embedding(query)
    conn = get_connection()
    rows = conn.execute("SELECT * FROM skills WHERE embedding IS NOT NULL").fetchall()
    conn.close()

    results = []
    for row in rows:
        similarity = cosine_similarity(query_embedding, row["embedding"])
        results.append({
            "skill_id": row["skill_id"],
            "name": row["name"],
            "description": row["description"],
            "confidence": round(max(0.0, min(1.0, (similarity + 1) / 2)), 4),
            "risk_score": row["risk_score"],
            "price_per_use": row["price_per_use"],
            "author": row["author"],
            "tags": json.loads(row["tags"]),
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    total_count = len(results)
    sliced_results = results[offset : offset + limit]
    return sliced_results, total_count


def get_total_skills_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as count FROM skills").fetchone()["count"]
    conn.close()
    return count


def get_skill(skill_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "skill_id": row["skill_id"],
        "name": row["name"],
        "version": row["version"],
        "description": row["description"],
        "author": row["author"],
        "tags": json.loads(row["tags"]),
        "skill_md_content": row["skill_md_content"],
        "permissions": json.loads(row["permissions"]),
        "price_per_use": row["price_per_use"],
        "license_fee": row["license_fee"],
        "risk_score": row["risk_score"],
    }


def list_skills(offset: int = 0, limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM skills ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [
        {
            "skill_id": row["skill_id"],
            "name": row["name"],
            "version": row["version"],
            "description": row["description"],
            "author": row["author"],
            "tags": json.loads(row["tags"]),
            "price_per_use": row["price_per_use"],
            "risk_score": row["risk_score"],
        }
        for row in rows
    ]


def log_usage(skill_id: str, agent_id: str, action: str, proof_hash: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO usage_log (skill_id, agent_id, action, proof_hash) VALUES (?, ?, ?, ?)",
        (skill_id, agent_id, action, proof_hash),
    )
    conn.commit()
    conn.close()


def log_transaction(txn: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO transactions
           (transaction_id, skill_id, agent_id, total_amount, developer_share, platform_share, proof_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            txn["transaction_id"],
            txn["skill_id"],
            txn["agent_id"],
            txn["total_amount"],
            txn["developer_share"],
            txn["platform_share"],
            txn["proof_hash"],
        ),
    )
    conn.commit()
    conn.close()


def get_usage_stats(skill_id: str) -> dict:
    conn = get_connection()
    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM usage_log WHERE skill_id = ?", (skill_id,)
    ).fetchone()["cnt"]
    unique_agents = conn.execute(
        "SELECT COUNT(DISTINCT agent_id) as cnt FROM usage_log WHERE skill_id = ?", (skill_id,)
    ).fetchone()["cnt"]
    revenue = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM transactions WHERE skill_id = ?",
        (skill_id,),
    ).fetchone()["total"]
    conn.close()
    return {
        "total_uses": total,
        "unique_agents": unique_agents,
        "total_revenue": revenue,
    }


def get_developer_stats(author: str) -> dict:
    conn = get_connection()
    skills = conn.execute(
        "SELECT skill_id, name, risk_score, price_per_use, created_at FROM skills WHERE author = ? ORDER BY created_at DESC",
        (author,),
    ).fetchall()

    skill_ids = [s["skill_id"] for s in skills]
    total_uses = 0
    unique_agents_set: set[str] = set()
    total_revenue = 0.0
    skill_stats = []

    for sid in skill_ids:
        uses = conn.execute(
            "SELECT COUNT(*) as cnt FROM usage_log WHERE skill_id = ?", (sid,)
        ).fetchone()["cnt"]
        agents = conn.execute(
            "SELECT DISTINCT agent_id FROM usage_log WHERE skill_id = ?", (sid,)
        ).fetchall()
        rev = conn.execute(
            "SELECT COALESCE(SUM(developer_share), 0) as total FROM transactions WHERE skill_id = ?",
            (sid,),
        ).fetchone()["total"]
        total_uses += uses
        for row in agents:
            unique_agents_set.add(row["agent_id"])
        total_revenue += rev

    for s in skills:
        sid = s["skill_id"]
        uses = conn.execute(
            "SELECT COUNT(*) as cnt FROM usage_log WHERE skill_id = ?", (sid,)
        ).fetchone()["cnt"]
        rev = conn.execute(
            "SELECT COALESCE(SUM(developer_share), 0) as total FROM transactions WHERE skill_id = ?",
            (sid,),
        ).fetchone()["total"]
        skill_stats.append({
            "skill_id": sid,
            "name": s["name"],
            "risk_score": s["risk_score"],
            "price_per_use": s["price_per_use"],
            "total_uses": uses,
            "developer_revenue": rev,
        })

    conn.close()
    return {
        "author": author,
        "skill_count": len(skills),
        "total_uses": total_uses,
        "unique_agents": len(unique_agents_set),
        "total_revenue": round(total_revenue, 4),  # type: ignore[no-matching-overload]
        "skills": skill_stats,
    }
