from flask import Flask, request, Response, json
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from werkzeug.wsgi import FileWrapper

import util
from util import Model

app = Flask(__name__)

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e,
    })
    response.content_type = "application/json"
    return response

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/gettext', methods=['POST'])
def gettext():
    # check if the post request has the file part
    if 'file' not in request.files:
        return Response("No file part", status=400)
    file = request.files['file']
    # empty file without a filename.
    if file.filename == '':
        return Response('No selected file', status=400)
    if file and util.allowed_file(file.filename):
        args: Model = Model()
        args.filename = secure_filename(file.filename)
        args.stream = file.stream.read()
        args.password = request.args.get('password')
        args.pages = request.args.get('pages', '1-N')
        args.convert_white = request.args.get('convert_white', False)
        args.noligatures = request.args.get('noligatures', False)
        args.extra_spaces = request.args.get('extra_spaces', False)
        args.mode = request.args.get('mode', 'layout')
        args.grid = request.args.get('grid', 2)
        args.fontsize = request.args.get('fontsize', 3)
        args.noformfeed = request.args.get('noformfeed', False)
        args.skip_empty = request.args.get('skip_empty', False)

        text_bytes_io = util.gettext(args)
        return Response(FileWrapper(text_bytes_io), mimetype="text/plain", direct_passthrough=True)
    return Response("File not allowed", status=400)

if __name__ == '__main__':
    app.run()
