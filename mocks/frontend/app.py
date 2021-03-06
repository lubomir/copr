#!/usr/bin/env python3

import flask
import json
import sys

app = flask.Flask(__name__)

task_dict = {}
distgit_responses = []


# http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/tmp/<path:path>')
def serve_uploaded_file(path):
    return app.send_static_file(path)


@app.route('/backend/importing/')
def dist_git_importing_queue():
    response = {'builds': list(task_dict.values())}
    return flask.jsonify(response)


@app.route('/backend/import-completed/', methods=['POST', 'PUT'])
def dist_git_upload_completed():
    distgit_responses.append(flask.request.json)
    task_dict.pop(flask.request.json['task_id'])
    if not task_dict:
        dump_responses()
        shutdown_server()
    return flask.jsonify({'updated': True})


def dump_responses():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'data/distgit-responses.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(distgit_responses))


def load_import_tasks():
    with open('data/import-tasks.json', 'r') as f:
        task_queue = json.loads(f.read())
        for task in task_queue:
            task_dict[task['task_id']] = task


if __name__ == '__main__':
    load_import_tasks()
    app.run()
