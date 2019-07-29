from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:Thinks08!@localhost:3306/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Buttz'

class Blog_Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String (120))
    blog_post =  db.Column(db.String (120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, text, user):
        self.title = title
        self.blog_post = text
        self.user = user 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blogs =  db.relationship('Blog_Post', backref='user')
    User_name = db.Column(db.String (30))
    User_email = db.Column (db.String (120))
    User_password = db.Column (db.String (30))

    def __init__(self, User_name, User_email, user_password):
        self.User_name = User_name
        self.User_email = User_email
        self.User_password = user_password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog','home']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route ('/signup', methods= ['POST', 'GET'])
def user_signup(): 
    if request.method == 'POST':
        correct_email= request.form['email']
        correct_username = request.form['username']
        correct_password = request.form['password']
        verified_password = request.form['verify']
        username_error = ""
        password_error = ""
        if correct_username == "" or len(correct_username) <3 or len(correct_username) >20: 
            username_error = "Please input a username between 3 and 20 characters"
        if " " in correct_username: 
            username_error = "Please input a username without spaces in between"
        if correct_password != verified_password:
            password_error="Passwords do not match"
        if username_error != "" or password_error != "":
            return redirect("/signup?password_error={}&username_error={}&correct_email={}&correct_username={}".format(password_error, username_error, correct_email, correct_username))
        existing_user = User.query.filter_by(User_name=correct_username).first()
        if not existing_user:
            new_user = User(correct_username, correct_email, correct_password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = correct_username
            return redirect('/')
    if request.args.get('username_error'):
        username_error = request.args.get('username_error')
    else: 
        username_error = ''
    if request.args.get('password_error'):
        password_error = request.args.get('password_error')
    else: 
        password_error= ''
    if request.args.get('correct_username'):
        correct_username=request.args.get('correct_username')
    else: 
        correct_username=''
    if  request.args.get('correct_email'):
        correct_email= request.args.get('correct_email')
    else: 
        correct_email=''
    return render_template('signup.html', error=username_error, password_error=password_error, username=correct_username, email=correct_email)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        User_name = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(User_name=User_name).first()
        if user and user.User_password == password:
            session['user'] = User_name
            flash("Logged in")
            return redirect('/new_post')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')
@app.route('/blog', methods= ['GET'])
def blog():
    posts = Blog_Post.query.all()
    if request.args.get('id'):
        post_id = request.args.get('id')
        individual_post = Blog_Post.query.get(post_id)
        return render_template('singlepost.html', title={}, post=individual_post)
    return render_template('index.html', posts=posts)

@app.route('/new_post', methods = ['GET', 'POST'])
def new_post():
    if request.method == 'POST' :
        post_title = request.form['title']
        blog_post = request.form['blog post']
        User_name = session['user']
        user = User.query.filter_by(User_name=User_name).first()
        user_error = ""
        if post_title == user_error or blog_post == user_error:
            return render_template('new_post.html',title = "New Post", user_error = "please input text into approriate fields", blog_title = post_title, blog_post= blog_post)
        new_blog_post = Blog_Post(post_title, blog_post, user)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect ('/blog?id={0}'.format(new_blog_post.id)) 
    return render_template('new_post.html',title = "New Post")

@app.route('/', methods=['GET'])
def home(): 
    users = User.query.all()
    if request.args.get('id'):
        user_id = request.args.get('id')
        user = User.query.get(user_id)
        return render_template('index.html', title={}, posts=user.blogs)
    return render_template('users.html', users=users)
    


@app.route('/logout')
def logout():
    del session['user']
    return redirect('/')

if __name__ == '__main__':
    app.run()

