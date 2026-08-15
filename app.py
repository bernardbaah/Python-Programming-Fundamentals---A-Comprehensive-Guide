from flask import Flask, send_file
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

@app.route('/download/pdf')
def download_pdf():
    return send_file(
        'book_data/Python_Fundamentals_Interior.pdf',
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Python_Fundamentals_Interior.pdf'
    )

@app.route('/download/docx')
def download_docx():
    return send_file(
        'book_data/Python_Fundamentals_Interior.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name='Python_Fundamentals_Interior.docx'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
