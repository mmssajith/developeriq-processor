from flask import Flask, jsonify
from sqlalchemy import create_engine, MetaData, Table, String, Integer, Column, ForeignKey
import os

app = Flask(__name__)

db_uri = os.environ.get(
    "DB_URI", "postgresql://postgres:dEbpMuh1YPXZu21SxR4t@developeriq.cgfn0rdytwyv.ap-southeast-1.rds.amazonaws.com:5432/developeriq?sslmode=require"
)
engine = create_engine(db_uri, echo=True)
metadata = MetaData()

# Define Tables
developer = Table(
    'developer',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String, unique=True),
)

pull_requests = Table(
    'pull_requests',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('developer_id', ForeignKey('developer.id'), nullable=False),
    Column('repo', String, nullable=False),
    Column('pr_date', String, nullable=False),
)

push = Table(
    'push',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('developer_id', ForeignKey('developer.id'), nullable=False),
    Column('repo', String, nullable=False),
    Column('commits_count', Integer, nullable=False),
)

commits = Table(
    'commits',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('developer_id', ForeignKey('developer.id'), nullable=False),
    Column('push_id', ForeignKey('push.id'), nullable=False),
    Column('repo', String, nullable=False),
    Column('files_added', Integer, nullable=False),
    Column('files_removed', Integer, nullable=False),
    Column('files_modified', Integer, nullable=False)
)

metadata.create_all(engine)


@app.route("/pr-created-per-month", methods=['GET'])
def pr_created_per_month():
    with engine.connect() as conn:
        result = conn.execute(
            "SELECT EXTRACT(MONTH FROM TO_DATE(pr_date, 'YYYY-MM-DD')) as month, COUNT(*) as pr_count "
            "FROM pull_requests GROUP BY month ORDER BY month"
        ).fetchall()

    response = [{"month": int(row[0]), "pr_count": row[1]} for row in result]
    return jsonify(response)


@app.route("/commits-count-per-push", methods=['GET'])
def commits_count_per_push():
    with engine.connect() as conn:
        result = conn.execute(
            "SELECT repo, SUM(commits_count) as total_commits FROM push GROUP BY repo"
        ).fetchall()

    response = [{"repo": row[0], "total_commits": row[1]} for row in result]
    return jsonify(response)


@app.route("/file-changes-per-commit", methods=['GET'])
def file_changes_per_commit():
    with engine.connect() as conn:
        result = conn.execute(
            "SELECT repo, SUM(files_added) as total_added, SUM(files_removed) as total_removed, "
            "SUM(files_modified) as total_modified FROM commits GROUP BY repo"
        ).fetchall()

    response = [{"repo": row[0], "total_added": row[1],
                 "total_removed": row[2], "total_modified": row[3]} for row in result]
    return jsonify(response)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "analytics service is healthy"})


if __name__ == '__main__':
    app.run(debug=True)
