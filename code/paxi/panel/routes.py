from flask import url_for, render_template, redirect, flash ,request, abort
from flask_login import current_user, logout_user, login_user, login_required
import os

# paxi panel importing
from paxi.panel import panel
from paxi.panel.forms import LoginForm, WeblogForm, WeblogFormEdit, ProfileForm
from paxi.panel.model import User, Verify

# paxi importing
from paxi import folder_upload, db
from paxi.model import Weblog
from paxi.method import files, comma, operation, verify_pro, passwords

@panel.route('/')
@login_required
def paxi_panel():
    return render_template('paxi_home.html')


@panel.route('/login/', methods=['POST', 'GET'])
def paxi_login():
    if current_user.is_authenticated:
        flash('نمی توان موقعی که login هستین دوباره login کنید', 'danger')
        return redirect(url_for('panel.paxi_panel'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and passwords.check_pass(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            flash('ورود با موفقیت', 'success')
            return redirect(next_page if next_page else url_for('panel.paxi_panel'))
        else:
            flash('اطلاعات وارد شده درست نمی باشد', 'danger')
    return render_template('login.html', form=form)


@panel.route('/logout/')
@login_required
def paxi_logout():
    logout_user()
    flash('خروج با موفقیت انجام شد', 'success')
    return redirect(url_for('panel.paxi_login'))


@panel.route('/weblog/', methods=['POST', 'GET'])
@login_required
def paxi_weblog():
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search')

    if search:
        all_weblog = Weblog.query.filter(Weblog.keyword.contains(search)+Weblog.title.contains(search)).paginate(page=page, per_page=15)
    else:
        all_weblog = Weblog.query.paginate(page=page, per_page=15)
    return render_template('weblog/weblog.html', data=all_weblog, search_text=search)


@panel.route('/weblog/add/', methods=['POST', 'GET'])
@login_required
def paxi_add_weblog():
    weblog_form = WeblogForm()
    if weblog_form.validate_on_submit():
        try:
            the_file = request.files['baner']
            
            if files.is_valid(the_file.filename):
                # save image in the path
                baner_path = os.path.join(folder_upload, 'weblog', files.rename_name(the_file.filename))
                the_file.save(baner_path)

                new_baner_path = files.get_url(baner_path, 'weblog')

                add_weblog = Weblog(
                    title = weblog_form.title.data,
                    content = weblog_form.content.data,
                    keyword = comma.save(weblog_form.keyword.data),
                    baner = str(new_baner_path)
                )

                # add new record
                db.session.add(add_weblog)
                db.session.commit()

                flash('وبلاگ جدید به درستی اضافه شد', 'success')
                return redirect(url_for('panel.paxi_weblog'))
            else:
                flash(f'فرمت فایل مورد قبول نیست ({the_file.filename})', 'danger')
                return redirect(url_for('panel.paxi_weblog'))
        except:
            flash('برای اضافه کردن وبلاگ جدید مشکلی پیش آمده است', 'danger')
            return redirect(url_for('panel.paxi_weblog'))
    return render_template('weblog/add.html', form=weblog_form)


@panel.route('/weblog/delete/<int:weblog_id>/', methods=['POST'])
@login_required
def paxi_delete_weblog(weblog_id):
    try:
        current_weblog = Weblog.query.get_or_404(int(weblog_id))
        
        # get old file for delete
        old_file = current_weblog.baner
        
        # delete record in table
        db.session.delete(current_weblog)
        db.session.commit()

        # try to delete file
        result = files.delete_file(old_file)
        if result == True:
            flash(f'فایل با موفقیت پاک شد ({current_weblog.baner})', 'success')
        else:
            flash(f'برای پاک کردن فایل مشکلی پیش آمده است ({current_weblog.baner})', 'danger')

        flash(f'وبلاگ با موفقیت حذف شد (id={current_weblog.id})','success')
        return redirect(url_for('panel.paxi_weblog'))
    except:
        flash(f'برای حذف کردن وبلاگ مشکلی پیش آمده است (id={current_weblog.id})','danger')
        return redirect(url_for('panel.paxi_weblog'))


@panel.route('/weblog/edit/<int:weblog_id>/', methods=['POST', 'GET'])
@login_required
def paxi_edit_weblog(weblog_id):
    current_weblog = Weblog.query.get_or_404(int(weblog_id))
    weblog_form = WeblogFormEdit()

    if weblog_form.validate_on_submit():
        # set new data into the record
        try:
            if weblog_form.baner.data:
                if files.is_valid(weblog_form.baner.data.filename):
                    the_file = request.files['baner']

                    # save image in the path
                    baner_path = os.path.join(folder_upload, 'weblog', files.rename_name(the_file.filename))
                    the_file.save(baner_path)

                    # get the old url for delete that
                    old_file = current_weblog.baner

                    current_weblog.baner = files.get_url(baner_path, 'weblog')

                    result = files.delete_file(old_file)
                    if result == True:
                        flash(f'فایل با موفقیت پاک شد ({old_file})', 'success')
                    else:
                        flash(f'برای پاک کردن فایل مشکلی پیش آمده است ({old_file})', 'danger')
                else:
                    flash(f'فرمت فایل مورد قبول نیست ({weblog_form.baner.data.filename})', 'danger')
                    return redirect(url_for('panel.paxi_edit_weblog', weblog_id=current_weblog.id))
            else:
                current_weblog.baner = current_weblog.baner

            current_weblog.title = weblog_form.title.data
            current_weblog.content = weblog_form.content.data
            current_weblog.keyword = comma.save(weblog_form.keyword.data)

            # save changes into the table
            db.session.commit()

            flash(f'اطلاعات وبلاگ با موفقیت تغییر کرد (id={current_weblog.id})', 'success')
            return redirect(url_for('panel.paxi_weblog'))
        except:
            flash(f'برای آبدیت کردن وبلاگ مشکلی پیش آمده است (id={current_weblog.id})', 'danger')
            return redirect(url_for('panel.paxi_edit_weblog', weblog_id=current_weblog.id))

    # set data in current_weblog
    weblog_form.title.data = current_weblog.title
    weblog_form.content.data = current_weblog.content
    weblog_form.keyword.data = comma.show(current_weblog.keyword)

    return render_template('weblog/edit.html', form=weblog_form, baner=current_weblog.baner)


@panel.route('/change/password/')
@login_required
def change_pass():
    if current_user.verify.startswith('1'):

        # send email for change password
        title = 'تغییر گذرواژه حساب شما در پاراکسین'
        message = 'amir mahdi joon'
        send_change_pass_email = operation.Send(destination=current_user.email, message=message, title=title)
        send_change_pass_email.as_email()

        if send_change_pass_email.response == True:
            flash('ایمیلی برای تغییر دادن پسورد حساب شما با موفقیت ارسال شد', 'success')
        else:
            flash('پروسه ارسال ایمیل جهت تغییر دادن گذرواژه با مشکل مواجه شده است', 'danger')
        return redirect(url_for('panel.profile'))        
    else:
        flash('ابتدا باید ایمیل خودتون رو تایید کنید', 'danger')
        return redirect(url_for('panel.profile'))


@panel.route('/change/info/', methods=['POST'])
@login_required
def change_info():
    if request.method == 'POST':
        try:
            if request.form.get('new_email'):
                if current_user.email != request.form.get('new_email'):
                    current_user.email = request.form.get('new_email')
                    current_user.verify = '0'+current_user.verify[1]

                    flash('با موفقیت ایمیل شما تغییر کرد','success')
            elif request.form.get('new_phone'):
                if current_user.phone != request.form.get('new_phone'):
                    current_user.phone = request.form.get('new_phone')
                    current_user.verify = current_user.verify[0]+'0'

                    flash('با موفقیت شماره‌ی تلفن شما تغییر کرد','success')
            # save changes
            db.session.commit()
        except:
            flash('برای تغییر اطلاعات حساب شما مشکلی پیش آمده است','danger')
        return redirect(url_for('panel.profile'))


@panel.route('/profile/', methods=['POST', 'GET'])
@login_required
def profile():
    profile_form = ProfileForm()

    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data

        # save changes
        db.session.commit()
        flash('اطلاعات با موفقیت تغییر کرد', 'success')
        return redirect(url_for('panel.profile'))
    return render_template('profile.html', form=profile_form)


@panel.route('/profile/baner/', methods=['POST'])
@login_required
def change_profile_baner():
    the_file = request.files['profile_baner']
    
    if files.is_valid(the_file.filename):
        # save new profile image
        profile_path = os.path.join(folder_upload, 'panel', files.rename_name(the_file.filename))
        the_file.save(profile_path)

        # delete old profile image
        result = files.delete_file(current_user.profile)
        if result == True:
            flash(f'فایل {current_user.profile} با موفقیت پاک شد', 'success')
        else:
            flash(f'نتونستیم فایل {current_user.profile} رو پاک کنیم', 'danger')

        current_user.profile = files.get_url(profile_path, 'panel')

        # save changes
        db.session.commit()
        flash('تصویر پروفایل شما با موفقیت عوض شد', 'success')
    else:
        flash(f'فرمت فایل مورد قبول نیست ({the_file.filename})', 'danger')
    return redirect(url_for('panel.profile'))


@panel.route('/verify/<string:verify_type>/<string:value>/', methods=['POST', 'GET'])
@login_required
def verify_account(verify_type,value):
    if request.method == 'POST':
        try:
            tocken_user = request.form.get('verify_tocken').strip()

            # get verify code in tabel
            if verify_type == 'phone':
                tocken_tabel = Verify.query.filter_by(item=current_user.phone).order_by(Verify.time.desc()).first()
            else:
                tocken_tabel = Verify.query.filter_by(item=current_user.email).order_by(Verify.time.desc()).first()

            # check verify code is true or no
            if str(tocken_user) == str(tocken_tabel.tocken) and tocken_tabel.item == value:
                if verify_pro.check_not_expire(tocken_tabel.time):
                    if verify_type == 'email':
                        current_user.verify = '1'+current_user.verify[1]
                    else:
                        current_user.verify = current_user.verify = current_user.verify[0]+'1'

                    # update verify for user
                    db.session.commit()

                    flash(f'با موفقیت {verify_type} شما تایید شد.','success')
                    return redirect(url_for('panel.profile'))
                else:
                    flash('کد تایید منقضی شده است','danger')
            else:
                flash('کد تایید اشتباه وارد شده است','danger')
        except:
            flash(f'برای تایید {verify_type} شما مشکلی پیش آمده است', 'danger')
            return redirect(url_for('panel.profile'))
    elif verify_type == 'email' or verify_type == 'phone':
        if verify_type == 'email':
            if current_user.email == value:
                if current_user.verify.startswith('0'):
                    result = verify_pro.email(value)
                    if result == True:
                        flash('پیامی حاوی کد تایید با موفقیت برای شما ارسال شد.', 'success')
                    else:
                        flash(result, 'danger')
                else:
                    flash('شما یک بار حساب ایمیل خودتون رو تایید کرده اید. دوبار نمی توانید اینکار ور بکنید.', 'danger')
                    return redirect(url_for('panel.profile'))
            else:
                flash('ایمیل وارد شده برای شما نیست', 'danger')
                return redirect(url_for('panel.profile'))
        else:
            if current_user.phone == value:
                if current_user.verify.endswith('0'):
                    result = verify_pro.phone(value)
                    if result == True:
                        flash('پیامی حاوی کد تایید با موفقیت برای شما ارسال شد.', 'success')
                    else:
                        flash(result, 'danger')
                else:
                    flash('شما یک بار شماره‌ی همراه خودتون رو تایید کرده اید. دوبار نمی توانید اینکار ور بکنید.', 'danger')
                    return redirect(url_for('panel.profile'))
            else:
                flash('شماره‌ی همراه وارد شده برای شما نیست', 'danger')
                return redirect(url_for('panel.profile'))
    else:
        abort(404)
    return render_template('verify.html', verify_type=verify_type, value=value)
