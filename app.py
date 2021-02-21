from flask import Flask,render_template,request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import flash
from flask import redirect
import os
import sys
import click

app = Flask(__name__)

# 初始化扩展， 传入程序实例 app

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))

db = SQLAlchemy(app)

class User(db.Model): # 表名将会是 user（ 自动生成， 小写处理）
    id = db.Column(db.Integer, primary_key=True) # 主键
    name = db.Column(db.String(20))

class Movie(db.Model): # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

name = 'Grey Li'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]


@app.context_processor
def inject_user(): # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user) # 需要返回字典， 等同于return {'user': user}

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html'), 404 # 返回模板和状态码


# app.route() 装饰器来为这个函数绑定对应的 URL
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/db_web')
def db_web():
    movies = Movie.query.all() # 读取所有电影记录
    return render_template('index_db.html', movies=movies)
    
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invaild input')
            return redirect(url_for('index'))
        
        movie = Movie(title = title, year = year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    
    user = User.query.first()
    movies = Movie.query.all()

    return render_template('index.html', name=name, movies=movies)   #会自动找templates文件夹里面的index.html,并不需要一个绝对路径。

@app.route('/login')
def login():
    return render_template('login.html')   

@app.route('/content')
def content():
    return render_template('content.html')  

# 可以在 URL 里定义变量部分
@app.route('/user/<name>')
def user_page(name):
    return 'Usersds: %s' % name   

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（ 请在命令行窗口查看输出的 URL） ：
    print(url_for('hello_world')) # 输出： /
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli')) # 输出： /user/greyli
    print(url_for('user_page', name='peter')) # 输出： /user/peter
    print(url_for('test_url_for')) # 输出： /test
    # 下面这个调用传入了多余的关键字参数， 它们会被作为查询字符串附加到 URL后面。
    print(url_for('test_url_for', num=2)) # 输出： /test?num=2
    return 'Test page'

@app.cli.command()
def forge():
    """ Generate fake data."""
    db.create_all()

    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title = m['title'], year = m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    user = User.query.first()
    return render_template('404.html', user=user), 404 # 返回模板和状态码

@app.route('/movie/edit/<int:movie_id>', methods = ['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id = movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


if __name__=="__main__":
    app.run(host='0.0.0.0',port=8080) 