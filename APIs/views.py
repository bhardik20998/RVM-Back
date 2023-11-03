from django.shortcuts import render
from django.http import JsonResponse
import json
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
from bson import json_util
from .functions import save_data, calculate_Y, get_all_documents, remove_object_id
# Create your views here
import math
import numpy as np

client = MongoClient('mongodb://localhost:27017/')
db = client['RVM']


def DeleteMasterData(request):
    try:
        db['master_data'].delete_many({})
        return JsonResponse({'message': 'Done'})

    except Exception as e:
        return JsonResponse({"error": e})


def SaveData(request):
    try:
        data = json.loads((request.body).decode('utf-8'))

        # Check if data is a dictionary with 'dataRows' key
        if not isinstance(data, dict) or 'dataRows' not in data:
            return JsonResponse({'error': 'Invalid data format'})

        # Extract 'dataRows' list
        column_names = data['columnNames']

        # Extract data rows
        data_rows = data['dataRows']

        documents = []

        # Iterate through data rows and create a document for each row
        for row in data_rows:
            document = {}
            for i, column_name in enumerate(column_names):
                # Assign the value from the row to the corresponding column name
                document[column_name] = row[i]
            documents.append(document)

        # Check if 'dataRows' is a list and not empty
        if not isinstance(data_rows, list) or not data_rows:
            return JsonResponse({'error': 'Invalid data format'})

        result = save_data(documents, 'master_data')
        save_data(documents, "calculation_logs")

        return JsonResponse({'message': 'Data inserted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def Calculating_Y_Single(request):
    try:
        model = json.loads(request.body.decode('utf-8'))
        scheme = model['ml_model']
        del model["ml_model"]
        data_as_arrays = {key: [value] for key, value in model.items()}
        input_data = pd.DataFrame(data_as_arrays)
        base_data = (pd.DataFrame(get_all_documents('base_data'))
                     ).drop('_id', axis=1)

        input_data['odometer_reading'] = input_data['odometer_reading'].astype(
            int)
        input_data['vehicle_age'] = input_data['vehicle_age'].astype(int)
        result, scaled_result = calculate_Y(input_data, scheme, base_data)
        input_data['Result'] = [None] * len(result)
        for x in range(len(result)):
            input_data['Result'][x] = result[x][0]
        payload = input_data.to_dict(orient='records')
        return JsonResponse({"y_pred": input_data['Result'][0], "scaled_y_pred": scaled_result[0][0]}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)})


def Calculating_Y(request):
    try:
        model = (request.body.decode('utf-8'))
        scheme = model
        data_as_arrays = get_all_documents('master_data')
        input_data = (pd.DataFrame(data_as_arrays)).drop('_id', axis=1)
        base_data = (pd.DataFrame(get_all_documents('base_data'))
                     ).drop('_id', axis=1)

        input_data['odometer_reading'] = input_data['odometer_reading'].astype(
            int)
        input_data['vehicle_age'] = input_data['vehicle_age'].astype(int)

        if (scheme == "newModel"):
            make_not_in_base = (check_input(input_data, base_data, 'Make'))
            input_data = input_data.drop(list(make_not_in_base))
            input_data = input_data.reset_index(drop=True)
            bodytype_not_in_base = (check_input(
                input_data, base_data, 'body_type'))
            input_data = input_data.drop(list(bodytype_not_in_base))
            input_data = input_data.reset_index(drop=True)
        else:
            make_not_in_base = (check_input(input_data, base_data, 'Model'))
            input_data = input_data.drop(list(make_not_in_base))
            input_data = input_data.reset_index(drop=True)

        result, scaled_result = calculate_Y(input_data, scheme, base_data)

        input_data['Predicted Residual Value'] = [None] * len(result)
        for x in range(len(result)):
            if (result[x][0] == 0):
                input_data['Predicted Residual Value'][x] = "Error: Outof bounds."
            else:
                input_data['Predicted Residual Value'][x] = result[x][0]

        input_data['Scaled Predicted Residual Value'] = [
            None] * len(scaled_result)
        for x in range(len(scaled_result)):
            if (scaled_result[x][0] == 0):
                input_data['Scaled Predicted Residual Value'][x] = "Error: Outof bounds."
            else:
                input_data['Scaled Predicted Residual Value'][x] = scaled_result[x][0]

        # input_data['Result'] = input_data['Result'].round(3)
        # input_data = input_data.rename(columns={'vehicle_age': 'Lease Tenure'})
        # input_data['Predicted Residual Value'] = (
        #     input_data['Predicted Residual Value'] * 100).astype(str) + '%'
        # input_data['Scaled Predicted Residual Value'] = (
        #     input_data['Scaled Predicted Residual Value'] * 100).astype(str) + '%'
        payload = input_data.to_dict(orient='records')
        return JsonResponse(payload, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)})


def check_input(input_data, base_data, column_name):
    # Get the rows not present in base_data
    rows_not_in_base = input_data[~input_data[column_name].isin(
        base_data[column_name])]

    # Convert the resulting DataFrame to a dictionary with index as key
    rows_dict = rows_not_in_base.to_dict(orient='index')

    return rows_dict


def FetchDetails(request):

    base_data = get_all_documents('base_data')
    for item in base_data:
        for key, value in item.items():
            if isinstance(value, float) and math.isnan(value):
                item[key] = None

    return JsonResponse(remove_object_id(base_data), safe=False)
