
from apps.home import blueprint
from flask import render_template, request,redirect,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
import sqlite3,os
from datetime import datetime
from flask_login import (
    current_user,
    login_user,
    logout_user
)

current_directory = os.getcwd()

print("Current Directory:", current_directory)
global jsonath2
new=os.path.join(current_directory,'apps')
jsonath1=os.path.join(new,'db.sqlite3')

dd=datetime.today().strftime('%Y-%m-%d')
DB_NAME=jsonath1

def lastweekssales():
    conn1 = sqlite3.connect(DB_NAME)
    cursor1 = conn1.cursor()

    query1 = """WITH RECURSIVE DateSequence AS (
            SELECT DATE(CURRENT_DATE, '-6 days') AS date
            UNION ALL
            SELECT DATE(date, '+1 day') 
            FROM DateSequence 
            WHERE date < CURRENT_DATE
        )
        SELECT
            ds.date,
            CASE 
                WHEN strftime('%w', ds.date) = '1' THEN 'M'
                WHEN strftime('%w', ds.date) = '2' THEN 'T'
                WHEN strftime('%w', ds.date) = '3' THEN 'W'
                WHEN strftime('%w', ds.date) = '4' THEN 'T'
                WHEN strftime('%w', ds.date) = '5' THEN 'F'
                WHEN strftime('%w', ds.date) = '6' THEN 'S'
                WHEN strftime('%w', ds.date) = '0' THEN 'S'
            END AS day_of_week,
            COALESCE(SUM(CAST(p.Amount AS DECIMAL)), 0) AS total_amount
        FROM
            DateSequence ds
        LEFT JOIN
            payment p ON ds.date = p.date
        GROUP BY
            ds.date
        ORDER BY
            ds.date;"""

    cursor1.execute(query1)
    reciept = cursor1.fetchall()

                            # Close the database connection
    conn1.close()
    return reciept



def montlypayment():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    query="""WITH RECURSIVE DateSequence AS (
    SELECT DATE(CURRENT_DATE, 'start of month') AS date
    UNION ALL
    SELECT DATE(date, '-1 month') 
    FROM DateSequence 
        WHERE date > DATE(CURRENT_DATE, 'start of month', '-9 months')
    )
    SELECT
        strftime('%Y-%m', ds.date) AS month,
        COALESCE(SUM(CAST(p.Amount AS DECIMAL)), 0) AS total_amount
    FROM
        DateSequence ds
    LEFT JOIN
        payment p ON strftime('%Y-%m', ds.date) = strftime('%Y-%m', p.date)
    GROUP BY
        strftime('%Y-%m', ds.date)
    ORDER BY
        ds.date;
        """
    cursor.execute(query)
    paymentdata=cursor.fetchall()
    conn.close()
    return paymentdata

def latestvrchofpay():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    qr='SELECT max(Voucher) FROM payment'
    cursor.execute(qr)
    p=cursor.fetchall()
    conn.close()
    return p

def latestvrchofrec():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    qr='SELECT max(Voucher) FROM reciept'
    cursor.execute(qr)
    p1=cursor.fetchall()
    conn.close()
    return p1

def card():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    qr='SELECT cardno,cardholder,exmonth,exyear,ccv FROM cardinfo'
    cursor.execute(qr)
    p1=cursor.fetchall()
    conn.close()
    return p1

def montlyreciept():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    query="""WITH RECURSIVE DateSequence AS (
    SELECT DATE(CURRENT_DATE, 'start of month') AS date
    UNION ALL
    SELECT DATE(date, '-1 month') 
    FROM DateSequence 
    WHERE date > DATE(CURRENT_DATE, 'start of month', '-9 months')
        )
        SELECT
            strftime('%Y-%m', ds.date) AS month,
            COALESCE(SUM(CAST(p.Amount AS DECIMAL)), 0) AS total_amount
        FROM
            DateSequence ds
        LEFT JOIN
            reciept p ON strftime('%Y-%m', ds.date) = strftime('%Y-%m', p.date)
        GROUP BY
            strftime('%Y-%m', ds.date)
        ORDER BY
            ds.date;
        """
    cursor.execute(query)
    paymentdata=cursor.fetchall()
    conn.close()
    return paymentdata



def percentchange():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """SELECT
    SUBSTR(date, 6, 2) AS month,
    SUBSTR(date, 1, 4) AS year,
    SUM(CAST(Amount AS DECIMAL(10, 2))) AS total_amount
    FROM
        payment
    GROUP BY
        SUBSTR(date, 1, 4),
        SUBSTR(date, 6, 2)
    ORDER BY
        year DESC,
        month DESC
    LIMIT 2;"""
    cursor.execute(query)
    perc = cursor.fetchall()
    conn.close()

    return perc



@blueprint.route('/index')
@login_required
def index():
    #-----------------------------------------Last 7 Days
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = 'SELECT COUNT(*) FROM Legders'
    cursor.execute(query)
    data = cursor.fetchall()

    cursor2 = conn.cursor()
    query2="SELECT sum(Amount) FROM payment"
    cursor2.execute(query2)
    totalsale = cursor2.fetchall()
        
    cursor3 = conn.cursor()
    query3 = f"SELECT sum(Amount) FROM payment WHERE date = '{dd}'"
    cursor3.execute(query3)
    todaysale = cursor3.fetchall()

    cursor4 = conn.cursor()
    query4 = "SELECT sum(Amount) FROM reciept"
    cursor4.execute(query4)
    totalreciept = cursor4.fetchall()

    cursor5 = conn.cursor()
    query5 = "SELECT ledgername,Amount,date,paymethod FROM payment ORDER BY Voucher DESC LIMIT 10"
    cursor5.execute(query5)
    last10payments = cursor5.fetchall()
    conn.close()

    a=lastweekssales()
    weeklypayment=[]
    daysway=[]
    for i in a:
        weeklypayment.append(i[2])
        daysway.append(i[1])
    
    # print(weeklypayment)
    # print(daysway)

    monthlist=[]

    monthsdata=[]
    x=montlypayment()
    for i in x:
        monthlist.append(i[0])
        monthsdata.append(i[1])

    # print(monthlist)
    # print(monthsdata)
    maxpayment=max(monthsdata)

    monthlist1=[]
    monthsdata1=[]

    x1=montlyreciept()
    for i in x1:
        monthlist1.append(i[0])
        monthsdata1.append(i[1])

    # print(monthlist1)
    # print(monthsdata1)

    maxreciept=max(monthsdata1)

    percentchan=[]
    x2=percentchange()
    for i in x2:
        percentchan.append(i[2])

    print(percentchan)

    lossorgain=((percentchan[0]-percentchan[1])/percentchan[0])*100
    print(lossorgain)


    return render_template('home/index.html', segment='index',total_cus=str(data)[2:-3],todaysales=str(totalsale)[2:-3],todaysale=str(todaysale)[2:-3],totalreciept=str(totalreciept)[2:-3]
    ,last10payments=last10payments,weeklypayment=weeklypayment,monthlist=monthlist,monthsdata=monthsdata,monthlist1=monthlist1,monthsdata1=monthsdata1,lossorgain=lossorgain,daysway=daysway
    ,maxreciept=maxreciept,maxpayment=maxpayment,maxsalesinaweek=max(weeklypayment))

def latesttra():
    query="""SELECT *
FROM payment
UNION
SELECT *
FROM reciept
ORDER BY date DESC LIMIT 8;"""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return data

@blueprint.route('/search',methods=['GET','POST'])
def getdata():
    data=request.form.get('searchcontent')
    print(data)
    query=f"SELECT * FROM payment WHERE ledgername = '{data}' UNION SELECT * FROM reciept WHERE ledgername = '{data}' ORDER BY date DESC"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    data1 = cursor.fetchall()

    conn2 = sqlite3.connect(DB_NAME)
    cursor2 = conn2.cursor()

    query2 = "SELECT * from Legders"

    cursor2.execute(query2)
    customers = cursor2.fetchall()

                            # Close the database connection
    conn2.close()


    return render_template('home/search.html',data1=data1,customersdata=customers)


@blueprint.route('/notifications',methods=['GET','POST'])
def search():
    # data=request.form.get('searchcontent')
    # print(data)
    # query=f"SELECT * FROM payment WHERE ledgername = '{data}' UNION SELECT * FROM reciept WHERE ledgername = '{data}' ORDER BY date DESC"

    # conn = sqlite3.connect(DB_NAME)
    # cursor = conn.cursor()
    # cursor.execute(query)
    # data1 = cursor.fetchall()
    # print(data1)

    conn2 = sqlite3.connect(DB_NAME)
    cursor2 = conn2.cursor()

    query2 = "SELECT * from Legders"

    cursor2.execute(query2)
    customers = cursor2.fetchall()

                            # Close the database connection
    conn2.close()


    return render_template('home/search.html',customersdata=customers)



@blueprint.route('/<template>')
@login_required
def route_template(template):

    NEWEST=latesttra()
    print(NEWEST)

    page = request.args.get('page', 1, type=int)
    items_per_page = 10                                 # Adjust this based on your needs

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = "SELECT ledgername, Amount, Voucher, date, paymethod FROM payment ORDER BY Voucher DESC"
    offset = (page - 1) * items_per_page
    query += f" LIMIT {items_per_page} OFFSET {offset}"

    cursor.execute(query)
    payments = cursor.fetchall()

                            # Close the database connection
    conn.close()

    #------------------------------------------------------------------------------------------------------------------------------

    page = request.args.get('page', 1, type=int)
    items_per_page = 10                                 # Adjust this based on your needs

    conn1 = sqlite3.connect(DB_NAME)
    cursor1 = conn1.cursor()

    query1 = "SELECT ledgername,Amount,Voucher,date,reciptmthd FROM reciept ORDER BY Voucher DESC"
    offset = (page - 1) * items_per_page
    query1 += f" LIMIT {items_per_page} OFFSET {offset}"

    cursor1.execute(query1)
    reciept = cursor1.fetchall()

                            # Close the database connection
    conn.close()

    page1 = request.args.get('page', 1, type=int)
    items_per_page1 = 40                                 # Adjust this based on your needs

    conn2 = sqlite3.connect(DB_NAME)
    cursor2 = conn2.cursor()

    query2 = "SELECT * from Legders"
    offset1 = (page1 - 1) * items_per_page1
    query1 += f" LIMIT {items_per_page1} OFFSET {offset1}"

    cursor2.execute(query2)
    customers = cursor2.fetchall()

                            # Close the database connection
    conn.close()



    conn4 = sqlite3.connect(DB_NAME)
    cursor4 = conn4.cursor()

    query4 = "SELECT * from Legders"

    cursor4.execute(query4)
    customerslist = cursor4.fetchall()

                            # Close the database connection
    conn4.close()

    conn5 = sqlite3.connect(DB_NAME)
    cursor5 = conn5.cursor()

    query5 = "SELECT * from paymthd"

    cursor5.execute(query5)
    paymthd = cursor5.fetchall()

                            # Close the database connection
    conn5.close()

    rc_number = str(latestvrchofrec())[3:-4]
    print(rc_number)
    incremented_number = int(rc_number[2:]) + 1
    result = "RC" + str(incremented_number).zfill(5)
    print(result)

    rc_number1=str(latestvrchofpay())[3:-4]
    incremented_number1 = int(rc_number1[2:]) + 1
    result1 = "PE" + str(incremented_number1).zfill(5)
    print(result1)
    
    carddet=card()
    print(carddet)


    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment,payments=payments, page=page,reciept=reciept,customers=customers,page1=page1,customerslist=customerslist,paymthd=paymthd
        ,NEWEST=NEWEST,result=result,result1=result1,carddet=carddet)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('/addcustomer',methods=['POST'])
@login_required
def addcustomer():
    company = request.form.get("company")
    print(company)
    namec=request.form.get("namec")
    print(namec)
    address=request.form.get('address')
    print(address)
    mobile=request.form.get('mobile')
    print(mobile)
    gstin=request.form.get('gstin')
    print(gstin)
    pan=request.form.get('pan')
    print(pan)

    conn = sqlite3.connect(DB_NAME)
            #conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * from Legders WHERE ledgername='"+company+"'")
    record = cur.fetchone()
    if record is None:
        query3 = f"INSERT INTO Legders (Ledgername,cus_name,address,Mobile_no,GST,Pan) VALUES ('{company}', '{namec}', '{address}', {mobile}, '{gstin}','{pan}')"
        cur.execute(query3)
        print("customer null: ")
        conn.commit()
    else:
        print("customer not null: ")
    print(record)  

    return redirect(url_for('home_blueprint.route_template', template='billing'))

@blueprint.route('/addreciept',methods=['POST'])
@login_required
def addreciept():
    bankname = request.form.get("bankname")
    print(bankname)
    legder=request.form.get("legder")
    print(legder)
    voucher=request.form.get('voucher')
    print(voucher)
    amount=request.form.get('amount')
    print(amount)
    date=request.form.get('date')
    print(date)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query3 = f"INSERT INTO reciept (reciptmthd, ledgername, Voucher, Amount, date) VALUES ('{bankname}', '{legder}', '{voucher}', {amount}, '{date}')"
    cursor.execute(query3)
    conn.commit()
    return redirect(url_for('home_blueprint.route_template', template='billing'))

@blueprint.route('/addpayment',methods=['POST'])
@login_required
def addpayment():
    paymethod = request.form.get("paymethod")
    print(paymethod)
    legder=request.form.get("legder")
    print(legder)
    voucher=request.form.get('voucher')
    print(voucher)
    amount=request.form.get('amount')
    print(amount)
    date=request.form.get('date')
    print(date)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query4 = f"INSERT INTO payment (paymethod, ledgername, Voucher, Amount, date) VALUES ('{paymethod}', '{legder}', '{voucher}', {amount}, '{date}')"
    cursor.execute(query4)
    conn.commit()
    
    return redirect(url_for('home_blueprint.route_template', template='billing'))

@blueprint.route('/addmethod',methods=['POST'])
@login_required
def Payment_Method():
    newmethod = request.form.get("newmethod")
    print(newmethod)

    conn = sqlite3.connect(DB_NAME)
            #conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM paymthd WHERE paymthd='"+newmethod+"'")
    record = cur.fetchone()
    if record is None:
        query3 = f"INSERT INTO paymthd (paymthd) VALUES ('{newmethod}')"
        cur.execute(query3)
        print("customer null: ")
        conn.commit()
    else:
        print("customer not null: ")
    print(record)  
    
    return redirect(url_for('home_blueprint.route_template', template='billing'))

@blueprint.route('/addcard',methods=['POST'])
@login_required
def addcard():
    cardno = request.form.get("cardno")
    print(cardno)
    nameoncard = request.form.get("nameoncard")
    print(nameoncard)
    expireymonth = request.form.get("expireymonth")
    print(expireymonth)
    expieryyear=request.form.get('expieryyear')
    print(expieryyear)
    ccv=request.form.get('ccv')
    print(ccv)

    conn = sqlite3.connect(DB_NAME)
            #conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cardinfo WHERE cardno='"+cardno+"'")
    record = cur.fetchone()
    if record is None:
        query3 = f"INSERT INTO cardinfo (cardno,cardholder,exmonth,exyear,ccv) VALUES ('{cardno}', '{nameoncard}', '{expireymonth}', {expieryyear},'{ccv}')"
        cur.execute(query3)
        print("customer null: ")
        conn.commit()
    else:
        print("customer not null: ")
    print(record)  

    
    return redirect(url_for('home_blueprint.route_template', template='billing'))




# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
