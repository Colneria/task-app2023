from flask import Flask,render_template,request,redirect,session
import sqlite3

app = Flask(__name__)
app.secret_key="SUNABACO2023"

@app.route("/")
def top():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("index.html")

@app.route("/hello")
def hello():
    py_name="yamada"
    return render_template("hello.html",name=py_name)

@app.route("/add")
def add_get():
    if "user_id" in session:
        return render_template("add.html")
    else:
        return redirect("/")

@app.route("/add", methods=["POST"])
def add_post():
        user_id = session["user_id"][0]
        task = request.form.get("task")
        print(task)
        # 2.データベースに接続する
        conn = sqlite3.connect("MyTask.db")
        # 3.データベースを操作するための準備
        c = conn.cursor()
        # 4.SQLを実行してDBにデータを送る
        c.execute("insert into task values (null, ?,?)", (task, user_id))
        # 5.データベースを更新（保存）する
        conn.commit()
        # 6.データベースの接続を終了する
        c.close()
        # リダイレクトでルーティングに飛ばす
        return redirect("/list")


@app.route("/list")
def list_get():

    if "user_id" in session:
        # DBを接続して処理
        user_id = session["user_id"][0]
        conn = sqlite3.connect("MyTask.db")
        c= conn.cursor()
        # taskテーブルの中身を取得するSQL
        c.execute("select id, task from task where user_id = ?",(user_id,))
        task_list = []

        for row in c.fetchall():
            task_list.append( {"id" : row[0], "task": row[1]} )
        c.close()
        print("----------")
        print(task_list)

        return render_template("list.html",task_list = task_list)
    else:
        return redirect("/")



@app.route("/edit/<int:task_id>")
def edit_get(task_id):
    if "user_id" in session:
        conn = sqlite3.connect("MyTask.db")
        c = conn.cursor()
        c.execute("select task from task where id = ?", ( task_id, ) )
        # レコードの１行を取得
        task = c.fetchone()
        c.close()
        # c.fetchoneで取り出したものはタプルになるので
        task = task[0]
        return render_template("edit.html", task = task, task_id = task_id)
    else:
        return redirect("/")


    # タスクの元データを取得する記述


@app.route("/edit", methods=["POST"])
def edit_post():
    task_id = request.form.get("task_id")
    task = request.form.get("task")

    conn = sqlite3.connect("MyTask.db")
    c = conn.cursor()
    c.execute("update task set task = ? where id = ?", (task, task_id))
    conn.commit()
    c.close()
    # リストページにリダイレクト
    return redirect("/list")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "user_id" in session:
        conn = sqlite3.connect("MyTask.db")
        c = conn.cursor()
        c.execute("delete from task where id = ?",(task_id,))
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/")



# 登録
@app.route("/regist")
def regist_get():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("regist.html")

@app.route("/regist", methods=["POST"])
def regist_post():
    name = request.form.get("name")
    password = request.form.get("password")

    conn = sqlite3.connect("MyTask.db")
    c = conn.cursor()
    c.execute("insert into users values(null,?,?)",(name,password))
    conn.commit()
    c.close()
    return redirect("/login")

@app.route("/login")
def login_get():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("login.html")

@app.route("/login",methods=["POST"])
def login_post():
    name=request.form.get("name")
    password = request.form.get("password")
    conn = sqlite3.connect("MyTask.db")
    c = conn.cursor()
    c.execute("select id from users where name = ? and password =?",(name, password))
    id = c.fetchone()
    c.close()
    # ログイン成功
    if id is not None:
        # セッションを発行 idをuser_idという名前で格納
        session["user_id"]=id
        return redirect("/list")
    # ログイン失敗
    else:
        return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect("/")


# @app.route("/<name>")
# def greet(name):
#     return name + "さん、こんにちは"

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html")

if __name__ == "__main__":
    app.run(debug=True)