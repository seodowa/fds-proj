VALID_TABLE_NAMES = ["customer", "emergency_contact", "employee", "employee_designation", "employment_status", "menu", "mode_of_payment", "orders", "order_transactions", "restaurant"]
VAT = 1.12 # 12%


# TODO: TEST THESE FUNCTIONS

# this is for quick n easy sql statements
def execute_sql_stmt(conn, stmt, is_select_stmt=False):
    cursor = conn.cursor()
    cursor.execute(stmt)
    if is_select_stmt:
        return cursor.fetchone()
    conn.commit()


# READ 
def view_table(conn, tblname):
    cursor = conn.cursor()
    if tblname in VALID_TABLE_NAMES:
        cursor.execute(f"SELECT * FROM {tblname}")
    return [item for item in cursor]


def get_receipt_details(conn, order_id):
    cursor = conn.cursor()
    cursor.execute("SELECT orders.order_id, order_type_name, customer.first_name, customer.middle_name, customer.last_name, customer.suffix,\
                   customer.barangay_address, customer.city_address, customer.province_address, SUM(order_transactions.dish_price), \
                   SUM(tax), SUM(total_price), employee.first_name, employee.middle_name, employee.last_name, employee.suffix, \
                   order_transactions.date_time_of_order \
                   FROM orders INNER JOIN customer ON customer.customer_id = orders.customer_id \
                   INNER JOIN order_transactions ON orders.order_id = order_transactions.order_id \
                   INNER JOIN order_type ON order_type.id = order_transactions.order_type_id \
                   INNER JOIN mode_of_payment ON mode_of_payment.mode_of_payment_id = order_transactions.mode_of_payment_id \
                   INNER JOIN employee ON orders.employee_id = employee.employee_id \
                   INNER JOIN menu ON order_transactions.dish_id = menu.dish_id \
                   WHERE orders.order_id = %s", (order_id,))
    return cursor.fetchone()
    

# INSERT/CREATE DATA
def insert_menu_data(conn, dish_name, dish_price):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (dish_name, dish_price) VALUES (%s, %s)", (dish_name, dish_price))
    conn.commit()


def insert_customer_data(conn, restaurant_id, contact_number, 
                         email_address, barangay_address, 
                         city_address, province_address, 
                         postal_code_address, first_name, 
                         middle_name, last_name, suffix=None):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customer (restaurant_id, first_name, \
        middle_name, last_name, suffix, contact_number, \
        email_address, barangay_address, city_address, \
        province_address, postal_code_address) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (restaurant_id, first_name, middle_name, last_name, suffix, 
         contact_number, email_address, barangay_address, city_address, 
         province_address, postal_code_address))
    conn.commit()


def insert_emergency_contact_data(conn, contact_number, 
                         contact_alt_number, relationship_with_employee, 
                         barangay_address, city_address, province_address, 
                         postal_code_address, first_name, 
                         middle_name, last_name, suffix=None):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO emergency_contact (first_name, middle_name, last_name, \
                   suffix, contact_number, contact_alt_number, \
                   relationship_with_employee, barangay_address, \
                   city_address, province_address, postal_code_address) \
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (first_name, middle_name, last_name, suffix,
                    contact_number, contact_alt_number, relationship_with_employee,
                    barangay_address, city_address, province_address, postal_code_address))
    conn.commit()


def insert_employee_data(conn, restaurant_id, employee_designation_id,
                         employment_status_id, emergency_contact_id,
                         date_of_birth, employee_salary, employee_contact_number,
                         employee_email_address, employee_umid, employee_tin,
                         barangay_address, city_address, province_address,
                         postal_code_address, first_name, middle_name, last_name,
                         suffix=None):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employee (restaurant_id, \
                   employee_designation_id, employment_status_id, \
                   emergency_contact_id, first_name, middle_name, \
                   last_name, suffix, date_of_birth, employee_salary, \
                   employee_contact_number, employee_email_address, \
                   employee_umid, employee_tin, barangay_address, \
                   city_address, province_address, postal_code_address) \
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DATE(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (restaurant_id, employee_designation_id, employment_status_id, 
                    emergency_contact_id, first_name, middle_name, last_name, suffix, 
                    date_of_birth, employee_salary, employee_contact_number, employee_email_address, 
                    employee_umid, employee_tin, barangay_address, city_address, 
                    province_address, postal_code_address))
    conn.commit()


def insert_employee_designation_data(conn, designation_name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employee_designation (designation_name) \
                   VALUES (%s)", (designation_name,))
    conn.commit()


def insert_employment_status_data(conn, employment_status):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employment_status (employment_status) \
                   VALUES (%s)", (employment_status,))
    conn.commit()


def insert_mode_of_payment_data(conn, mode_of_payment_name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mode_of_payment (mode_of_payment_name) \
                   VALUES (%s)", (mode_of_payment_name,))
    conn.commit()


def insert_orders_data(conn, customer_id, employee_id):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_id, employee_id) \
                   VALUES (%s, %s)", (customer_id, employee_id))
    conn.commit()



def insert_order_transactions_data(conn, order_id, dish_id, mode_of_payment_id, order_type_id,
                                   dish_quantity):
    cursor = conn.cursor()

    cursor.execute("SELECT dish_price, (dish_price * %s) * %s FROM menu WHERE dish_id = %s", (VAT, dish_quantity, dish_id))
    prices = cursor.fetchone()
    
    cursor.execute("SELECT NOW()")
    date_time = cursor.fetchone()[0]

    total_before_tax = prices[0] * dish_quantity
    added_vat = total_before_tax * (VAT-1)

    cursor.execute("INSERT INTO order_transactions (order_id, dish_id, \
                   mode_of_payment_id, order_type_id, dish_price, dish_quantity, total_before_tax, value_added_tax, total_price, date_time_of_order) \
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (order_id, dish_id, mode_of_payment_id, order_type_id, prices[0],
                    dish_quantity, total_before_tax, added_vat, prices[1], date_time))
    conn.commit()


def insert_order_type_data(conn, order_type_name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO order_type (order_type_name) VALUES (%s)", (order_type_name,))
    conn.commit()


def insert_restaurant_data(conn, restaurant_name, contact_number,
                           restaurant_tin, barangay_address, city_address,
                           province_address, postal_code_address):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO restaurant (restaurant_name, contact_number, \
                   restaurant_tin, barangay_address, city_address, \
                   province_address, postal_code_address) \
                   VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                   (restaurant_name, contact_number, restaurant_tin,
                    barangay_address, city_address, province_address, postal_code_address))
    conn.commit()


# UPDATE
def update_menu_data(conn, dish_id, dish_name, dish_price):
    cursor = conn.cursor()
    cursor.execute("UPDATE menu SET dish_name = %s, dish_price = %s WHERE dish_id = %s", (dish_name, dish_price, dish_id))
    conn.commit()


def update_customer_data(conn, customer_id, restaurant_id,
                         first_name, middle_name, last_name,
                         suffix, contact_number, email_address,
                         barangay_address, city_address,
                         province_address, postal_code_address):
    cursor = conn.cursor()
    cursor.execute("UPDATE customer SET restaurant_id = %s, \
                   first_name = %s, middle_name = %s, last_name = %s, \
                   suffix = %s, contact_number = %s, email_address = %s, \
                   barangay_address = %s, city_address = %s, \
                   province_address = %s, postal_code_address = %s \
                   WHERE customer_id = %s", (restaurant_id,
                         first_name, middle_name, last_name,
                         suffix, contact_number, email_address,
                         barangay_address, city_address,
                         province_address, postal_code_address, customer_id))
    conn.commit()


def update_emergency_contact_data(conn, ec_id, first_name,
                                  middle_name, last_name, suffix, contact_number,
                                  contact_alt_number, relationship_with_employee,
                                  barangay_address, city_address, province_address,
                                  postal_code_address):
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_contact SET \
                   first_name = %s, middle_name = %s, last_name = %s, \
                   suffix = %s, contact_number = %s, contact_alt_number = %s, \
                   relationship_with_employee = %s, barangay_address = %s, \
                   city_address = %s, province_address = %s, postal_code_address = %s \
                   WHERE ec_id = %s", (first_name, middle_name, last_name,
                                       suffix, contact_number, contact_alt_number,
                                       relationship_with_employee, barangay_address, city_address,
                                       province_address, postal_code_address, ec_id))
    conn.commit()


def update_employee_data(conn, employee_id, restaurant_id, employee_designation_id,
                         employment_status_id, emergency_contact_id, first_name,
                         middle_name, last_name, suffix, date_of_birth, 
                         employee_salary, employee_contact_number, employee_email_address,
                         employee_umid, employee_tin, barangay_address, city_address,
                         province_address, postal_code_address):
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_contact SET restaurant_id = %s, \
                   employee_designation_id = %s, employment_status_id = %s, \
                   emergency_contact_id = %s, first_name = %s, middle_name = %s, \
                   last_name = %s, suffix = %s, date_of_birth = %s, employee_salary = %s \
                   employee_contact_number = %s, employee_email_address = %s, employee_umid = %s \
                   employee_tin = %s, barangay_address = %s, city_address = %s, \
                   province_address = %s, postal_code_address = %s \
                   WHERE employee_id = %s", (restaurant_id, employee_designation_id,
                         employment_status_id, emergency_contact_id, first_name,
                         middle_name, last_name, suffix, date_of_birth, 
                         employee_salary, employee_contact_number, employee_email_address,
                         employee_umid, employee_tin, barangay_address, city_address,
                         province_address, postal_code_address, employee_id))
    conn.commit()


def update_employee_designation_data(conn, designation_id, designation_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE employee_designation SET designation_name = %s \
                   WHERE designation_id = %s", (designation_name, designation_id))
    conn.commit()


def update_employment_status_data(conn, employment_status_id, employment_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE employement_status SET employment_status = %s \
                   WHERE employment_status_id = %s", (employment_status, employment_status_id))
    conn.commit()


def update_mode_of_payment_data(conn, mode_of_payment_id, mode_of_payment_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE mode_of_payment SET mode_of_payment_name = %s WHERE mode_of_payment_id = %s", 
                   (mode_of_payment_name, mode_of_payment_id))
    conn.commit()


def update_orders_data(conn, order_id, customer_id, employee_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET customer_id = %s, employee_id = %s \
                   WHERE order_id = %s", (customer_id, employee_id, order_id))
    conn.commit()


def update_order_transactions_data(conn, order_transaction_id, order_id,
                                   dish_id, mode_of_payment_id, order_type_id, dish_price, dish_quantity, total_before_tax,
                                   value_added_tax, total_price, date_time_of_order):
    cursor = conn.cursor()
    cursor.execute("UPDATE order_transactions SET order_id = %s, \
                   dish_id = %s, mode_of_payment_id = %s, order_type_id = %s, dish_price = %s, dish_quantity = %s, total_before_tax = %s, \
                   value_added_tax = %s, total_price = %s, date_time_of_order = %s WHERE \
                   order_transaction_id = %s", (order_id, dish_id, mode_of_payment_id, order_type_id, dish_price,
                                                dish_quantity, total_before_tax, value_added_tax, total_price, date_time_of_order,
                                                order_transaction_id))
    conn.commit()


def update_order_type_data(conn, id, order_type_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE order_type SET order_type_name = %s WHERE id = %s", (order_type_name, id))
    conn.commit()


def update_restaurant_data(conn, restaurant_id, restaurant_name, contact_number,
                           restaurant_tin, barangay_address, city_address, 
                           province_address, postal_code_address):
    cursor = conn.cursor()
    cursor.execute("UPDATE restaurant SET restaurant_name = %s, contact_number = %s, \
                   restaurant_tin = %s, barangay_address = %s, city_address = %s, \
                   province_address = %s, postal_code_address = %s \
                   WHERE restaurant_id = %s", (restaurant_name, contact_number,
                           restaurant_tin, barangay_address, city_address, 
                           province_address, postal_code_address, restaurant_id))
    conn.commit()


# DELETE
def delete_from_menu(conn, dish_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE dish_id = %s", (dish_id,))
    conn.commit()


def delete_from_customer(conn, customer_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
    conn.commit()


def delete_from_emergency_contact(conn, ec_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emergency_contact WHERE ec_id = %s", (ec_id,))
    conn.commit()

def delete_from_employee(conn, employee_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))
    conn.commit()

def delete_from_employee_designation(conn, designation_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee_designation WHERE designation_id = %s", (designation_id,))
    conn.commit()

def delete_from_employment_status(conn, employement_status_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employment_status WHERE employment_status_id = %s", (employement_status_id,))
    conn.commit()

def delete_from_mode_of_payment(conn, mode_of_payment_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mode_of_payment WHERE mode_of_payment_id = %s", (mode_of_payment_id,))
    conn.commit()

def delete_from_orders(conn, order_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    conn.commit()

def delete_from_order_transactions(conn, order_transaction_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_transactions WHERE order_transaction_id = %s", (order_transaction_id,))
    conn.commit()


def delete_from_order_type(conn, id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_type WHERE id = %s", (id,))
    conn.commit()


def delete_from_restaurant(conn, restaurant_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restaurant WHERE restaurant_id = %s", (restaurant_id,))
    conn.commit()


# extra funcs


if __name__ == "__main__":
    pass
