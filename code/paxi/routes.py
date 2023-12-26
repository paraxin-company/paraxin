from flask import render_template, abort, redirect, flash, request
from paxi.model import Category, Weblog, Sample, Ticket
from paxi.forms import ContactForm
from paxi import app, db

from paxi.panel import panel
app.register_blueprint(panel)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about/')
def about():
   return render_template('about.html')


@app.route('/contact/', methods=['POST', 'GET'])
def contact():
    contact_form = ContactForm()
    
    # if contact_form.validate_on_submit():
    if request.method == 'POST':
        try:
            add_new_contact = Ticket(
                text = contact_form.text.data,
                title = contact_form.title.data,
                email = contact_form.email.data,
                phone = contact_form.phone.data,
                name = contact_form.name.data,
                department = contact_form.department.data,
                relation = contact_form.relation.data
            )

            # commit a contact text in database
            db.session.add(add_new_contact)
            db.session.commit()

            flash(f'پیام شما با موفقیت ارسال شد (شماره تیکت {add_new_contact.id})', 'success')
            return redirect('/contact#send-mail')
        except:
            flash('پیام شما ارسال نشد .', 'danger')
            return redirect('/contact#send-mail')

    return render_template('contact.html', form=contact_form)


@app.route('/weblog/')
def weblog():
    page = request.args.get('page', default=1, type=int)
    web_log = Weblog.query.order_by(Weblog.date).paginate(page=page, per_page=12)
    return render_template('weblog.html', info=web_log)


@app.route('/weblog/detail/<int:id>/')
def weblog_detail(id):
    web_log = Weblog.query.get_or_404(id)
    related = Weblog.query.limit(6)
    return render_template('detail.html', data=web_log, related=related)


@app.route('/work-sample/', methods=['GET'])
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


@app.route('/work-sample/detail/<int:id>/', methods=['GET'])
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


@app.route('/web-design/')
def site_design():
    category = Category.query.filter_by(text='طراحی سایت').first()
    tops = Sample.query.filter_by(category_id=category.id).limit(6)
    return render_template('services/web-design.html', tops=tops)


@app.route('/logo-design/')
def logo_design():
    return render_template('services/logo-design.html')


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('base/404.html'), 404


@app.errorhandler(405)
def not_allowed(error):
    return render_template('base/405.html'), 405