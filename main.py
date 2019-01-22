from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from datetime import datetime
from wtforms import  StringField, PasswordField, BooleanField, DateTimeField, SubmitField, FileField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, DataRequired, ValidationError
from wtforms.widgets import TextArea
from time import time
from flask_moment import Moment
from flask_uploads import  UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///businessProf.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"
ACCESS_KEY = 'pk.eyJ1IjoiY2Vld2FpIiwiYSI6ImNqbng3eDcyZDByeXgzcHBnY2w0cGloM2sifQ.NsvAT34SplBxuUvZsvUSKA'
moment = Moment(app)


# DATABASE TABLES
# Business Profile
class BusinessProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brandName = db.Column(db.String(50))
    brandDesc = db.Column(db.String(150))
    address = db.Column(db.String(200))
    hotline = db.Column(db.Integer())
    email = db.Column(db.String(50))
    website = db.Column(db.String(100))
    operatingHours = db.Column(db.String(200))
    image = db.Column(db.String(200))
    post = db.relationship("BusinessPosts", backref="author", lazy="dynamic")


# Business Posts
class BusinessPosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # blogger = current_user
    # bloggerImg = current_user.image_file
    blog = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    blog_id = db.Column(db.Integer, db.ForeignKey('business_profile.id'))
    postImage = db.Column(db.String(200))


# STORE PHOTOS IN DATABASE AND STATIC FOLDER
# BUSINESS GALLERY
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/galleries'
configure_uploads(app, photos)


# WTForms
class BusinessForms(FlaskForm):
    brandName = StringField('Brand Name', validators=[DataRequired()])
    brandDesc = StringField('Brand Description', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    hotline = StringField('Hotline', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    website = StringField('Website', validators=[DataRequired()])
    operatingHours = StringField('Operating Hours', validators=[DataRequired()])
    submit = SubmitField("Create profile!")

    def validate_brandName(self, brandName):
        user = BusinessProfile.query.filter_by(brandName=brandName.data).first()
        if user is not None:
            raise ValidationError('Please use a different Brand Name.')

    def validate_hotline(self, hotline):
        user = BusinessProfile.query.filter_by(hotline=hotline.data).first()
        if user is not None:
            raise ValidationError('Please use a different Hotline.')

    def validate_email(self, email):
        user = BusinessProfile.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different E-Mail.')

    def validate_website(self, website):
        user = BusinessProfile.query.filter_by(website=website.data).first()
        if user is not None:
            raise ValidationError('Please use a different Website.')


class PostStatus(FlaskForm):
    post = TextAreaField('Say something...', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


# APP ROUTES
# REGISTER BUSINESS PAGE
@app.route("/register", methods=["POST", "GET"])
def register():
    form = BusinessForms()
    if form.validate_on_submit() and 'photo' in request.files:
        image = photos.save(request.files["photo"])
        business = BusinessProfile(
            brandName=form.brandName.data,
            brandDesc=form.brandDesc.data,
            address=form.address.data,
            hotline=form.hotline.data,
            email=form.email.data,
            website=form.website.data,
            operatingHours=form.operatingHours.data,
            image=image
        )
        db.session.add(business)
        db.session.commit()
        flash('Successfully created Business profile!')
        return redirect(url_for("businessprof", name=form.brandName.data))
    return render_template("RegisterProfile.html", form=form)


# BUSINESS PROFILE PAGE
@app.route("/profile/<name>", methods=["POST", "GET"])
def businessprof(name):
    business = BusinessProfile.query.filter_by(brandName=name).first()
    form = PostStatus()
    posts = BusinessPosts.query.filter_by(blog_id=business.id).all()
    if form.validate_on_submit():
        image = photos.save(request.files["photo"])
        post1 = BusinessPosts(blog=form.post.data, author=business, postImage=image)  # current_user
        db.session.add(post1)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('businessprof', name=name))
    return render_template("BusinessProf.html", name=business, form=form, posts=posts)


@app.route("/create")
def create():
    db.create_all()
    return "Created"


if __name__ == '__main__':
    app.run(debug=True)






































