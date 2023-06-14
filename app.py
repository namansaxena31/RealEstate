from flask import Flask,render_template,request,redirect,url_for,session,flash,jsonify

import mysql.connector
import os

app = Flask(__name__) 
app.secret_key = 'any'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="naman",
    database="project"
)


@app.route('/',methods=['GET','POST'])
def index():
    if session.get('authenticated'):
        guest_name = session['username']
    else:
        guest_name = "Guest"

    return render_template('index.html',message=guest_name)

@app.route('/signin',methods=['GET','POST'])
def signin():

    # POST method
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        # user exists check
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        # correct information
        if user is not None:
            session['authenticated'] = True
            session['username'] = user[0] 
            session['email'] = email
            flash("Welcome to Dubai Properties")
            return redirect(url_for('index'))
        
        # wrong information
        else:        
            error = "Invalid email or password"
            return render_template('signin.html', error=error)

    
    return render_template('signin.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method== 'POST' :

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # password matching check
        if password!=confirm_password:
            flash('Password not Matching')
            return render_template("signup.html")

        # user already exists check
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            flash('User Already Exists')
            return render_template("signup.html")
        
        # inserting into table
        else:
            cursor.execute("INSERT INTO user(name,email,password) VALUES(%s,%s,%s)",(name,email,password))
            db.commit()
            return redirect(url_for('index'))
    
    # GET method
    return render_template('signup.html')

@app.route('/buy',methods=['GET','POST'])
def buy():
    if session.get('authenticated'):
        if request.method=="POST":

            #empty array for sql code
            neighborhood_array =[]

            #checking checkboxes

            if 'c1' in request.form:
                neighborhood_array.append("Dubai Marina")
            if 'c2' in request.form:
                neighborhood_array.append("Bur Dubai")
            if 'c3' in request.form:
                neighborhood_array.append("Deira")
            if 'c4' in request.form:
                neighborhood_array.append("Jumeirah")
            if 'c5' in request.form:
                neighborhood_array.append("Downtown")

            min_price = request.form['min-price']
            max_price = request.form['max-price']
            min_area = request.form['min-area']
            max_area = request.form['max-area']

            p_balcony=p_gym=p_garden=p_parking=p_pool="No"
            if 'cb1' in request.form:
                p_balcony = "Yes"
            if 'cb2' in request.form:
                p_gym = "Yes"
            if 'cb3' in request.form:
                p_garden = "Yes"
            if 'cb4' in request.form:
                p_parking = "Yes"
            if 'cb5' in request.form:
                p_pool = "Yes"
            
            placeholders = ', '.join(['%s'] * len(neighborhood_array))

            cursor = db.cursor()
            cursor.execute("select * from property2 where p_location =%s and (p_price between %s and %s) and (p_area between %s and %s) and p_balcony=%s and p_gym=%s and p_garden = %s and p_parking = %s and p_pool = %s",(neighborhood_array[0],min_price,max_price,min_area,max_area,p_balcony,p_gym,p_garden,p_parking,p_pool))
            results=cursor.fetchall()
            return render_template('buy.html',results=results)
        cursor = db.cursor()
        cursor.execute("select * from property2")
        results_default = cursor.fetchall()
        return render_template('buy.html',results=results_default)
    else:
        flash('You are not Logged in')
        return redirect(url_for('signin'))

@app.route('/sell',methods=['GET','POST'])
def sell():
    if session.get('authenticated'):
        if request.method=="POST":
            p_name = request.form['name']
            p_location = request.form['location']
            p_neighborhood = request.form['neighborhood']
            p_area = request.form['size']
            p_beds = request.form['bedrooms']
            p_baths = request.form['bathrooms']
            p_balcony = request.form['balcony']
            p_gym = request.form['gym']
            p_garden = request.form['garden']
            p_parking = request.form['parking']
            p_pool = request.form['pool']
            p_price = request.form['price']
            file = request.files['photos']

            #saving the photo 
            name= file.filename
            file_path = os.path.join(app.root_path, 'static', 'images', name) 
            file.save(file_path)
            p_photo = "images/"+name

            #database entry
            cursor = db.cursor()
            query = "INSERT INTO property2 (p_name,p_location,p_neighborhood,p_area,p_beds,p_baths,p_balcony,p_gym,p_garden,p_parking,p_pool,p_price,p_photo) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            values = (p_name,p_location,p_neighborhood,p_area,p_beds,p_baths,p_balcony,p_gym,p_garden,p_parking,p_pool,p_price,p_photo)
            cursor.execute(query,values)
            db.commit()
            flash("Property Successfully Listed")
            return redirect(url_for('index'))
        else:
            return render_template('seller.html')
    else:
        flash('You are not Logged in')
        return redirect(url_for('signin'))

@app.route('/t&c',methods=['GET','POST'])
def tnc():
    return render_template('t&c.html')

@app.route('/contactus',methods=['GET','POST'])
def contactus():
    return render_template('contactus.html')

@app.route('/cart',methods=['GET','POST'])
def cart():
    if session.get('authenticated'):
        return render_template('cart.html')
    else:
        flash('You are not Logged in')
        return redirect(url_for('signin'))

@app.route('/contactsend',methods=['POST'])
def contactsend():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    cursor = db.cursor()
    cursor.execute("insert into contact values (%s,%s,%s)",(name,email,message))
    db.commit()
    flash("Thank you for contacting us")
    return redirect(url_for('index'))

@app.route('/buyproperty',methods=['POST'])
def buyproperty():
    p_id = request.form['p_id']
    email = session['email']

    cursor = db.cursor()
    cursor.execute("insert into buy values (%s,%s)",(email,p_id))
    db.commit()
    flash("Succesfully Purchased")
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
    