from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from paxi.model import User, Category, Weblog, Sample
from paxi.forms import LoginForm, WeblogForm, SampleForm
from paxi.method import passwords, files, comma
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
    category = Category.query.get(1)
    tops = Sample.query.filter_by(category_id=category.id).limit(6)
    return render_template('services/web-design.html', tops=tops)


@app.route('/logo-design')
def logo_design():
    return render_template('services/logo-design.html')


@app.route('/qr-code')
def qrcode():
    return render_template('services/qr-code.html')


@app.route('/fap-builder')
def fap():
    return render_template('services/fap-builder.html')


@app.route('/paxi')
@login_required
def paxi_panel():
    return render_template('panel/home.html')


@app.route('/paxi/login', methods=['POST', 'GET'])
def paxi_login():
    if current_user.is_authenticated:
        flash('شما به حساب خود وارد هستین نمی توانید دوباره به حساب خود وارد شوید', 'danger')
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
    all_weblog = Weblog.query.all()
    return render_template('panel/weblog/weblog.html', data=all_weblog)


@app.route('/paxi/weblog/add', methods=['POST', 'GET'])
@login_required
def paxi_add_weblog():
    weblog_form = WeblogForm()
    if weblog_form.validate_on_submit():
        # try:
            the_file = request.files['baner']
            
            if files.is_valid(the_file.filename):
                baner_path = os.path.join(folder_upload, 'weblog', files.change_name(the_file.filename))

                # save image in the path
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

            flash('رکورد جدید به درستی اضافه شد', 'success')
            return redirect(url_for('paxi_weblog'))
        # except:
        #     flash('برای اضافه کردن رکورد جدید مشکلی پیش آمده است', 'danger')
        #     return redirect(url_for('paxi_weblog'))
    
    return render_template('panel/weblog/add.html', form=weblog_form)


@app.route('/paxi/weblog/delete/<int:weblog_id>', methods=['GET', 'POST'])
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
            flash(f'فایل {current_weblog.baner} با موفقیت پاک شد', 'success')
        else:
            flash(f'نتونستیم فایل {current_weblog.baner} رو پاک کنیم', 'danger')

        flash('با موفقیت حذف شد','success')
        return redirect(url_for('paxi_weblog'))
    except:
        flash(f'برای حذف کردن رکورد {current_weblog.id} مشکلی پیش آمده است','danger')
        return redirect(url_for('paxi_weblog'))


@app.route('/paxi/weblog/edit/<int:weblog_id>', methods=['POST', 'GET'])
@login_required
def paxi_edit_weblog(weblog_id):
    current_weblog = Weblog.query.get_or_404(int(weblog_id))
    weblog_form = WeblogForm()

    if weblog_form.validate_on_submit():
        # set new data into the record
        try:
            if files.is_valid(weblog_form.baner.data.filename):
                the_file = request.files['baner']
                baner_path = os.path.join(folder_upload, 'weblog', files.change_name(the_file.filename))

                if files.rename_undo(os.path.basename(current_weblog.baner)) != weblog_form.baner.data.filename:
                    # save image in the path
                    the_file.save(baner_path)

                    # get the old url for delete that
                    old_file = current_weblog.baner

                    new_baner_path = files.get_url(baner_path, 'weblog')
                    current_weblog.baner = new_baner_path

                    result = files.delete_file(old_file)
                    if result == True:
                        flash(f'فایل {current_weblog.baner} با موفقیت پاک شد', 'success')
                    else:
                        flash(f'نتونستیم فایل {current_weblog.baner} رو پاک کنیم', 'danger')
                
                else:
                    current_weblog.baner = current_weblog.baner

                current_weblog.title = weblog_form.title.data
                current_weblog.content = weblog_form.content.data
                current_weblog.keyword = comma.save(weblog_form.keyword.data)

                # save changes into the table
                db.session.commit()

                flash(f'اطلاعات مربوط به رکورد ( {current_weblog.id}) با موفقیت تغییر کرد', 'success')
                return redirect(url_for('paxi_weblog'))
            
            else:
                flash('فرمت وارد شده مورد قبول نمی باشد', 'danger')
                return redirect(url_for('paxi_edit_weblog', weblog_id=current_weblog.id))
        except:
            flash(f'برای آبدیت کردن رکورد ( {current_weblog.id}) مشکلی پیش آمده است', 'danger')
            return redirect(url_for('paxi_edit_weblog', weblog_id=current_weblog.id))
    
    # set data in current_weblog
    weblog_form.title.data = current_weblog.title
    weblog_form.content.data = current_weblog.content
    weblog_form.keyword.data = comma.show(current_weblog.keyword)

    return render_template('/panel/weblog/edit.html', form=weblog_form, baner=current_weblog.baner)


@app.route('/paxi/work-sample')
@login_required
def paxi_work_sample():
    samples = Sample.query.all()
    return render_template('panel/work-sample/work-sample.html', data=samples)


@app.route('/paxi/work-sample/edit/<int:sample_id>', methods=['GET', 'POST'])
@login_required
def paxi_work_sample_edit(sample_id):
    sample_info = Sample.query.get_or_404(int(sample_id))
    sample_form = SampleForm()
    

    if sample_form.validate_on_submit():
        Sample(
            title = sample_form.title.data,
            content = sample_form.content.data,
            baner = '/test/',
            album = '/test/ablbum',
            keyword = comma.save(sample_form.keyword.data)
        )

        # save changes
        db.session.commit()
        
        flash('تغییرات با موفقیت اعمال شد', 'success')
        return redirect(url_for('paxi_work_sample'))
        
    sample_form.title.data = sample_info.title
    sample_form.content.data = sample_info.content
    sample_form.baner.data = sample_info.baner
    sample_form.album.data = sample_info.album
    sample_form.keyword.data = comma.show(sample_info.keyword)

    return render_template('panel/work-sample/edit.html', form=sample_form)


@app.route('/paxi/work-sample/category')
@login_required
def paxi_work_sample_category():
    cats = Category.query.all()   
    return render_template('panel/work-sample/category.html', data=cats)


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html'), 404