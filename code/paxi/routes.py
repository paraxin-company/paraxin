from flask import render_template, url_for, redirect, abort, request
from paxi.model import User, Category, Weblog, Sample
from paxi import app

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
    try:
        web_log = Weblog.query.order_by(Weblog.date).all()
        return render_template('weblog.html', info=web_log)
    except:
        abort(404)

@app.route('/weblog/<int:id>')
def weblog_info(id):
    try:
        web_log = Weblog.query.get(id)
        return redirect(render_template('home.html', info=web_log))
    except:
        abort(404)

@app.route('/sample', methods=['GET', 'POST'])
def work_sample():
    try:
        sample = Sample.query.all()
        category = Category.query.all()
        return render_template('sample.html', sample=sample, category=category)
    except:
        abort(404)

@app.route('/sample/<int:id>')
def detail(id):
    try:
        sample = Sample.query.get(id)
        return f'amir this is simpel text {sample}'
    except:
        abort(404)

@app.route('/web-design')
def site_design():
    return render_template('services/web-design.html')

@app.route('/logo-design')
def logo_design():
    return render_template('services/logo-design.html')

@app.route('/qr-code')
def qrcode():
    return render_template('services/qr-code.html')

@app.route('/fap-builder')
def fap():
    return render_template('services/fap-builder.html')

@app.route('/<inputs>')
def page_not_found(inputs):
    abort(404)

@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html')