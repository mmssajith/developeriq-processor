from flask import Flask, jsonify
from sqlalchemy import create_engine, \
    Table, \
    Column, \
    MetaData, \
    Integer, \
    String, \
    JSON, \
    ForeignKey, \
    DateTime, \
    text
import os
from datetime import datetime

app = Flask(__name__)

db_uri = os.environ["DB_URI"]
engine = create_engine(db_uri, echo=True)
metadata = MetaData()

# Define Tables
github_event = Table(
    "github_events",
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('payload', JSON),
)

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
    Column('created_at', DateTime,
           default=datetime.now()),
)

push = Table(
    'push',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('developer_id', ForeignKey('developer.id'), nullable=False),
    Column('repo', String, nullable=False),
    Column('commits_count', Integer, nullable=False),
    Column('created_at', DateTime,
           default=datetime.now()),
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
    Column('files_modified',
           Integer, nullable=False),
    Column('created_at', DateTime,
           default=datetime.now()),
)
metadata.create_all(engine)


@app.route("/pr-created", methods=['GET'])
def pr_created_per_month():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM PULL_REQUESTS;")
        ).all()

    response = [{"developer": get_developer_name(int(row[1])), "repo": row[2],
                 "created_date": row[3]} for row in result]
    return jsonify(response)


@app.route("/push-data", methods=['GET'])
def commits_count_per_push():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM push;")
        ).all()

    response = [{"developer": get_developer_name(int(row[1])), "repo": row[2],
                 "commits_count": row[3], "created_at": row[4]} for row in result]
    return jsonify(response)


@app.route("/commits-data", methods=['GET'])
def file_changes_per_commit():
    with engine.connect() as conn:
        result = conn.execute(
            text("select * from commits;")
        ).fetchall()

    response = [{"developer": get_developer_name(int(row[1])), "push_id": row[2],
                 "repo": row[3], "files_added": row[4], "files_removed": row[5], "files_modified": row[6], "created_at": row[7]} for row in result]
    return jsonify(response)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "analytics service is healthy"})


def get_developer_name(developer_id):
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT username FROM developer WHERE id={developer_id};")
        ).scalar()

    return result


if __name__ == '__main__':
    app.run(debug=True)
