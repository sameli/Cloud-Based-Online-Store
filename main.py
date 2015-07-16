# Online Store for Google app engine
# by S. Ameli

# Notes:
# This script has been tested with Google app engine 1.8.9
# How to run:
# cd [the directory of this file]
# /[path to google app engine]/dev_appserver.py .

import webapp2
import os
import cgi
import re
import time
from google.appengine.ext import db
from google.appengine.api import users

# This class generates the order page
class OrderPage(webapp2.RequestHandler):
    def get(self):
        itemID = self.request.GET["itemID"]
        itemName= self.request.GET["itemName"]
        itemPrice = self.request.GET["itemPrice"]
        content = """<html><body>
        <head>
        <title>Online Store - Order</title>
        <style>
        body {
            font-family: Verdana, Helvetica, sans-serif;
            background-color: #DDDDDD;
        }
        </style>
        </head>
        <script>
        var itemPrice = %s;
        """ % (itemPrice)
        
        content += """
        var taxRates = { 10 : 15 , 30 : 10, 50 : 1 };
        
        function calcTotal(){
            var weight = document.getElementById("weightInput").value;
            if(weight >= 1){
                var totalBeforeTax = weight * itemPrice;
                var selectedTaxRate = 0;
                
                for(var key in taxRates) {
                    //alert(key);
                    if(totalBeforeTax < key){
                        selectedTaxRate = taxRates[key]
                        break;
                    }
                }
                
                var totalAfterTax = ((selectedTaxRate /100) * totalBeforeTax) + totalBeforeTax;
                
                document.getElementById("totalBeforeTax").value = "$" + totalBeforeTax.toFixed(2);
                document.getElementById("taxRate").value = selectedTaxRate + "%%";
                document.getElementById("totalAfterTax").value = "$" + totalAfterTax.toFixed(2);
                document.getElementById("submitOrder").disabled = false;


            }else
                alert("weight input is invalid");
        }
        
        function checkAndSubmitForm(){
            calcTotal();
            
            var address = document.getElementById("address").value;
            var deliveryTime = document.getElementById("deliveryTime").value;

            if(address == "" || deliveryTime == "")
                alert("Please fill valid data.");
            else
                document.getElementById('orderForm').submit();
        }
        </script>

         <p> Order page: </p> </br>
        
         <form id="orderForm" method = "post" action = "/report">
         
          Selected item: <br />
          Item ID: <input type = "text" name = "itemID" value = "%s" readonly style="background-color: lightgray;" /> <br />
          Item Name: <input type = "text" name = "itemName" value = "%s" readonly style="background-color: lightgray;" /> <br />
          Item Price (per kg): <input type = "text" name = "itemPrice" value = "$%s" readonly style="background-color: lightgray;" /><br />
          <br />
          
          <div style = "color: blue">
             Please fill in all fields then click "Calculate Total": <br /><br />
          </div>
          
          Weight (in kg): <input type = "text" id = "weightInput"  name = "weightInput" /> (Minimum 1 kg)<br />
          Delivery Address: <input type = "text" id = "address" name = "address" /><br />
          Preferred Delivery Time: <input type = "text" id = "deliveryTime" name = "deliveryTime"/> (Any format is accepted)<br />
          <br />
          Total (before tax): <input type = "text" id = "totalBeforeTax" readonly style="background-color: lightgray;" /><br />
          Tax rate <input type = "text" id = "taxRate" name = "taxRate" readonly style="background-color: lightgray;" /><br />
          Total (after tax): <input type = "text" id = "totalAfterTax" name = "totalAfterTax" readonly style="background-color: lightgray;" /><br />
          <br />
          <button type="button" onclick="calcTotal()" id="calctaxbtn">Calculate Total</button>
          <button type="button" onclick="checkAndSubmitForm()" id="submitOrder" disabled>Submit Order</button>
          
        </form>
        <br />
        <a href="/">Click here to discard this order and go to home page</a>
        """ % (itemID, itemName, itemPrice)
        
        content += """
        
        <br /> <br />
        Tax rate guide: <br />
        Basically tax rate is calculated based on total cost and the table below: <br />
        So if total cost of your order is less than the specified total cost in each row of this table, tax rate of
        that row will be applied.<br />
        Zero tax will be counted for unspecified ranges.<br />
        <table style = "border: 0; border-width: 0;
             border-spacing: 10">
          <tr><td style = "background-color: yellow">Total Cost </td>
              <td style = "background-color: yellow">Tax rate</td>
          </tr>
        
        """
        
        listOfTaxRates = db.GqlQuery("SELECT * FROM TaxRatesDB ORDER BY totalCost ASC")
        for row in listOfTaxRates:
    
            totalCost = str(row.totalCost)
            taxRate = str(row.taxRate)
            
            content += """
            <tr>
            <td>$%s</td> <td>%s%%</td>
            </tr>
            """ % (totalCost, taxRate)
            
        content += """
              </table>
          </body>
        </html>
        """
        
        
        self.response.write(content)
        

# This class generates the report page for the user
class ReportPage(webapp2.RequestHandler):
    def post(self):
        itemID = self.request.get('itemID')
        itemName = self.request.get('itemName')
        itemPrice = self.request.get('itemPrice')
        weightInput = self.request.get('weightInput')
        address = self.request.get('address')
        deliveryTime = self.request.get('deliveryTime')
        taxRate = self.request.get('taxRate')
        totalAfterTax = self.request.get('totalAfterTax')
        
        ordersDB = db.GqlQuery("SELECT * FROM OrdersDB")
        orderID = str(ordersDB.count()+1)
        
        user = users.get_current_user()
        userNickName = "Guest User"
        if user:
            userNickName = user.nickname()
        
        
        ordersDBObj = OrdersDB()
        ordersDBObj.orderID = orderID
        ordersDBObj.userID = userNickName
        ordersDBObj.itemID = itemID
        ordersDBObj.weight = weightInput
        ordersDBObj.address = address
        ordersDBObj.preferredTime = deliveryTime
        ordersDBObj.totalCost = totalAfterTax
        ordersDBObj.put()
        
        self.response.write("""
        <html><body>
        <head>
        <title>Online Store - Report order</title>
        <style>
        body {
            font-family: Verdana, Helvetica, sans-serif;
            background-color: #DDDDDD;
        }
        </style>
        </head>
        Report of your order:  <br /> <br />
        Selected item: <br />
        Order ID: %s <br />
        User: %s <br />
        Item ID: %s <br />
        Item Name: %s <br />
        Price (per kg): %s <br />
        Requested weight: %s kg <br />
        Delivery Address: %s <br />
        Preferred Time: %s <br />
        Tax Rate: %s <br />
        Total: %s <br />
         <br /> <br />
        Your order will be sent to you once we receive payment.
        <br /> <a href="/">Click here to go to home page</a>
        
         </body></html>
        """ % (orderID, userNickName, itemID, itemName, itemPrice, weightInput, address, deliveryTime, taxRate, totalAfterTax))

# This class defines the product value types for the database
class ProductsDB(db.Model):
    itemID = db.IntegerProperty()
    itemName = db.StringProperty()
    itemPrice = db.FloatProperty()
    itemAvailability = db.BooleanProperty()

# This class defines the order value types for the database
class OrdersDB(db.Model):
    orderID = db.StringProperty()
    userID = db.StringProperty()
    itemID = db.StringProperty()
    weight = db.StringProperty()
    address = db.StringProperty()
    preferredTime = db.StringProperty()
    totalCost = db.StringProperty()
    
# This class defines the tax rates and total cost of order for the database
class TaxRatesDB(db.Model):
    totalCost = db.FloatProperty()
    taxRate = db.FloatProperty()
    
# This function checks if tables exist or not and returns a boolean value
def checkIfTablesExist():
    productsDB = db.GqlQuery("SELECT * FROM ProductsDB")
    rowCountProductsDB = productsDB.count()
    print "count: "+ str(rowCountProductsDB)
    
    taxRatesDB = db.GqlQuery("SELECT * FROM TaxRatesDB")
    rowCountTaxRatesDB = taxRatesDB.count()
    print "count: "+ str(rowCountTaxRatesDB)
    
    
    if rowCountProductsDB > 0 and rowCountTaxRatesDB > 0:
        return True
    else:
        return False
    
# This function initializes the database with default values
def initializeDBs():
    dbproductstmp1 = ProductsDB()
    dbproductstmp1.itemID = 1
    dbproductstmp1.itemName = "Apple"
    dbproductstmp1.itemPrice = 1.5
    dbproductstmp1.itemAvailability = True
    dbproductstmp1.put()
    
    dbproductstmp2 = ProductsDB()
    dbproductstmp2.itemID = 2
    dbproductstmp2.itemName = "Orange"
    dbproductstmp2.itemPrice = 3.0
    dbproductstmp2.itemAvailability = True
    dbproductstmp2.put()
    
    dbproductstmp3 = ProductsDB()
    dbproductstmp3.itemID = 3
    dbproductstmp3.itemName = "Grapes"
    dbproductstmp3.itemPrice = 8.0
    dbproductstmp3.itemAvailability = False
    dbproductstmp3.put()
    
    dbtaxrate1 = TaxRatesDB()
    dbtaxrate1.totalCost = 10.0
    dbtaxrate1.taxRate = 15.0
    dbtaxrate1.put()

    dbtaxrate2 = TaxRatesDB()
    dbtaxrate2.totalCost = 30.0
    dbtaxrate2.taxRate = 10.0
    dbtaxrate2.put()

    dbtaxrate3 = TaxRatesDB()
    dbtaxrate3.totalCost = 50.0
    dbtaxrate3.taxRate = 1.0
    dbtaxrate3.put()

# This function delets contents of all tables
def resetDBs():
    productsDB = db.GqlQuery("SELECT * FROM ProductsDB")
    for item in productsDB:
        item.delete()
        
    ordersDB = db.GqlQuery("SELECT * FROM OrdersDB")
    for item in ordersDB:
        item.delete()
    
    taxRatesDB = db.GqlQuery("SELECT * FROM TaxRatesDB")
    for item in taxRatesDB:
        item.delete()


# This function generates the main page and grabs the items from the database
def printMainPage():
    content = """
    <html>
      <head>
      <title>Online Store</title>
        <style>
        body {
            font-family: Verdana, Helvetica, sans-serif;
            background-color: #DDDDDD;
        }
        </style>
      </head>
      <body>
          <p> List of products: </p>
    
          <table style = "border: 0; border-width: 0;
             border-spacing: 10">
          <tr><td style = "background-color: yellow">Item ID </td>
              <td style = "background-color: yellow">Item Name</td>
              <td style = "background-color: yellow">Price (per kg)</td>
              <td style = "background-color: yellow">Availability</td>
              <td style = "background-color: yellow">Order link</td>
          </tr>
    """ 
    listOfProducts = db.GqlQuery("SELECT * FROM ProductsDB ORDER BY itemID ASC") 
    for row in listOfProducts:

        itemID = str(row.itemID)
        itemName = row.itemName
        itemPrice = str(row.itemPrice)
        iitemAvailability = str(row.itemAvailability)
        
        linkStr = "---"
        if row.itemAvailability:
            linkStr = """
            <a href="/order?itemID=%s&itemName=%s&itemPrice=%s">Order this item</a>
            """ % (itemID, itemName, itemPrice)        
        
        content += """
        <tr>
        <td>%s</td> <td>%s</td> <td>$%s</td> <td>%s</td> <td> %s </td>
        </tr>
        """ % (itemID, itemName, itemPrice, iitemAvailability, linkStr)
        
    content += """
          </table>

          <br />
        <a href="/admin">Click here to go to Admin page</a> <br /> <br />
      </body>
    </html>
    """
    return content;

# This class generates a page that allows Administrator to add items to the store
class AddItemPage(webapp2.RequestHandler):
    def post(self):

        itemID = self.request.get("itemID")
        itemName = self.request.get("itemName")
        itemPrice = self.request.get("itemPrice")
        itemAvailability = self.request.get("itemAvailability")
        
        
        dbproductstmp1 = ProductsDB()
        dbproductstmp1.itemID = int(itemID)
        dbproductstmp1.itemName = itemName
        dbproductstmp1.itemPrice = float(itemPrice)
        if itemAvailability == "True":
            dbproductstmp1.itemAvailability = True
        else:
            dbproductstmp1.itemAvailability = False
        dbproductstmp1.put()
        
        self.response.write("<html><body> item has been added. redirecting to home page now.")
        time.sleep(1)
        self.redirect("/")
        
    def get(self):
        productsDB = db.GqlQuery("SELECT * FROM ProductsDB")
        rowCountProductsDB = productsDB.count()
        nextProductID = rowCountProductsDB + 1
    
        content = """
        <html><body>
        <head>
        <title>Online Store -- Add Item</title>
        <style>
        body {
            font-family: Verdana, Helvetica, sans-serif;
            background-color: #DDDDDD;
        }
        </style>
      </head>
        <script>

        function submitfunc(){
            var itemName = document.getElementById("itemName").value;
            var itemPrice = document.getElementById("itemPrice").value;

            var result = itemPrice.match(/^\d{0,2}(?:\.\d{0,2}){0,1}$/);
            
            if(itemName == "" || itemPrice == "" || itemPrice < 0 || !result){
                alert("Please enter valid values. Item Price must be larger than zero and also item name must be given.");
            }else{
                document.getElementById('orderForm').submit();
            }
        }
        </script>
            
            
        <form id="orderForm" method = "post" action = "/additem">
         
          <div style = "color: blue">
             Please fill in all fields then click "Submit": <br /><br />
          </div>
          
          Item ID: <input type = "text" name = "itemID" name = "itemID" value = "%s" readonly style="background-color: lightgray;" /> <br />
          Item Name: <input type = "text" id = "itemName" name = "itemName"/> <br />
          Item Price (per kg): <input type = "text" id = "itemPrice" name = "itemPrice"/><br />
          Availability:
          <select name = "itemAvailability">
          <option>True</option>
          <option>False</option>
          </select><br />
          <br />
          <button type="button" onclick="submitfunc()" id="submitbtn" name="submitbtn">Submit</button>
          
        </form>
        <br />
        <a href="/admin">Click here to discard this page and go back to admin page</a> <br /> <br /> <br />
        </body></html>
        """ % (nextProductID)
        self.response.write(content)
        
# This class generates a page which lists all of the orders by users
class AdminPage(webapp2.RequestHandler):
    def get(self):
        content = """
        <html>
          <head>
          <title>Online Store - Admin page</title>
            <style>
            body {
                font-family: Verdana, Helvetica, sans-serif;
                background-color: #DDDDDD;
            }
            </style>
          </head>
          <body>
              <p> list of orders: </p>
        
              <table style = "border: 0; border-width: 0;
                 border-spacing: 10">
              <tr><td style = "background-color: yellow">Order ID </td>
                  <td style = "background-color: yellow">User ID</td>
                  <td style = "background-color: yellow">Ordered Item ID</td>
                  <td style = "background-color: yellow">Weight</td>
                  <td style = "background-color: yellow">Delivery Address</td>
                  <td style = "background-color: yellow">Preferred Time</td>
                  <td style = "background-color: yellow">Total Cost</td>
              </tr>
        """ 
        listOfOrders = db.GqlQuery("SELECT * FROM OrdersDB ORDER BY orderID DESC") 
        for row in listOfOrders:

            orderID = row.orderID
            userID = row.userID
            itemID = row.itemID
            weight = row.weight
            address = row.address
            preferredTime = row.preferredTime
            totalCost = row.totalCost
            
            content += """
            <tr>
            <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td>
            </tr>
            """ % (orderID, userID, itemID, weight, address, preferredTime, totalCost)
            
        content += """
              </table>
    
              <br />
            <a href="/additem">Click here to add an item to the list of products</a> <br /> <br />
            <a href="/">Click here to go to home page</a> <br /> <br /> <br />
            <a href="/reset">Click here to reset all tables and initialize with default values</a>
          </body>
        </html>
        """
        
        self.response.write(content)
           
# This class resets the databases and shows a response to user
class ResetPage(webapp2.RequestHandler):
    def get(self):
        resetDBs()
        time.sleep(3)
        initializeDBs()
        self.response.write("""<html><body> 
        <head>
        <title>Online Store -- Reset</title>
        <style>
        body {
            font-family: Verdana, Helvetica, sans-serif;
            background-color: #DDDDDD;
        }
        </style>
      </head>
      <p> All tables has been reset and initialized with default values </p>
        <br /> <a href="/">Click here to go to home page</a>
        </body></html>""")
        
# This is the main class which is placed at the root of the site.
class MainPage(webapp2.RequestHandler):
    def get(self):
        #resetDBs()
        
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in</a> or continue as guest.' %
                        users.create_login_url('/'))
            
            
        self.response.write("<html><body>")
        self.response.out.write("<p> %s </p>" % greeting)
        
        
        if checkIfTablesExist() == True:
            #self.response.write("<p> exist <p> </br>")
            print "db exist"
        else:
            #self.response.write("<p> dosen't exist <p> </br>")
            print "db doesn't exist. initing now."
            initializeDBs()
        
        #self.response.write("</body></html>")
        self.response.write(printMainPage())
        
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/order', OrderPage),
    ('/report', ReportPage),
    ('/admin', AdminPage),
    ('/reset', ResetPage),
    ('/additem', AddItemPage)
], debug=True)




