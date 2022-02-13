from multiprocessing import Process
from flask import Flask, render_template,request
import requests
import json
import time
import pyodbc

app = Flask(__name__)

conn=pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;'
                      'Server=ABHI173\SQLEXPRESS;'
                      'Database=Work;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()
cursor.execute("IF OBJECT_ID (N'dbo.Information',N'U') is Null Begin create table dbo.Information (Name VARCHAR(50) "
               "NOT NULL,Gender VARCHAR(50) NOT NULL,Location VARCHAR(50)  ,Mail VARCHAR(50) )end;")

cursor.commit()





def WriteToDatabase():
    count = 0
    while True:
        count = count + 1
        response = requests.get('https://randomuser.me/api')
        json_load = (json.loads(response.text))
        gender = json_load["results"][0]["gender"]
        fullname = json_load["results"][0]["name"]["title"] + " " + \
                   json_load["results"][0]["name"]["first"] + " " + \
                   json_load["results"][0]["name"]["last"]
        gender = json_load["results"][0]["gender"]
        location = json_load["results"][0]["location"]["country"]
        mail = json_load["results"][0]["email"]
        cursor.execute('INSERT INTO dbo.Information (Name,Gender,Location,Mail) values(?,?,?,?)',fullname,gender,location,mail)
        cursor.commit()
        time.sleep(30)


@app.route("/", methods=["GET","POST"])
def hello_world():
    nameslist = []
    display=""
    listlen=0
    if request.method=="POST":

        countryname = request.form["country"]
        print(countryname)
        cursor.execute(f"select * from dbo.Information where Location='{countryname}'")

        nameslist=cursor.fetchall()
        listlen=len(nameslist)
        if listlen>0:
            display=f"Records found{listlen}"
        else:
            display = f"No  records found"
        cursor.commit()
    return render_template('index.html',details=nameslist,display=display)


@app.route("/bye/<name>")
def bye(name):
    return "bye " + name


def func1():
    app.run(debug=True)


if __name__ == "__main__":
    p1 = Process(target=func1)
    p2 = Process(target=WriteToDatabase)
    p2.start()
    p1.start()
    p1.join()

    p2.join()
