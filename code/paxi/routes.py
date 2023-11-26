from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from paxi.model import User, Category, Weblog, Sample
from paxi.forms import LoginForm, WeblogForm, WeblogFormEdit, SampleForm, SampleFormEdit, ProfileForm, CategoryForm
from paxi.method import passwords, files, comma, folder, operation
from paxi import app, db, folder_upload
import os

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
    page = request.args.get('page', default=1, type=int)
    web_log = Weblog.query.order_by(Weblog.date).paginate(page=page, per_page=12)
    return render_template('weblog.html', info=web_log)


@app.route('/weblog/detail/<int:id>')
def weblog_detail(id):
    web_log = Weblog.query.get_or_404(id)
    related = Weblog.query.limit(6)
    return render_template('detail.html', data=web_log, related=related)


@app.route('/work-sample', methods=['GET'])
def work_sample():
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search')

    if search:
        cat_find_by_search = Category.query.filter(Category.text.contains(search)).first()

        if cat_find_by_search:
            sample = Sample.query.filter(Sample.title.contains(search)+Sample.keyword.contains(search)+Sample.category_id.contains(cat_find_by_search.id)).paginate(page=page, per_page=12)
        else:
            sample = Sample.query.filter(Sample.title.contains(search)+Sample.keyword.contains(search)).paginate(page=page, per_page=12)
    else:
        sample = Sample.query.paginate(page=page, per_page=12)

    return render_template('sample.html', sample=sample, search_text=search)


@app.route('/work-sample/detail/<int:id>', methods=['GET'])
def work_sample_detail(id):
    try:
        gallery = False
        sample = Sample.query.get_or_404(id)
        related = Sample.query.filter_by(category_id=sample.category_id).limit(6)
        
        # check album in the colum is full or no (can we show the album or no)
        if '|,|' in sample.album:
            gallery = True
        else:
            gallery = False
    
        return render_template('detail.html', data=sample, related=related, gallery=gallery, sample=True)
    except:
        abort(404)


@app.route('/web-design')
def site_design():
    category = Category.query.filter_by(text='طراحی سایت').first()
    tops = Sample.query.filter_by(category_id=category.id).limit(6)
    return render_template('services/web-design.html', tops=tops)


@app.route('/logo-design')
def logo_design():
    return render_template('services/logo-design.html')


@app.route('/paxi')
@login_required
def paxi_panel():
    return render_template('panel/home.html')


@app.route('/paxi/login', methods=['POST', 'GET'])
def paxi_login():
    if current_user.is_authenticated:
        flash('نمی توان موقعی که login هستین دوباره login کنید', 'danger')
        return redirect(url_for('paxi_panel'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and passwords.check_pass(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            flash('ورود با موفقیت', 'success')
            return redirect(next_page if next_page else url_for('paxi_panel'))
        else:
            flash('اطلاعات وارد شده درست نمی باشد', 'danger')
    return render_template('panel/login.html', form=form)


@app.route('/paxi/logout')
@login_required
def paxi_logout():
    logout_user()
    flash('خروج با موفقیت انجام شد', 'success')
    return redirect(url_for('paxi_login'))


@app.route('/paxi/weblog', methods=['POST', 'GET'])
@login_required
def paxi_weblog():
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search')

    if search:
        all_weblog = Weblog.query.filter(Weblog.keyword.contains(search)+Weblog.title.contains(search)).paginate(page=page, per_page=15)
    else:
        all_weblog = Weblog.query.paginate(page=page, per_page=15)
    return render_template('panel/weblog/weblog.html', data=all_weblog, search_text=search)


@app.route('/paxi/weblog/add', methods=['POST', 'GET'])
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
                return redirect(url_for('paxi_weblog'))
            else:
                flash(f'فرمت فایل مورد قبول نیست ({the_file.filename})', 'danger')
                return redirect(url_for('paxi_weblog'))
        except:
            flash('برای اضافه کردن وبلاگ جدید مشکلی پیش آمده است', 'danger')
            return redirect(url_for('paxi_weblog'))
    return render_template('panel/weblog/add.html', form=weblog_form)


@app.route('/paxi/weblog/delete/<int:weblog_id>', methods=['POST'])
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
        return redirect(url_for('paxi_weblog'))
    except:
        flash(f'برای حذف کردن وبلاگ مشکلی پیش آمده است (id={current_weblog.id})','danger')
        return redirect(url_for('paxi_weblog'))


@app.route('/paxi/weblog/edit/<int:weblog_id>', methods=['POST', 'GET'])
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
                    return redirect(url_for('paxi_edit_weblog', weblog_id=current_weblog.id))
            else:
                current_weblog.baner = current_weblog.baner

            current_weblog.title = weblog_form.title.data
            current_weblog.content = weblog_form.content.data
            current_weblog.keyword = comma.save(weblog_form.keyword.data)

            # save changes into the table
            db.session.commit()

            flash(f'اطلاعات وبلاگ با موفقیت تغییر کرد (id={current_weblog.id})', 'success')
            return redirect(url_for('paxi_weblog'))
        except:
            flash(f'برای آبدیت کردن وبلاگ مشکلی پیش آمده است (id={current_weblog.id})', 'danger')
            return redirect(url_for('paxi_edit_weblog', weblog_id=current_weblog.id))

    # set data in current_weblog
    weblog_form.title.data = current_weblog.title
    weblog_form.content.data = current_weblog.content
    weblog_form.keyword.data = comma.show(current_weblog.keyword)

    return render_template('/panel/weblog/edit.html', form=weblog_form, baner=current_weblog.baner)


@app.route('/paxi/work-sample')
@login_required
def paxi_work_sample():
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search')

    if search:
        samples = Sample.query.filter(Sample.title.contains(search)+Sample.keyword.contains(search)).paginate(page=page, per_page=15)
    else:
        samples = Sample.query.paginate(page=page, per_page=15)
    return render_template('panel/work-sample/work-sample.html', data=samples, search_text=search)


@app.route('/paxi/work-sample/add', methods=['GET', 'POST'])
@login_required
def paxi_add_work_sample():
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
                        return redirect(url_for('paxi_work_sample'))
                    
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
                return redirect(url_for('paxi_work_sample'))
            else:
                flash(f'فرمت فایل مورد قبول نیست ({baner_image.filename})', 'danger')
                return redirect(url_for('paxi_work_sample'))
        return render_template('panel/work-sample/add.html', form=sample_form, cats=all_category)
    except:
        flash('برای اضافه کردن رکورد جدید مشکلی پیش آمده است', 'danger')
        return redirect(url_for('paxi_work_sample'))


@app.route('/paxi/work-sample/delete/<int:sample_id>', methods=['POST'])
@login_required
def paxi_delete_work_sample(sample_id):
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
        return redirect(url_for('paxi_work_sample'))
    except:
        flash(f'برای حذف کردن نمونه کار مشکلی پیش آمده است (id={current_sample.id})','danger')
        return redirect(url_for('paxi_work_sample'))


@app.route('/paxi/work-sample/edit/<int:sample_id>', methods=['GET', 'POST'])
@login_required
def paxi_edit_work_sample(sample_id):
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
                    return redirect(url_for('paxi_work_sample'))
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
                            return redirect(url_for('paxi_work_sample'))
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
            return redirect(url_for('paxi_work_sample'))
        except:
            flash(f'برای تغییر نمونه کار مشکلی پیش آمده است (id={sample_id})','danger')
            return redirect(url_for('paxi_work_sample'))

    category_list = []
    for category in all_category:
        category_list.append(category.text)

    sample_form.title.data = current_sample.title
    sample_form.content.data = current_sample.content
    sample_form.category.data = current_sample.cat.text
    sample_form.baner.data = current_sample.baner
    sample_form.keyword.data = comma.show(current_sample.keyword)

    return render_template('panel/work-sample/edit.html', form=sample_form, baner=current_sample.baner, album=current_sample.album, choice=category_list)


@app.route('/paxi/work-sample/category')
@login_required
def paxi_work_sample_category():
    page = request.args.get('page', default=1, type=int)

    cats = Category.query.order_by(Category.id).paginate(page=page, per_page=15)
    cat_form = CategoryForm()
    return render_template('panel/work-sample/category.html', data=cats, form=cat_form)


@app.route('/paxi/work-sample/category/edit/<int:cat_id>', methods=['POST'])
@login_required
def paxi_edit_work_sample_category(cat_id):
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
    return redirect(url_for('paxi_work_sample_category'))


@app.route('/paxi/work-sample/category/add', methods=['POST'])
@login_required
def paxi_add_work_sample_category():
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
                    return redirect(url_for('paxi_work_sample_category'))
                else:
                    flash('برای اضافه کردن پوشه در هاست مشکلی پیش آمده است', 'danger')
                    return redirect(url_for('paxi_work_sample_category'))
            else:
                flash(f'چنین دسته بندی وجود دارد ({cat_form.text.data})', 'danger')
                return redirect(url_for('paxi_work_sample_category'))
        else:
            flash(result_folder_name, 'danger')
            return redirect(url_for('paxi_work_sample_category'))
    except:
        flash(f'برای اضافه کردن دسته بندی نمونه کار جدید مشکلی پیش آمده است', 'danger')
        return redirect(url_for('paxi_work_sample_category'))


@app.route('/paxi/profile', methods=['POST', 'GET'])
@login_required
def profile():
    profile_form = ProfileForm()

    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.password = passwords.get_hash(profile_form.password.data)

        # save changes
        db.session.commit()
        flash('اطلاعات با موفقیت تغییر کرد', 'success')
        return redirect(url_for('profile'))

    return render_template('panel/profile.html', form=profile_form)


@app.route('/paxi/profile/baner', methods=['POST'])
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
    return redirect(url_for('profile'))


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(405)
def not_allowed(error):
    return render_template('405.html'), 405