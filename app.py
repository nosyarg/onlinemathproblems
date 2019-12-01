from flask import *
from flask_sqlalchemy import *
from flask_login import login_user, current_user, LoginManager, UserMixin
from random import *

app = Flask(__name__)

app.secret_key = b'change this secret key asap'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'questions': 'sqlite:///questions.db',
    'problems': 'sqlite:///problems.db',
    'assessments': 'sqlite:///assessments.db'
}
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(db.Model):
    __bind_key__ = 'users'
    username = db.Column(db.String(100),primary_key=True)
    is_authenticated = False
    is_active = True
    is_anonymous = False
    def get_id(self):
        return self.username
    def __str__(self):
        return self.username
    def __repr__(self):
        return self.username

class Question(db.Model):
    __bind_key__ = 'questions'
    idnum = db.Column(db.Integer(),primary_key=True)
    typename = db.Column(db.String(100),nullable=True) 
    inputs = db.Column(db.String(1000),nullable=False) 
    answer = db.Column(db.String(1000),nullable=False) 

class Problem(db.Model):
    __bind_key__ = 'problems'
    idnum = db.Column(db.Integer(),primary_key=True)
    text = db.Column(db.String(100),nullable=True) 
    inputs = db.Column(db.String(1000),nullable=False) 
    answer = db.Column(db.String(1000),nullable=False) 

class Assessment(db.Model):
    __bind_key__ = 'assessments'
    idnum = db.Column(db.Integer(),primary_key=True)
    owner = db.Column(db.String(1000))
    questionlist = db.Column(db.String(10000))
    seed = db.Column(db.Integer())

@login_manager.user_loader
def load_user(username):
    allusers = User.query.order_by(User.username).all()
    for current in allusers:
        if(current.username == username):
            return current

@app.route('/newassessment', methods=['GET'])
def newassessment():
    return render_template('newassessment.html')

@app.route('/newassessment', methods=['POST'])
def newassessment():
    numquestions = int(request.form['numquestions'])
    inputlist = []
    for i in range(numquestions):
        import questions.factoring
        a = int(10*random())
        b = int(10*random())
        c = int(10*random())
        nextproblem = Problem
        (
            idnum = Problem.count(),
            text = questions.factoring.gettext(a,b,c),
            answer = questions.factoring.getanswer(a,b,c)
        )
        try:
            __bind_key__ = 'problem'
            db.session.add(nextproblem)
            db.session.commit()
        except:
            return('problem creating assessment')
        inputlist.append(nextproblem.idnum)
    completeassessment = Assessment
    (
        idnum = Assessment.count()
        owner = current_user.name
        questionlist = str(inputlist)
    )
    return render_template('newassessment.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        __bind_key__ = 'users'
        check_username = request.form['username']
        allusers = User.query.order_by(User.username).all()
        for current in allusers:
            if(current.username == check_username):
                login_user(current)
                return redirect('/')
        return "USERNAME NOT FOUND"
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        new_username = request.form['username']
        newuser = User(username = new_username)
        login_user(newuser)
        try:
            __bind_key__ = 'users'
            db.session.add(newuser)
            db.session.commit()
            return redirect('/')
        except:
            return("ERROR WITH REGISTRATION")
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
