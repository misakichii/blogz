from flask import Flask, request, redirect, flash, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 's58c!^54dg9z4frc'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    day = db.Column(db.String(10))
    date = db.Column(db.String(10))

    def __init__(self, title, body, day, date):
        self.title = title
        self.body = body
        self.day = day
        self.date = date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

def empty_field(entry):
    if entry:
        return True
    else:
        return False

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_day = request.form.get('day')
        blog_date = request.form['date']

        if not empty_field(blog_title) and not empty_field(blog_body):  
            flash ('Error: Title and blog entry required.')
            return redirect('/newpost')
        elif not empty_field(blog_title):  
            flash('Error: Title for blog required.')
            return redirect('/newpost')
        elif not empty_field(blog_body):
            flash('Error: Blog entry required.')
            return redirect('/newpost')

        new_post = Blog(blog_title, blog_body, blog_day, blog_date)

        db.session.add(new_post)
        db.session.commit()

        return render_template('newpost.html', title='Blogz', new_post=new_post)
    else:
        return render_template('blog.html')

    @app.route('/blog', method=['POST', 'GET'])    
    def blog():
        blog_id = request.args.get('id')

        if (blog_id):
            new_entry = Blog.query.get(blog_id)
            return render_template('newpost.html', title='Blogz', new_entry=new_entry)
        else:
            blog_list = Blog.query.all()
        return render_template('blogall.html', title='Blogz', blog_list=blog_list)

    if __name__ == '__main__':
        app.run()

