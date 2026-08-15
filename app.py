from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('viewer.html')

@app.route('/pdf')
def pdf():
    return send_file(
        'attached_assets/Python_Fundamentals_Updated.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
