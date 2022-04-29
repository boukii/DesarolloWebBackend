mport email
from operator import index
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import datetime
import pymongo
from sqlalchemy import null
import pyautogui as pag
import pymsgbox


# FlASK
#############################################################
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = "super secret key"
#############################################################

# FlASK
#############################################################
mongodb_key = "mongodb+srv://desarrollowebuser:desarrollowebpassword@cluster0.dfh7g.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(
    mongodb_key, tls=True, tlsAllowInvalidCertificates=True)
db = client.Escuela
cuentas = db.alumno
#############################################################

# Twilio
#############################################################
#account_sid = ""
#auth_token = ""
#TwilioClient = Client(account_sid, auth_token)
#############################################################

def informacion(email):
    users=[]
    user = cuentas.find_one({"correo": (email)})
    nombre = user["nombre"]
    matricula= user["matricula"]
    users = []
    users.append(nombre)
    users.append(matricula)
    users.append(email)
    return users


@app.route('/')
def home():
    email = None
    if "email" in session:
        email = session["email"]
        user = cuentas.find_one({"correo": (email)})
        nombre= user["nombre"]
        matricula= user["matricula"]
        users = []
        users.append(nombre)
        users.append(matricula)
        users.append(email)
        return render_template('index.html', data=users)
    else:
        return render_template('login.html')
    
    
@app.route("/login", methods=["GET", "POST"])
def login():
    email = None
    if "email" in session:
        email=session['email']
        email = session["email"]
        user = cuentas.find_one({"correo": (email)})
        nombre= user["nombre"]
        matricula= user["matricula"]
        users = []
        users.append(nombre)
        users.append(matricula)
        users.append(email)
        return render_template('index.html', data=users)
    else:
        if (request.method == "GET"):
            return render_template("login.html", data="email")
        else:
            email = request.form["correo"]
            password = request.form["contrasena"]
            
            try:
                user = cuentas.find_one({"correo": (email)})
                if(user!=None):
                    
                    if (user["contrasena"] == password):
                        session["email"] = email
                        nombre= user["nombre"]
                        matricula= user["matricula"]
                        users = []
                        users.append(nombre)
                        users.append(matricula)
                        users.append(email)
                        return render_template("index.html", data=users)

                    else:
                        resp =pag.alert(text="Contraseña incorrecta", title="Contraseña incorrecta")
                        if (resp):
                            return redirect(url_for("login"))
                else:
                    resp =pag.alert(text="Correo Inesxintente", title="Correo Inexistente")
                    if (resp):
                        return redirect(url_for("login"))
                    return null
                        
                    
            except Exception as e:
                return "%s" % e

                
        
@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return redirect(url_for("home"))


@app.route('/homepage')
def homepage():
    return render_template('Homepage.html')


@app.route('/create')
def create_form():  
    return render_template('CreateForm.html')


@app.route("/usuarios")
def usuarios():
    cursor = cuentas.find({})
    users = []
    for doc in cursor:
        users.append(doc)
    return render_template("/Retrieve.html", data=users)


@app.route("/insert", methods=["POST"])
def insertUsers():
    
    user = {
        "matricula": request.form["matricula"],
        "nombre": request.form["nombre"],
        "correo": request.form["correo"],
        "contrasena": request.form["contrasena"],
    }
    if cuentas.find_one({"correo": user['correo'] }):
        
        resp = pag.alert(text="Correo ya registrado por favor Inicia Sesión", title="Correo Existente")
        #resp= pymsgbox.confirm('Correo ya registrado por favor Inicia Sesión!', 'Correo Existente')

        if (resp):
            return redirect(url_for("home"))
      
    else:
             
        try:
            cuentas.insert_one(user)
            correo=user["correo"]
            nombre= user["nombre"]
            matricula= user["matricula"]
            users = []
            users.append(nombre)
            users.append(matricula)
            users.append(correo)
            #comogusten = TwilioClient.messages.create(
                #from_="whatsapp:+14155238886",
                #body="El usuario %s se agregó a tu pagina web" % (
                    #request.form["nombre"]),
                #to="whatsapp:+5215514200581"
            #)
            #print(comogusten.sid)
            session["email"]=correo
            return render_template('index.html', data=users)
        except Exception as e:
            return "<p>El servicio no esta disponible =>: %s %s" % type(e), e


@app.route("/find_one/<matricula>")
def find_one(matricula):
    try:
        user = cuentas.find_one({"matricula": (matricula)})
        if user == None:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            return "<p>Encontramos: %s </p>" % (user)
    except Exception as e:
        return "%s" % e

@app.route("/delete_one/<matricula>")
def delete_one(matricula):
    try:
        
        user = cuentas.delete_one({"matricula": (matricula)})
        if user.deleted_count == None and "email" in session:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            session.clear()
            user.deleted_count
            return redirect(url_for("home"))
    except Exception as e:
        return "%s" % e
    
    
@app.route("/update", methods=["POST"])
def update():
    try:
        filter = {"matricula": request.form["matricula"]}
        user = {"$set": {
            "nombre": request.form["nombre"]
        }}
        cuentas.update_one(filter, user)
        return redirect(url_for("usuarios"))

    except Exception as e:
        return "error %s" % (e)