from flask import Flask, render_template, request,session
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import os
import re
import random
import string
import datetime
import requests


app= Flask(__name__)

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=whc86393;PWD=uGbpEH72cbM04CgG",'','')

if __name__== "__main__":
    app.run(debug=True, port=5000 ,host="0.0.0.0")
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/studentprofile")
def sprofile():
    return render_template("studentprofile.html")



@app.route("/adminprofile")
def aprofile():
    return render_template("adminprofile.html")

@app.route("/facultyprofile")
def fprofile():
    return render_template("facultyprofile.html")

@app.route("/login", methods=['POST','GET'])
def loginentered():
    global Userid
    global Ussername
    msg=''
    if request.method=="POST":
        email=str(request.form['email'])
        print(email)
        password=request.form["password"]
        sql="select * from REGISTER where email=? and password=?"
        stmt= ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.executr(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin']=True
            session['id']= account['email']
            Userid= account['email']
            session['email']=account['email']
            Username=account['username']
            Name=account['Name']
            msg="logged in successfully !"
            sql="select role from register where email=?"
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.execute(stmt)
            r= ibm_db.fetch_assoc(stmt)
            print(r)
            if r['role']==1:
                print("STUDENT")
                return render_template("studentprofile.html",msg=msg, user=email, name=Name, role="STUDENT", username=Username, email=email)
            elif r['role']==2:
                print("FACULTY")
                return render_template("facultyprofile.html", msg=msg, user=email, name=Name, role="FACULTY", username=Username, email=email)
            else:
                return render_template("adminprofile.html", msg=msg, user=email, name=Name, role="ADMIN", username=Username, email=email)
        else:
                msg="Incorrect Email/password"
                return render_template("login.html", msg=msg)
    else:
                return render_template("login.html"
                                       )
    
@app.route("/register", methods=['POST', 'GET'])
def signup():
    msg= ''
    if request.method=='POST':
        name=request.form["sname"]
        email=request.form["semail"]
        username=request.form["susername"]
        role=int(request.form['role'])
        password=''.join(random.choice(string.ascii_letters) for i in range(0,8))
        link='https://unicersity.ac.in/portal'
        print(password)
        sql= "select * from register where email=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg="Already Registered"
            return render_template('adminregister.html', error=True, msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg="invalid Email Address"
        else:
            insert_sql="insert into register values (?,?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn, insert_sql)
            # this username & password should be same as db2 details and in order also
            ibm_db.bind_param(prep_stmt,1,name)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,username)
            ibm_db.bind_param(prep_stmt,5,role)
    
@app.route("/studentsubmit", methods=['POST','GET'])
def sassignment():
    u= Ussername.strip()
    subtime=[]
    ma=[]
    sql="select Subtime, marks from submit where studentname=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,u)
    ibm_db.execute(stmt)
    st=ibm_db.fetch_tuple(stmt)
    while st!=False:
        subtime.append(st[0])
        ma.append(st[1])
        st=ibm_db.fetch_tuple(stmt)
    print(subtime)
    print(ma)
    if request.method=="POST":
        for x in range(1,5):
            x=str(x)
            y=str("file"+x)
            print(type(y))
            f=request.file[y]
            print(f)
            print(f.filename)
            
            if f.filename !='':
                
                basepath=os.path.dirname(__file__) #getting the current path i.e where app.py is present
                #print ("current path",basepath)
                filepath=os.path.join(basepath,'uploads',u+x+".pdf") #from anywhere in the system we can give image but we want that image
                #print(upload folder is",filepath)
                f.save(filepath)


@app.route("/facultymarks")
def facultymarks():
    data=[]
    sql="select username from register where role=1"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    name=ibm_db.fetch_tuple(stmt)
    while name!= False:
        data.append(name)
        name=ibm_db.fetch_tuple(stmt)
    data1=[]
    for i in range (0,len(data)):
        y=data[i][0].strip()
        data1.append(y)
    data1=set(data1)
    data1=list(data1)
    print(data1)
    
    return render_template("facultystulist.html", names= data1, Le=len(data1))

        

@app.route("/marksassign/<string:stdname>", methods=['POST','GET'])
def marksassign(stdname):
    global u
    global g
    global file
    da =[]
    
    COS_ENDPOINT = "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints"
    COS_API_KEY_ID = "H9163jBcq5Q8FrsM3Lvd7q4dt0g557J2mFL3PkvaMw1d"
    COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/14f366562d78432f9d53866158d664d7:ff5455ba-8300-4678-bc82-da5f822889e4::"
    cos = ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_INSTANCE_CRN, config=Config(signature_version="oauth"),endpoint_url=COS_ENDPOINT)
    output = cos.list_objects(Bucket="ansh")
    output
    l=[]
    for i in range(0,len(output['Contents'])):
        j=output['Contents'][i]['Key']
        l.append(j)
    l
    u=stdname
    print(len(u))
    print(len(l))
    n=[]
    for i in range (0,len(l)):
        for j in range(0,len(u)):
            if u[j]==l[i][j]:
                n.append(l[i])


@app.route("/logout")
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return render_template("logout.html")




























































