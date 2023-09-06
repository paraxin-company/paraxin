from flask import render_template, abort, redirect, url_for, flash
from flask_login import login_user
from paxi.model import User, Category, Weblog, Sample
from paxi.forms import LoginForm
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
    return render_template('detail.html', data=web_log)
    

@app.route('/work-sample', methods=['GET', 'POST'])
def work_sample():
    sample = Sample.query.all()
    category = Category.query.all()
    return render_template('sample.html', sample=sample, category=category)

@app.route('/work-sample/detail/<int:id>')
def work_sample_detail(id):
    sample = Sample.query.get_or_404(id)
    return render_template('detail.html', data=sample)

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

@app.route('/paxi/login', methods=['POST', 'GET'])
def paxi_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and (user.password==form.password.data):
            login_user(user, remember=form.remember.data)
            flash('ورود با موفقیت', 'success')
            return redirect(url_for('paxi_panel'))
        else:
            flash('اطلاعات وارد شده درست نمی باشد', 'danger')
    return render_template('panel/login.html', form=form)

@app.route('/paxi')
def paxi_panel():
    return render_template('panel/paxi.html')

@app.route('/<inputs>')
def page_not_found(inputs):
    abort(404)

@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html')