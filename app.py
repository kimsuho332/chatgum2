from flask import Flask, render_template, request, redirect, url_for
import dropbox

app = Flask(__name__)

DROPBOX_TOKEN = "여기에_너의_dropbox_access_token_입력"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/grade")
def select_grade():
    group_type = request.args.get("type", "weekday")
    return render_template("grade.html", group_type=group_type)

@app.route("/students")
def student_list():
    group_type = request.args.get("type", "weekday")
    grade = request.args.get("grade", "중1")
    students = []
    try:
        _, res = dbx.files_download("/scores.txt")
        lines = res.content.decode("utf-8").splitlines()
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) >= 5 and parts[2] == group_type and parts[3] == grade:
                students.append(f"{parts[0]} {parts[1]}")
    except:
        students = ["2025-04-21 홍길동"]
    return render_template("students.html", group_type=group_type, grade=grade, students=students)

@app.route("/score")
def scoring():
    name = request.args.get("name")
    date = request.args.get("date")
    correct_answers = []
    try:
        _, res = dbx.files_download("/scores.txt")
        lines = res.content.decode("utf-8").splitlines()
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) >= 5 and parts[0] == date and parts[1] == name:
                correct_answers = parts[4].split("/")
                break
    except:
        correct_answers = ["1", "2", "3", "4", "5"]
    return render_template("score.html", name=name, date=date, answers=correct_answers)

@app.route("/submit", methods=["POST"])
def submit_score():
    name = request.form.get("name")
    date = request.form.get("date")
    group_type = request.form.get("group_type")
    grade = request.form.get("grade")
    answers = request.form.getlist("answers")
    wrong = [str(i+1) for i, ans in enumerate(answers) if ans != "O"]
    result_entry = f"{date}:{name}:{group_type}:{grade}:{','.join(wrong) if wrong else '없음'}\n"
    try:
        content = ""
        try:
            _, res = dbx.files_download("/results.txt")
            content = res.content.decode("utf-8")
        except:
            pass
        content += result_entry
        dbx.files_upload(content.encode("utf-8"), "/results.txt", mode=dropbox.files.WriteMode.overwrite)
    except Exception as e:
        print("Dropbox 저장 실패:", e)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
