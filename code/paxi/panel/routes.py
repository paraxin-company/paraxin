from flask_login import login_required
from flask import url_for, render_template, redirect, flash ,request
from flask_login import current_user, logout_user, login_user

# paxi panel importing
from paxi.panel import panel
from paxi.panel.forms import LoginForm, WeblogForm, WeblogFormEdit
from paxi.panel.model import User

# paxi importing
from paxi import folder_upload, db
from paxi.method import passwords
from paxi.model import Weblog
from paxi.method import files, comma

import os

@panel.route('/')
@login_required
def paxi_panel():
    return render_template('home_paxi.html')


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

