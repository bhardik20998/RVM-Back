from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import warnings
import openpyxl
from datetime import datetime
import re
import matplotlib.pyplot as plt
import os
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
import numpy as np
import json
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

client = MongoClient('mongodb://localhost:27017/')
db = client['RVM']


def get_all_documents(collectionName):
    try:
        collection = db[collectionName]
        documents = list(collection.find({}))
        return documents
    except Exception as e:
        return ({'error': str(e)})


def save_data(documentsArray, collectionName):
    try:
        collection = db[collectionName]

        # Insert the dictionary as a document

        result = collection.insert_many(documentsArray)
        return result
    except Exception as e:
        print(e)


# def calculate_Y(input_data, scheme, base_data):
#     if scheme == 'existingModel':
#         y_pred = fit_existing(input_data, scheme, base_data)
#     elif scheme == 'newModel':
#         y_pred = fit_new(input_data, scheme, base_data)
#     return y_pred


# def fit_new(input_data, scheme, base_data):
#     X = base_data[['city', 'Make', 'body_type',
#                   'odometer_reading', 'vehicle_age']]

#     Y = base_data[['Residual_Value']]
#     X = pd.get_dummies(X, columns=list(X.select_dtypes(
#         include=['object']).columns), drop_first=True)
#     input_data = pd.get_dummies(input_data, columns=list(
#         input_data.select_dtypes(include=['object']).columns), drop_first=True)
#     X = sm.add_constant(X)
#     input_data = sm.add_constant(input_data)
#     X = X[X.columns.intersection(input_data.columns)]
#     input_data = input_data[input_data.columns.intersection(X.columns)]
#     lr_model = LinearRegression()
#     lr_model.fit(X, Y)
#     y_pred = lr_model.predict(input_data)
#     return y_pred


# def fit_existing(input_data, scheme, base_data):
#     X = base_data[['city', 'Model', 'odometer_reading', 'vehicle_age']]
#     Y = base_data[['Residual_Value']]
#     X = pd.get_dummies(X, columns=list(X.select_dtypes(
#         include=['object']).columns), drop_first=True)
#     input_data = pd.get_dummies(input_data, columns=list(
#         input_data.select_dtypes(include=['object']).columns), drop_first=True)
#     X = sm.add_constant(X)
#     input_data = sm.add_constant(input_data)
#     X = X[X.columns.intersection(input_data.columns)]
#     input_data = input_data[input_data.columns.intersection(X.columns)]
#     lr_model = LinearRegression()
#     lr_model.fit(X, Y)
#     y_pred = lr_model.predict(input_data)
#     return y_pred


def remove_object_id(documents):
    for document in documents:
        if '_id' in document:
            del document['_id']
    return documents


warnings.filterwarnings("ignore")
pd.set_option("display.max_rows", None)
pd.set_option('display.max_columns', None)
pd.options.display.float_format = "{:.2f}".format


# In[134]:


# Create a function to assign cities to buckets
def categorize_city(city):
    if city in city_buck_1:
        return 'bucket_1'
    elif city in city_buck_2:
        return 'bucket_2'
    elif city in city_buck_3:
        return 'bucket_3'
    elif city in city_buck_4:
        return 'bucket_4'
    elif city in city_buck_5:
        return 'bucket_5'
    elif city in city_buck_6:
        return 'bucket_6'
    elif city in city_buck_7:
        return 'bucket_7'
    elif city in city_buck_8:
        return 'bucket_8'
    elif city in city_buck_9:
        return 'bucket_9'
    elif city in city_buck_10:
        return 'bucket_10'
    elif city in city_buck_11:
        return 'bucket_11'
    elif city in city_buck_12:
        return 'bucket_12'
    elif city in city_buck_13:
        return 'bucket_13'
    elif city in city_buck_14:
        return 'bucket_14'
    else:
        return 'Others'


# City Buckets
city_buck_1 = ["tirur", "kalpetta", "shimoga", "calicut", "malappuram", "kannur", "palghat",
               "kumbakonam", "trivandrum", "coimbatore", "tiruchirapalli", "kasaragod"]
city_buck_2 = ["tirunelveli", "kollam", "madurai", "trichur", "puducherry", "tiruppur",
               "salem", "muvattupuzha"]
city_buck_3 = ['ernakulam', 'kottayam', 'vellore', 'erode',
               'mangalore', 'udupi', 'nellore', 'guntur', 'amritsar', 'karimnagar']
city_buck_4 = ['tirupati', 'kalaburgi',
               'anantapur', 'vijayawada', 'jalgaon', 'darjeeling', 'ahmedabad', 'kurnool', 'bilaspur', 'rajahmundry', 'trichy']
city_buck_5 = ['visakhapatnam', 'tumkur', 'jammu', 'ludhiana', 'panchkula', 'hubli', 'chhindwara', "pune",
               "jalandhar", "guwahati", "surat", "indore", "sriganganagar", "panvel"]
city_buck_6 = ["thane", "vapi", "mohali", "patiala", "satna", "warangal", "karnal", "dhanbad", "latur",
               "lucknow", "raipur", "nashik", "cochin", "dehradun", "sangrur", "baramati"]
city_buck_7 = ["hissar", "solan", "bhopal", "chandigarh", "howrah", "mysore", "vadodara",
               "jaipur", "ambala", "ranchi", "bhilwara"]
city_buck_8 = ["faridabad", "panipat", "yamuna nagar", "varanasi", "jodhpur", "cuttack", "patna", "rohtak", "kolkata",
               "udaipur", "gulbarga", "allahabad", "nagpur"]
city_buck_9 = ["gurgaon", "ghaziabad", "agra", "noida", "meerut", "kanpur"]
city_buck_10 = ["chennai"]
city_buck_11 = ["hyderabad"]
city_buck_12 = ["bangalore"]
city_buck_13 = ["mumbai"]
city_buck_14 = ["delhi"]


# Function to convert strings to lowercase
def lower_if_string(x):
    if isinstance(x, str):
        return x.lower()
    else:
        return x

# Function to strip extra spaces in strings


def strip_string(x):
    if isinstance(x, str):
        return x.strip()
    else:
        return x


# In[139]:


def manipulation(data):
    # Apply the function to a DataFrame or Series
    if isinstance(data, pd.DataFrame):
        data = data.applymap(lower_if_string)
        data = data.applymap(strip_string)
    elif isinstance(data, pd.Series):
        data = data.map(lower_if_string)
        data = data.map(strip_string)
    data['vehicle_age'] = data['vehicle_age'].astype(int)
    data['odometer_reading'] = data['odometer_reading'].astype(int)
    data['vehicle_age'] = data['vehicle_age'].apply(
        lambda x: np.maximum(x, 1))  # 96
    # data['retail'] = np.where(data['odometer_reading']
    #                           > data['vehicle_age'] * 35000, '0', '1')
    # Apply the categorization function to the 'city' column in your data
    data['city'] = data['city'].apply(categorize_city)
    return data


# In[140]:


def fit(input_data, base_data):
    X = base_data.drop(columns={'Residual_Value'})
    Y = base_data[['Residual_Value']]
    input_data = manipulation(input_data)
    input_data_temp = pd.get_dummies(input_data, columns=list(
        input_data.select_dtypes(include=['object']).columns))
    input_data = pd.get_dummies(input_data, columns=list(
        input_data.select_dtypes(include=['object']).columns), drop_first=True)
    dropped_dummies = list(
        set(input_data_temp.columns) - set(input_data.columns))
    X = pd.get_dummies(X, columns=list(
        X.select_dtypes(include=['object']).columns))
    X = X.drop(columns=dropped_dummies)
    X = sm.add_constant(X)

    input_data = sm.add_constant(input_data)
    X, input_data = X.align(input_data, axis=1, fill_value=0)
    lr_model = LinearRegression()
    lr_model.fit(X, Y)
    y_pred = lr_model.predict(input_data)
    y_pred = np.maximum(y_pred, 0)

    return y_pred


# In[141]:


def calculate_Y(input_data, scheme, base_data):

    # base_data['retail'] = np.where(
    #     base_data['odometer_reading'] > base_data['vehicle_age'] * 35000, 'Commercial', 'Retail')

    if scheme == 'existingModel':
        base_data = manipulation(base_data)

        base_data = base_data[[
            'city', 'Model', 'odometer_reading', 'vehicle_age', 'retail', 'Residual_Value']]
        input_data = input_data[['city', 'Model',
                                 'odometer_reading', 'vehicle_age']]

        y_pred = fit(input_data, base_data)

        final_y_pred = []

        # for i in range(len(y_pred) + len(model_not_in_base)):
        #     if index_counter < len(model_not_in_base) and i == model_not_in_base[index_counter]:
        #         final_y_pred.append(0)
        #         index_counter += 1
        #     else:
        #         final_y_pred.append(y_pred[i - index_counter])
        y_scaled_pred = y_pred*0.81
    elif scheme == 'newModel':
        base_data = manipulation(base_data)

        base_data = base_data[['city', 'Make', 'body_type',
                               'odometer_reading', 'vehicle_age', 'retail', 'Residual_Value']]
        input_data = input_data[['city', 'Make',
                                 'body_type', 'odometer_reading', 'vehicle_age']]

        y_pred = fit(input_data, base_data)

        # for index in make_not_in_base:
        #     if 0 <= index < len(y_pred):
        #         y_pred[index] = 0
        # for index in bodytype_not_in_base:
        #     if 0 <= index < len(y_pred):
        #         y_pred[index] = 0
        y_scaled_pred = y_pred*0.83

    return np.round(y_pred, 2), np.round(y_scaled_pred, 2)