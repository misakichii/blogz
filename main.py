from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '4zd3gpc4f1d!9d1z'

#BLOG CLASS
class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#connections
#all post - id
#one user (individual) - owner_id


#REQUIRES LOGIN 
#NOTE - will not display css files if static not listed below
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#INDEX - ROUTES TO INDEX.HTML
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

#LOGIN ROUTE
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        #DATABASE BASED VALIDATION OF INFORMATION ENTERED
        #check to see if username and password match what is in database
        user = User.query.filter_by(username=username).first()

        #COMMENTED OUT HASHED PASSWORD CHECK      
        #if user and check_pw_hash(password, user.pw_hash):
            #session['username'] =  username
            #return redirect('/newpost')
                    
        if not user:
            flash("User doesn't exit. Valid username required")
            return render_template('login.html')
            #checking to see if password entered is same the one in the database
        elif user.password != password:
            flash('Username or password incorrect please try again')
            return render_template('login.html')
            #ask how to check for password when its hashed

        #FORM VALIDATION (SAME AS ABOVE WITH NO DB CHECK)
        if not username and not password:
            flash('Username and password required for login')
            return render_template('login.html')
        if not username:
            flash('Username required')
            return render_template('login.html')
        if not password:
            flash('Password required')
            return render_template('login.html')

        if user and user.password == password:
            session['username'] = username
            return redirect('newpost')    
    
    return render_template('login.html')

#LOGOUT ROUTE
@app.route('/logout')   
def logout():
     del session['username']
     flash('You have been logged out')
     return redirect('/login')

#MULTIPLE USE FUNCTION - checks empty fields
def empty_field(entry):
    if entry:
        return True
    else: 
        return False

#REGISTER ROUTE
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
         
        user_exist = User.query.filter_by(username=username).first()
    
        #username validation# error messages replaced with flash messages
        if not empty_field(username) or not empty_field(password) or not empty_field(verify):
            flash('Error: Please fill out the whole form.')
            return render_template('register.html')
        elif len(username) < 3 or len(username) > 20:
            flash('Password should be 3 - 20 characters long.')
            #username_error = 'Password should be 3 - 20 characters long.'
            return render_template('register.html')
        elif ' ' in username:
            flash('No spaces allowed in username')
            #password_error = 'Please re-enter password'
            return render_template('register.html')
        #password validation#
        if not empty_field(password): #not password
            #popup message for flash syntax
            flash('Error: Password required','error')
            return render_template('register.html')
        elif len(password) < 3 or len(password) > 20:
            flash('Error: Password must be between 3 and 20 characters long.')
            return render_template('register.html')
        elif ' ' in password:
            #password_error = 'No spaces allowed in password.'
            flash('Error: No space allowed in the password')
            return render_template('register.html')
    
        #do passwords match
        if verify == '' or verify != password:
            flash('Error: Passwords must be the same.')
            return render_template('register.html')
        
        if not user_exist:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Thank you for registering a new account with Blogz.')
            return redirect('/newpost')
        else:
            flash('Error: Username is taken, please use a different username.')
            return render_template('register.html')
            
    return render_template('register.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body'] 

        owner = User.query.filter_by(username=session['username']).first()

        new_entry = Blog(blog_title, blog_body, owner)

        if empty_field(blog_title) and empty_field(blog_body):
            #next 2 lines add blog title, blog body and the owner of blog to db
            db.session.add(new_entry)        
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_entry.id))
        else:
            #validation of entry for blog_title and blog_body#
            #using redirect/url causes error if passing values, 
            #must use render_template and filename
            if not empty_field(blog_title) and not empty_field(blog_body):
                flash ('Error: Title and blog entry required.')
                return render_template('post.html', blog_title=blog_title, blog_body=blog_body)
            elif not empty_field(blog_title):  
                flash('Error: Title for blog required.')
                return render_template('post.html',  blog_title=blog_title)
            elif not empty_field(blog_body):
                flash('Error: Blog entry required.')
                return render_template('post.html', blog_body=blog_body)

        #part9 13:57
        #postowner = User.query.filter_by(username=session['username']).first()
        #newblog = Blog(blog_title, blog_body, postowner)    
        #return render_template('newpost.html', title='Blog', newblog=newblog)  #needs to show the post      

    else: #if user doesn't enter anything take them back to blog entry page
        return render_template('post.html')

#BLOG ROUTE
@app.route('/blog', methods=['POST','GET'])
def blog():
    entry_id = request.args.get('id')
    users_id = request.args.get('owner_id') #user_id

    if entry_id: 
        user_post = Blog.query.get(entry_id)
        return render_template('post_blog.html', user_post=user_post)

    else:    
        if users_id:
            posts = Blog.query.filter_by(owner_id=users_id)
            return render_template('singleUser.html', posts=posts)

        else:
            allblogs = Blog.query.all()
            return render_template('blog.html', allblogs=allblogs)

if __name__ == '__main__':
    app.run()


#BLOG ROUTE COMMENTS
#chaining to get owner info. please let this be where to put this
#return render_template('post_blog.html', title=user_post.title, body=user_post.body, 
#user=user_post.owner.username, users_id=user_post.owner_id)   
#user_post = Blog.query.filter_by(id=entry_id).first()
#TODO - CHANGING FILE NAME FROM 'BLOGALL.HTML' TO 'BLOG.HTML' TO MATCH INSTRUCTIONS
#return render_template('blogall.html', allblogs=allblogs)