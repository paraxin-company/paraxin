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

@app.route('/weblog/detail/<int:id>')
def weblog_detail(id):
    web_log = Weblog.query.get_or_404(id)
    related = Weblog.query.limit(6)
    return render_template('detail.html', data=web_log, related=related)

@app.route('/work-sample', methods=['GET', 'POST'])
def work_sample():
    try:
        sample = Sample.query.all()
        category = Category.query.all()
        print(sample)
        print(category)
        return render_template('sample.html', sample=sample, category=category)
    except:
        abort(404)

@app.route('/work-sample/detail/<int:id>')
def work_sample_detail(id):
    try:
        gallery = False
        sample = Sample.query.get_or_404(id)
        related = Sample.query.filter_by(category_id=sample.category_id).limit(6)
        try:
            # check album in the colum is full or no (can we show the album or no)
            if ',' in sample.album:
                gallery = True
        except:
            gallery = False
        return render_template('detail.html', data=sample, related=related, gallery=gallery, sample=True)
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