from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('viewer.html')

@app.route('/pdf')
def pdf():
    return send_file(
        'book_data/Python_Fundamentals_Interior.pdf',
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

ANSWER_KEY_PATH = 'book_data/Python_Fundamentals_Answer_Key.pdf'

@app.route('/download/answers')
def download_answers():
    if not os.path.exists(ANSWER_KEY_PATH):
        # Rebuild from the committed answer JSONs if the PDF is absent
        import subprocess
        subprocess.run(
            ['python', '.agents/scripts/build_answer_key.py'],
            check=True
        )
    return send_file(
        ANSWER_KEY_PATH,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Python_Fundamentals_Answer_Key.pdf'
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
