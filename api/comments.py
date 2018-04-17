from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List

comment_blueprint = Blueprint('comment_blueprint', __name__)

class NewCommentForm(FlaskForm):
    content = StringField('Add a new comment.', validators=[InputRequired(), Length(max=200)])

@login_required
@list_blueprint.route('/<user_name>/list/<list_id>/comments', methods = ['POST', 'GET'])
def show_comments(user_name,list_id):
    user=User.query.filter(User.username==user_name).first()
    list=List.query.get(list_id)
    comments = Comment.query.filter(Comment.list_id = list_id).all()
    form=NewCommentForm()
    if form.validate_on_submit():
        new_comment = Comment(user_id=user.id,content=form.content.data,list_id=list_id)
        db.session.add(new_comment)
        db.session.commit()
        comments = Comment.query.filter(Comment.list_id = list_id).all()
        return redirect render_template('show_comments.html', user=user, list=list,form=form,comments=comments)
    return render_template('show_comments.html', user=user, list=list,form=form,comments=comments)

