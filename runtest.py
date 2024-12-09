import db_api, mysql.connector

connection = mysql.connector.connect(host="localhost", user="root", password="", database="kentucky")

"""
tist = db_api.get_receipt_details(connection, 1)
print("resibo")
for item in tist:
    if item == "order":
        print("order:")
        for order, price in tist[item]:
            print(f"\t{order: <60}{price: >5} php")
        continue
        
    print(f"{item}: {tist[item]}")"""

for order in db_api.view_orders(connection, 1):
    print(order)