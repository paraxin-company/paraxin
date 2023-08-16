from flask import Flask, render_template, url_for

app = Flask(__name__)

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

@app.route('/web-design')
def site_design():
    return render_template('web-design.html')

@app.route('/logo-design')
def logo_design():
    return render_template('logo-design.html')

@app.route('/qr-code')
def qrcode():
    return render_template('qr-code.html')

@app.route('/fap-builder')
def fap():
    return render_template('fap-builder.html')

if __name__ == "__main__":
    app.run()