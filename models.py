from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy, event
from sqlalchemy import engine
from sqlalchemy.schema import Sequence


db = SQLAlchemy()

# noinspection PyUnusedLocal
@event.listens_for(engine.Engine, 'connect')
def __set_sqlite_pragma(db_conn, conn_record):
    cursor = db_conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    cursor.close()


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.user_id')),
)

shared_lists = db.Table('shared_lists',
    db.Column('list_id', db.Integer, db.ForeignKey('list.list_id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
)

# class Friends(Base):
#     __tablename__ = 'friends'
#     user_id = db.Column(db.Integer, ForeignKey('user.user_id'), primary_key=True)
#     friend_id = db.Column(db.Integer, ForeignKey('user.user_id'), primary_key=True)
#     request_status = db.Column(db.Boolean, unique=False, default=False)
#     user = db.relationship('User', foreign_keys='Friend.user_id')
#     friend = db.relationship('User', foreign_keys='Friend.friend_id')
'''
class Friends(Base):
    __tablename__ = 'friends'
    user_id = db.Column(db.Integer, ForeignKey('user.user_id'), primary_key=True)
    friend_id = db.Column(db.Integer, ForeignKey('user.user_id'), primary_key=True)
    request_status = db.Column(db.Boolean, unique=False, default=False)
'''

class User(UserMixin, db.Model):
    # __tablename__ = 'user-table'
    id = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.String(64), unique=True, nullable=False)
    name = db.Column('name', db.String(120), unique=False, nullable=False)
    dob = db.Column('date_of_birth', db.DateTime, nullable=False)
    email = db.Column('email', db.String(64), nullable=False, unique=True)
    registration_time = db.Column('registration_time',db.DateTime, default=datetime.utcnow)
    password_hash = db.Column('password_hash',db.String(80), nullable=False)
    remember_me = db.Column('remember_me', db.Boolean, unique=False, default=False)
    profile_picture_filename = db.Column('profile_picture_filename', db.String(64))
    profile_picture_url = db.Column('profile_picture_url', db.String(64))

    followed = db.relationship(
    'User', secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id == id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    tasks = db.relationship(
        'Task',
        backref=db.backref('user', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    lists = db.relationship(
        'List',
        backref=db.backref('user', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    comments = db.relationship(
        'Comment',
        backref= db.backref('user', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    notif = db.relationship(
        'Notif',
        backref= db.backref('user', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )


    def set_password(self, secret):
        self.password = generate_password_hash(secret)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def all_followed(self):
        return self.followed.all()

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def return_all_lists(self):
        return self.all_lists.all()

    def serialize(self):
        return {
            'user_id' : self.id,
            'username' : self.username,
            'name' : self.name,
            'dob' : self.dob,
            'registration_time' : self.registration_time,
            'password_hash' : self.password_hash,
            'remember_me' : self.remember_me
        }

    def __repr__(self):
        return self.serialize().__repr__()


dependent_tasks = db.Table('dependent_tasks',
    db.Column('task_id', db.Integer, db.ForeignKey('task-table.task_id')),
    db.Column('dependent_id', db.Integer, db.ForeignKey('task-table.task_id')),
)

class Task(db.Model):

    __tablename__ = 'task-table'

    id = db.Column('task_id', db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column('create_time', db.DateTime,
                            default=datetime.utcnow)
    start_time = db.Column('start_time', db.DateTime)
    end_time = db.Column('end_time', db.DateTime)
    deadline = db.Column('deadline', db.DateTime, nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey(
        'user', ondelete='CASCADE'), nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.String(200))
    status = db.Column('status', db.Enum(
        *['Pending', 'Ongoing', 'Completed']), nullable=False, default='Pending')
    priority = db.Column('priority', db.Boolean, nullable=False, default=False)
    relpriority =  db.Column('relpriority', db.Integer)
    incentive = db.Column('incentive', db.String(200))
    consequences = db.Column('consequences', db.String(200))
    list_id = db.Column('list_id', db.Integer, db.ForeignKey('list.list_id', ondelete='CASCADE'), nullable=False)

    dependent = db.relationship(
    'Task', secondary=dependent_tasks,
    primaryjoin=(dependent_tasks.c.task_id == id),
    secondaryjoin=(dependent_tasks.c.dependent_id == id),
    backref=db.backref('dependent_tasks', lazy='dynamic'), lazy='dynamic')


    def set_relpriority(self):
        self.relpriority = self.id
        db.session.commit()

    def all_dependent(self):
        return self.dependent.all()

    def dependent_on(self, task):
        if not self.is_dependent(task):
            self.dependent.append(task)

    def remove_dependency(self, task):
        if self.is_dependent(task):
            self.dependent.remove(task)

    def is_dependent(self, task):
        return self.dependent.filter(
            dependent_tasks.c.dependent_id == task.id).count() > 0

    def serialize(self):
        return {
            'task_id': self.id,
            'create_time': self.create_time,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'deadline': self.deadline,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'incentive': self.incentive,
            'consequences': self.consequences
        }

    def __repr__(self):
        return self.serialize().__repr__()

class List(db.Model):
    id = db.Column('list_id', db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column('create_time', db.DateTime, default=datetime.utcnow)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user', ondelete='CASCADE'), nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.String(200))
    tasks = db.relationship(
            'Task',
            backref= db.backref('list', lazy='joined'),
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    comments = db.relationship(
            'Comment',
            backref= db.backref('list', lazy='joined'),
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    
    all_users = db.relationship(
    'User', secondary=shared_lists,
    backref=db.backref('all_lists', lazy='dynamic'), lazy='dynamic')

    def return_all_users(self):
        return self.all_users.all()

    def is_user(self,cur_user):
        return self.all_users.filter(User.id == cur_user.id).count() > 0

    def add_user(self,cur_user):
        if not self.is_user(cur_user):
            self.all_users.append(cur_user)

    def remove_user(self, user):
        if self.is_user(user):
            self.all_users.remove(user)

class Comment(db.Model):
    id = db.Column('comment_id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user', ondelete='CASCADE'), nullable=False)
    list_id = db.Column('list_id', db.Integer, db.ForeignKey('list.list_id', ondelete='CASCADE'), nullable=False)
    content = db.Column('content', db.String(200))
    create_time = db.Column('create_time', db.DateTime, default=datetime.utcnow)
    username = db.Column('username', db.String(64))

    def serialize(self):
        return {
            'username' : self.username,
            'comment_id': self.id,
            'create_time': self.create_time,
            'user_id': self.user_id,
            'content': self.content,
            'list_id' : self.list_id
        }

    def __repr__(self):
        return self.serialize().__repr__()

class Message(db.Model):
    id = db.Column('message_id', db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column('create_time', db.DateTime, default=datetime.utcnow)
    from_username = db.Column('from_username', db.String(64))
    to_username = db.Column('to_username',db.String(64))
    content = db.Column('content',db.String(200))

    def serialize(self):
        return {
            'from_username' : self.from_username,
            'to_username' : self.to_username,
            'message_id': self.id,
            'create_time': self.create_time,
            'content': self.content,
        }

    def __repr__(self):
        return self.serialize().__repr__()

class Notif(db.Model):
    id = db.Column('notif_id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user', ondelete='CASCADE'), nullable=False)
    content = db.Column('content', db.String(200))
    create_time = db.Column('create_time', db.DateTime, default=datetime.utcnow)
    typ = db.Column('typ', db.Enum(
        *['Accepted', 'Deadline', 'Shared','Request','Message']))
    status = db.Column('status', db.Enum(
        *['Read', 'Unread']), default = 'Unread')
    second_username = db.Column('second_username', db.String(200))

        

    def serialize(self):
        return {
            'notif_id': self.id,
            'create_time': self.create_time,
            'status' : self.status,
            'user_id': self.user_id,
            'content': self.content,
            'typ' : self.typ,
            'second_username' : self.second_username
    }

    def __repr__(self):
        return self.serialize().__repr__()

    
# shared_lists = db.Table('shared_lists',
#     db.Column('list_id', db.Integer, db.ForeignKey('list.list_id')),
#     db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
# )

class Connection(db.Model):

    __tablename__ = "connections"

    connection_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(100), nullable=False)

    # When both columns have a relationship with the same table, need to specify how
    # to handle multiple join paths in the square brackets of foreign_keys per below
    user_a = db.relationship("User", foreign_keys=[user_a_id], backref=db.backref("sent_connections"))
    user_b = db.relationship("User", foreign_keys=[user_b_id], backref=db.backref("received_connections"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Connection connection_id=%s user_a_id=%s user_b_id=%s status=%s>" % (self.connection_id,
                                                                                      self.user_a_id,
                                                                                      self.user_b_id,
                                                                                      self.status)
