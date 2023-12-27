from flask import url_for, render_template, redirect, flash ,request, abort
from flask_login import current_user, logout_user, login_user, login_required
import os

# paxi panel importing
from paxi.panel import panel
from paxi.panel.forms import LoginForm, WeblogForm, WeblogFormEdit, ProfileForm, SampleForm, SampleFormEdit, CategoryForm
from paxi.panel.model import User, Verify

# paxi importing
from paxi import folder_upload, db
from paxi.model import Weblog, Sample, Category, Ticket, Answer
from paxi.method import files, comma, operation, verify_pro, passwords, folder

@panel.route('/')
@login_required
def paxi_panel():
    return render_template('home_panel.html')


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
    if current_user.roll[1] != '0':
        page = request.args.get('page', default=1, type=int)
        search = request.args.get('search')

        if search:
            all_weblog = Weblog.query.filter(Weblog.keyword.contains(search)+Weblog.title.contains(search)).paginate(page=page, per_page=15)
        else:
            all_weblog = Weblog.query.paginate(page=page, per_page=15)
        return render_template('weblog/weblog.html', data=all_weblog, search_text=search, roll=current_user.roll[1])
    else:abort(405)

@panel.route('/weblog/add/', methods=['POST', 'GET'])
@login_required
def paxi_add_weblog():
    if current_user.roll[1] == '1' or current_user.roll[1] == '4' or current_user.roll[1] == '9':
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
    else:abort(405)


@panel.route('/weblog/delete/<int:weblog_id>/', methods=['POST'])
@login_required
def paxi_delete_weblog(weblog_id):
    if current_user.roll[1] == '3' or current_user.roll[1] == '9':
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
    else:abort(405)


@panel.route('/weblog/edit/<int:weblog_id>/', methods=['POST', 'GET'])
@login_required
def paxi_edit_weblog(weblog_id):
    if current_user.roll[1] == '2' or current_user.roll[1] == '4' or current_user.roll[1] == '9' :
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
    else:abort(405)


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


@panel.route('/work-sample/')
@login_required
def paxi_work_sample():
    if  current_user.roll[2] != '0':
        page = request.args.get('page', default=1, type=int)
        search = request.args.get('search')

        if search:
            samples = Sample.query.filter(Sample.title.contains(search)+Sample.keyword.contains(search)).paginate(page=page, per_page=15)
        else:
            samples = Sample.query.paginate(page=page, per_page=15)
        return render_template('work-sample/work-sample.html', data=samples, search_text=search, roll=current_user.roll[2])
    else:abort(405)


@panel.route('/work-sample/add/', methods=['GET', 'POST'])
@login_required
def paxi_add_work_sample():
    if current_user.roll[2] == '1' or current_user.roll[2] == '4' or current_user.roll[2] == '9':
        try:
            sample_form = SampleForm()
            all_category = Category.query.order_by(Category.id).all()

            if sample_form.validate_on_submit():
                baner_image = request.files['baner']
                album = request.files.getlist("album")
                
                if files.is_valid(baner_image.filename):
                    new_category = passwords.small(sample_form.category.data)

                    baner_path = os.path.join(os.path.join(folder_upload, 'sample'), new_category, files.rename_name(baner_image.filename))

                    if len(album) > 1:
                        album_path_host = []

                        # Iterate for each file in the files List, and Save them
                        if files.is_valid_album(album):
                            for image in album:
                                # save album image in host
                                album_path = os.path.join(os.path.join(folder_upload, 'sample'), new_category, files.rename_name(image.filename))
                                album_path_host.append(files.get_url(album_path, os.path.join('sample', new_category)))
                                image.save(album_path)
                        else:
                            flash(f'فرمت فایل یا فایل های album نادرست می باشد', 'danger')
                            return redirect(url_for('panel.paxi_work_sample'))
                        
                        if len(album_path_host) == 1:
                            album_result = album_path_host[0]+'|,|'
                        else:
                            album_result = '|,|'.join(album_path_host)
                    else:
                        album_result = ''
                    
                    # save baner in host
                    baner_image.save(baner_path)

                    # find baner path
                    new_baner_path = files.get_url(baner_path, os.path.join('sample', new_category))
        
                    # find category info
                    for item in all_category:
                        if sample_form.category.data in str(item):
                            current_cat = item

                    add_sample = Sample(
                        title = sample_form.title.data,
                        content = sample_form.content.data,
                        keyword = comma.save(sample_form.keyword.data),
                        baner = str(new_baner_path),
                        album = album_result,
                        cat = current_cat
                    )

                    # save new record
                    db.session.add(add_sample)
                    db.session.commit()

                    flash('رکورد جدید به درستی اضافه شد', 'success')
                    return redirect(url_for('panel.paxi_work_sample'))
                else:
                    flash(f'فرمت فایل مورد قبول نیست ({baner_image.filename})', 'danger')
                    return redirect(url_for('panel.paxi_work_sample'))
            return render_template('work-sample/add.html', form=sample_form, cats=all_category)
        except:
            flash('برای اضافه کردن رکورد جدید مشکلی پیش آمده است', 'danger')
            return redirect(url_for('panel.paxi_work_sample'))
    else:abort(405)


@panel.route('/work-sample/delete/<int:sample_id>/', methods=['POST'])
@login_required
def paxi_delete_work_sample(sample_id):
    if current_user.roll[2] == '3' or current_user.roll[2] == '9':
        try:
            current_sample = Sample.query.get_or_404(int(sample_id))

            baner = current_sample.baner
            album = current_sample.album

            result = files.delete_file(baner)
            if result == True:
                flash(f'فایل با موفقیت پاک شد ({current_sample.baner})', 'success')
            else:
                flash(f'برای پاک کردن فایل مشکلی پیش آمده است ({current_sample.baner})', 'danger')

            if '|,|' in album:
                images_in_album = album.split('|,|')
                for image in images_in_album:
                    if len(image) != 0:
                        state_image = files.delete_file(image)
                        if state_image == True:
                            flash(f'فایل با موفقیت پاک شد ({image})', 'success')
                        else:
                            flash(f'برای پاک کردن فایل مشکلی پیش آمده است ({image})', 'danger')

            # delete record
            db.session.delete(current_sample)
            db.session.commit()

            flash(f'نمونه کار با موفقیت حذف شد (id={current_sample.id})','success')
            return redirect(url_for('panel.paxi_work_sample'))
        except:
            flash(f'برای حذف کردن نمونه کار مشکلی پیش آمده است (id={current_sample.id})','danger')
            return redirect(url_for('panel.paxi_work_sample'))
    else:abort(405)


@panel.route('/work-sample/edit/<int:sample_id>/', methods=['GET', 'POST'])
@login_required
def paxi_edit_work_sample(sample_id):
    if current_user.roll[2] == '2' or current_user.roll[2] == '4' or current_user.roll[2] == '9':
        current_sample = Sample.query.get_or_404(int(sample_id))
        all_category = Category.query.all()
        sample_form = SampleFormEdit()

        if sample_form.validate_on_submit():
            try:
                baner_image = request.files['baner']
                album = request.files.getlist('album')

                new_category = passwords.small(sample_form.category.data)

                if sample_form.baner.data:
                    if files.is_valid(baner_image.filename):
                        # save new baner in host
                        baner_path = os.path.join(os.path.join(folder_upload, 'sample'), new_category, files.rename_name(baner_image.filename))
                        baner_image.save(baner_path)

                        # find baner path
                        new_baner_path = files.get_url(baner_path, os.path.join('sample', new_category))

                        # delete old baner
                        result = files.delete_file(current_sample.baner)
                        if result == True:
                            flash(f'بنر قبلی با موفقیت پاک شد ({current_sample.baner})', 'success')
                        else:
                            flash(f'برای حذف کردن بنر قبلی مشکلی پیش آمده است ({current_sample.baner})', 'danger')

                    else:
                        flash(f'فرمت فایل مورد قبول نیست ({baner_image.filename})', 'danger')
                        return redirect(url_for('panel.paxi_work_sample'))
                else:
                    # find baner path
                    if new_category == passwords.small(current_sample.cat.text):
                        new_baner_path = current_sample.baner
                    else:
                        # copy baner in new folder
                        new_baner_path = operation.copy_to_new_category(current_sample.baner, passwords.small(current_sample.cat.text), passwords.small(sample_form.category.data))
                        
                        # delete old baner
                        result = files.delete_file(current_sample.baner)
                        if result == True:
                            flash(f'بنر قبلی با موفقیت پاک شد ({current_sample.baner})', 'success')
                        else:
                            flash(f'برای حذف کردن بنر قبلی مشکلی پیش آمده است ({current_sample.baner})', 'danger')

                # check album is set or no
                if len(album) == 1 and new_category == passwords.small(current_sample.cat.text):
                    album_result = current_sample.album
                else:
                    album_path_host = []
                    # Iterate for each file in the files List, and Save them
                    for image in album:
                        if image:
                            if files.is_valid(image.filename):
                                # save album image in host
                                album_path = os.path.join(os.path.join(folder_upload, 'sample'), new_category, files.rename_name(image.filename))
                                album_path_host.append(files.get_url(album_path, os.path.join('sample', new_category)))
                                image.save(album_path)
                            else:
                                flash(f'فرمت فایل مورد قبول نیست ({image.filename})', 'danger')
                                return redirect(url_for('panel.paxi_work_sample'))
                    if len(album_path_host) == 1:
                        album_result = album_path_host[0]+'|,|'
                    else:
                        album_result = '|,|'.join(album_path_host)
                    
                    # delete old album from host
                    images_in_album = current_sample.album.split('|,|')
                    for image in images_in_album:
                        if len(image) != 0:
                            state_image = files.delete_file(image)
                            if state_image == True:
                                flash(f'فایل با موفقیت پاک شد ({image})', 'success')
                            else:
                                flash(f'برای پاک کردن فایل مشکلی پیش آمده است ({image})', 'danger')

                # find category info
                for item in all_category:
                    if sample_form.category.data in str(item):
                        current_cat = item
                        break

                current_sample.title = sample_form.title.data,
                current_sample.content = sample_form.content.data,
                current_sample.baner = new_baner_path,
                current_sample.album = album_result,
                current_sample.keyword = comma.save(sample_form.keyword.data),
                current_sample.cat = current_cat

                # save changes
                db.session.commit()

                flash(f'تغییرات با موفقیت اعمال شد (id={sample_id})', 'success')
                return redirect(url_for('panel.paxi_work_sample'))
            except:
                flash(f'برای تغییر نمونه کار مشکلی پیش آمده است (id={sample_id})','danger')
                return redirect(url_for('panel.paxi_work_sample'))

        category_list = []
        for category in all_category:
            category_list.append(category.text)

        sample_form.title.data = current_sample.title
        sample_form.content.data = current_sample.content
        sample_form.category.data = current_sample.cat.text
        sample_form.baner.data = current_sample.baner
        sample_form.keyword.data = comma.show(current_sample.keyword)

        return render_template('work-sample/edit.html', form=sample_form, baner=current_sample.baner, album=current_sample.album, choice=category_list)
    else:abort(405)

@panel.route('/work-sample/category/')
@login_required
def paxi_work_sample_category():
    if current_user.roll[3] != '0':
        page = request.args.get('page', default=1, type=int)

        cats = Category.query.order_by(Category.id).paginate(page=page, per_page=15)
        cat_form = CategoryForm()
        return render_template('work-sample/category.html', data=cats, form=cat_form, roll=current_user.roll[3])
    else:abort(405)


@panel.route('/work-sample/category/edit/<int:cat_id>/', methods=['POST'])
@login_required
def paxi_edit_work_sample_category(cat_id):
    if current_user.roll[3] == '2' or current_user.roll[3] == '9':
        try:
            current_category = Category.query.get_or_404(int(cat_id))
            all_sample_match = Sample.query.filter_by(cat=current_category).all()
            cat_form = CategoryForm()

            new_category_text = passwords.small(cat_form.text.data)
            result_folder_name = folder.check_name(cat_form.text.data)
            if result_folder_name == True:
                if current_category.text != cat_form.text.data:
                    if Category.query.filter_by(text=new_category_text).first() == None:
                        if folder.rename('sample', passwords.small(current_category.text), new_category_text):
                            # change sample directory
                            if all_sample_match:
                                for item in all_sample_match:
                                    item.baner = item.baner.replace(passwords.small(current_category.text), new_category_text)
                                    item.album = item.album.replace(passwords.small(current_category.text), new_category_text)

                            current_category.text = cat_form.text.data
                            
                            # save changes
                            db.session.commit()

                            flash(f'اطلاعات دسته بندی با موفقیت تغییر کرد (ID={current_category.id})', 'success')
                        else:
                            flash('برای تغییر اسم پوشه در هاست مشکلی پیش آمده است', 'danger')
                    else:
                        flash(f'دسته بندی با نام ({cat_form.text.data}) وجود دارد', 'danger')
                else:
                    flash('اطلاعاتی تغییر نکرده است','danger')
            else:
                flash(result_folder_name, 'danger')
        except:
            flash(f'برای تغییر دسته بندی مشکلی پیش آمده است (ID={current_category.id})', 'danger')
        return redirect(url_for('panel.paxi_work_sample_category'))
    else:abort(405)


@panel.route('/work-sample/category/add/', methods=['POST'])
@login_required
def paxi_add_work_sample_category():
    if current_user.roll[3] == '1' or current_user.roll[3] == '9':
        try:
            cat_form = CategoryForm()
            
            result_folder_name = folder.check_name(cat_form.text.data)
            if result_folder_name == True:
                if Category.query.filter_by(text=cat_form.text.data).first() == None:
                    if folder.create('sample', passwords.small(cat_form.text.data)):
                        add_category = Category(text=cat_form.text.data)

                        # save changes
                        db.session.add(add_category)
                        db.session.commit()
                        flash(f'با موفقیت دسته بندی جدید برای نمونه کار اضافه شد ({cat_form.text.data})', 'success')
                        return redirect(url_for('panel.paxi_work_sample_category'))
                    else:
                        flash('برای اضافه کردن پوشه در هاست مشکلی پیش آمده است', 'danger')
                        return redirect(url_for('panel.paxi_work_sample_category'))
                else:
                    flash(f'چنین دسته بندی وجود دارد ({cat_form.text.data})', 'danger')
                    return redirect(url_for('panel.paxi_work_sample_category'))
            else:
                flash(result_folder_name, 'danger')
                return redirect(url_for('panel.paxi_work_sample_category'))
        except:
            flash(f'برای اضافه کردن دسته بندی نمونه کار جدید مشکلی پیش آمده است', 'danger')
            return redirect(url_for('panel.paxi_work_sample_category'))
    else:abort(405)


@panel.route('/ticket/')
@login_required
def paxi_ticket():
    page = request.args.get('page',type=int, default=1)
    search = request.args.get('search')

    if search:
        all_ticket = Ticket.query.filter(Ticket.id.contains(search)+Ticket.title.contains(search)+Ticket.department.contains(search)).order_by(Ticket.time.desc()).paginate(page=page, per_page=15)
    else:
        all_ticket = Ticket.query.order_by(Ticket.time.desc()).paginate(page=page, per_page=15)

    return render_template('ticket/ticket.html', data=all_ticket, search_text=search)


@panel.route('/ticket/chat/<int:id_ticket>/', methods=['POST', 'GET'])
@login_required
def paxi_answer_ticket(id_ticket):
    find_ticket = Ticket.query.get_or_404(id_ticket)
    find_answers = Answer.query.filter_by(tick=find_ticket).order_by(Answer.time).all()

    if request.method == 'POST':
        try:
            answer_for_ticket = Answer(
                text = request.form.get('answer_input'),
                full_name=current_user.fullname,
                tick=find_ticket
            )

            # save answer for ticket
            db.session.add(answer_for_ticket)
            db.session.commit()

            flash(f'پاسخ شما به تیکت {find_ticket.id} به درستی ارسال شد', 'success')
            return redirect(url_for('panel.paxi_ticket'))
        except:
            flash(f'برای پاسخ دادن به تیکت {find_ticket.id} مشکلی پیش آمده است', 'danger')

    return render_template('ticket/chat.html', data=find_ticket, find_answers=find_answers)

@panel.route('/<path:input>/')
def can_not_find_page(input):
    abort(404)

@panel.errorhandler(405)
def not_allowed(error):
    return render_template('base/405_paxi_panel.html'), 405

@panel.errorhandler(404)
def page_not_found_error(error):
    return render_template('base/404_paxi_panel.html'), 404