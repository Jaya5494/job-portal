from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///job_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50))
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

@app.route("/")
def index():
    jobs = Job.query.all()
    return render_template("index.html", jobs=jobs)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/post_job", methods=["GET", "POST"])
def post_job():
    if session.get("role") != "employer":
        return redirect(url_for("index"))
    if request.method == "POST":
        job = Job(
            title=request.form["title"],
            description=request.form["description"],
            salary=request.form["salary"],
            location=request.form["location"],
            company=request.form["company"]
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("post_job.html")

@app.route("/apply/<int:job_id>")
def apply(job_id):
    if session.get("user_id") and session.get("role") == "jobseeker":
        application = Application(user_id=session["user_id"], job_id=job_id)
        db.session.add(application)
        db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Force insert dummy jobs (you can remove or comment this block later)
        jobs = [
            Job(
                title="Frontend Developer",
                description="Work on UI components using React and TailwindCSS.",
                salary="6 LPA",
                location="Remote",
                company="OpenAI Solutions"
            ),
            Job(
                title="Backend Developer",
                description="Develop RESTful APIs using Flask and PostgreSQL.",
                salary="8 LPA",
                location="Bangalore",
                company="DataSphere Pvt Ltd"
            ),
            Job(
                title="Data Analyst",
                description="Analyze business data and create dashboards using Power BI.",
                salary="5.5 LPA",
                location="Hyderabad",
                company="Insight Analytics"
            ),
            Job(
                title="DevOps Engineer",
                description="Manage CI/CD pipelines and cloud deployments.",
                salary="9 LPA",
                location="Chennai",
                company="CloudOps Systems"
            )
        ]
        db.session.add_all(jobs)
        db.session.commit()

    app.run(debug=True)
