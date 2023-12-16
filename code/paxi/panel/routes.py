from flask_login import login_required
from flask import url_for, render_template, redirect, flash ,request
from flask_login import current_user, logout_user, login_user

from paxi.panel import panel
from paxi.panel.forms import LoginForm
from paxi.panel.model import User

from paxi.method import passwords

@panel.route('/')
@login_required
def paxi_panel():
    return render_template('home_paxi.html')


@panel.route('/login/', methods=['POST', 'GET'])
def paxi_login():
    print('\n\n\n login login login')
    if current_user.is_authenticated:
        flash('نمی توان موقعی که login هستین دوباره login کنید', 'danger')
        return redirect(url_for('panel.paxi_panel'))
    print('befor form\n\n\n\n\n')
    form = LoginForm()
    print('after form\n\n\n\n\n')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and passwords.check_pass(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            flash('ورود با موفقیت', 'success')
            return redirect(next_page if next_page else url_for('paxi_panel'))
        else:
            flash('اطلاعات وارد شده درست نمی باشد', 'danger')
    return render_template('login.html', form=form)


@panel.route('/logout/')
@login_required
def paxi_logout():
    logout_user()
    flash('خروج با موفقیت انجام شد', 'success')
    return redirect(url_for('panel.paxi_login'))
