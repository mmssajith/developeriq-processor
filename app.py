from flask import Flask, jsonify
from sqlalchemy import create_engine, \
    Table, \
    Column, \
    MetaData, \
    Integer, \
    String, \
    ForeignKey, \
    DateTime, \
    text
import os
from datetime import datetime

app = Flask(__name__)

db_uri = os.environ["DB_URI"]
engine = create_engine(db_uri, echo=True)
metadata = MetaData()

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
    Column('number', Integer, nullable=False, unique=True),
    Column('developer_id', ForeignKey('developer.id'), nullable=False),
    Column('repo', String, nullable=False),
    Column('created_at', DateTime,
           default=datetime.now()),
)


pr_process = Table(
    'pr_process',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('pr_number', ForeignKey('pull_requests.number'), nullable=False),
    Column('repo', String, nullable=False),
    Column('created_at', DateTime),
    Column('closed_at', DateTime),
    Column('merged_at', DateTime),
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


@app.route('/commits-per-push', methods=['GET'])
def get_developers_data():
    developers_data = []

    # Query commits and group by push_id and developer_id
    with engine.connect() as connection:
        query = '''
            SELECT
                developer_id,
                push_id,
                SUM(files_added) AS total_files_added,
                SUM(files_removed) AS total_files_removed,
                SUM(files_modified) AS total_files_modified
            FROM commits
            GROUP BY developer_id, push_id;
        '''
        result = connection.execute(text(query)).fetchall()

        current_developer = None
        current_pushes = []

        for row in result:
            developer_id, push_id, files_added, files_removed, files_modified = row

            if developer_id != current_developer:
                # Start a new developer entry
                if current_developer is not None:
                    developers_data.append({
                        'developer': get_developer_name(developer_id),
                        'developer_id': current_developer,
                        'pushes': current_pushes
                    })

                current_developer = developer_id
                current_pushes = []

            current_pushes.append({
                'push_id': push_id,
                'files_added': files_added,
                'files_removed': files_removed,
                'files_modified': files_modified,
            })

        # Add the last developer entry
        if current_developer is not None:
            developers_data.append({
                'developer': get_developer_name(developer_id),
                'developer_id': current_developer,
                'pushes': current_pushes
            })

    return jsonify(developers_data)


@app.route('/pr-timing', methods=['GET'])
def get_pull_requests_data():
    query = '''
        SELECT pr_process.*, pull_requests.developer_id
        FROM pr_process
        JOIN pull_requests ON pull_requests.number = pr_process.pr_number;
    '''

    with engine.connect() as connection:
        result = connection.execute(text(query)).fetchall()

        pull_requests_data = []
        for row in result:
            pull_request_entry = {
                'id': row.id,
                'pr_number': row.pr_number,
                'developer_name': get_developer_name(row.developer_id),
                'developer_id': row.developer_id,
                'repo': row.repo,
                'created_at': row.created_at.isoformat(),
                'closed_at': row.closed_at.isoformat(),
                'merged_at': row.merged_at.isoformat(),
            }
            pull_requests_data.append(pull_request_entry)

    return jsonify(pull_requests_data)


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
