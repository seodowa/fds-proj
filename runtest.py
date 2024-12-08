import db_api, mysql.connector

connection = mysql.connector.connect(host="localhost", user="root", password="", database="kentucky")



#print(db_api.get_receipt_details(connection, 1))
db_api.update_order_transactions_data()