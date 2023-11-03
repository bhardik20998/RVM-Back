import pandas as pd
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['RVM']
collection = db["base_data"]
# Insert the dictionary as a document

data = pd.read_excel(r'C:\Users\hardik\Downloads\RVM_Base_Data_Ver3.xlsx')
data = data.to_dict(orient='records')

# 'data' is now an array of dictionaries where each dictionary represents a row from the Excel file

result = collection.insert_many(data)
