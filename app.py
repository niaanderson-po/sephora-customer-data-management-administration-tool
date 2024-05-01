from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

#Second Form: User_Data_Form
class  Customer:
    def __init__(self,userID, location, time_on_site, frequency, vip_status):
        self.userID = userID
        self.location = location
        self.time_on_site = time_on_site
        self.frequency = frequency
        self.vip_status = vip_status


    def __repr__(self):
        return f"Customer(userID={self.userID}, location={self.location}, time_on_site={self.time_on_site}, frequency={self.frequency}, vip_status={self.vip_status})"

class DataManager:
    def __init__(self, filename):
        self.filename = filename
        self.customers = self.load_customers()
    #JSON Handle
    def load_customers(self):
        try:
            #open, read, and get json file content
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                #get json file content
                customers_data = data.get('customers', [])
                customers = []
                for customer_data in customers_data:
                    #checks if each customer_data is a dict
                    if isinstance(customer_data, dict):
                        #if it is, the dict gets unpacked '**' so its key-values is turned into arg in a funct.
                        customer_obj = Customer(**customer_data)
                        customers.append(customer_obj)
                    else:
                        print(f"Ignoring invalid customer data: {customer_data}")
                return customers
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
            return []
    
    #SEARCH Handle (primary function for second form)
    def search_customers(self, **kwargs): #variable key word arguments 
        results = []
        #if no filters are entered return all data
        if not any(kwargs.values()):
            return self.customers
        

        for customer in self.customers:
            #assumes each customer meets all criteria in order to append to final displayed results
            match = True
            #iterate through the parameters
            for key, value in kwargs.items():
                #if no filter selected for a certain category then skip check since that criteria shouldnt be considered
                if value is None or value == "":
                    continue
                #Boolean conversion
                if key == 'vip_status':
                    value = value.lower() == 'true'
                #check if int values matchs if not match = false
                if key in ['time_on_site', 'frequency']:
                    if getattr(customer, key) is None or getattr(customer, key) != int(value):
                        match = False
                        break
                #if the value of other keys like location and vip status arent equal to the prameters key-value match = False
                else: 
                    if getattr(customer, key) != value:
                        match = False
                        break
            #if after heck the customer is still macth = true then display
            if match:
                results.append(customer)
        
        return results

    #RESET Handle
    def reset_data(self):
        return self.customers


#FLASK Routing
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select-data', methods=['POST'])
#first form on index
def select_data():
    data_type = request.form.get('data_type')

    if data_type == 'user_data':
        return redirect(url_for('user_data_form'))
    elif data_type == 'product_data':
        return redirect(url_for('product_data'))
    elif data_type == 'cart_data':
        return redirect(url_for('cart_data'))
    else:
        return "Invalid data type selected."

@app.route('/user-data-form')
def user_data_form():
    return render_template('user_data_form.html')
  
@app.route('/search', methods=['POST'])
#second form on second page
def search():
    location = request.form.get('location')
    time_on_site = request.form.get('time_on_site')
    frequency = request.form.get('frequency')
    vip_status = request.form.get('vip_status')

    data_manager = DataManager('users.json')

    if location or time_on_site or frequency or vip_status:  # Check if any filter is provided
        # use the search_customer def created
        results = data_manager.search_customers(location=location, time_on_site=time_on_site, frequency=frequency, vip_status=vip_status)
    else:
        # if no filters return all with the reset data def
        results = data_manager.reset_data()
    #return results from search on third page
    return render_template('results.html', results=results)

@app.route('/update', methods=['GET'])
def update():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)