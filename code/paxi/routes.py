from paxi import app
from flask import render_template, url_for

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/weblog')
def weblog():
    return render_template('weblog.html')

@app.route('/sample')
def work_sample():
    return render_template('sample.html')