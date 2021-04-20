import csv
from os import path
import datetime
from flask import Flask
import requests
import xmltodict
import json
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

invoice_args = reqparse.RequestParser()
invoice_args.add_argument('index', type=int)



class GLCode(Resource):
    
    def post(self):
        f = datetime.datetime.now().strftime("%Y_%m_%d-%H")
        fieldnames = ['supplier_code', 'invoice_number', 'remit_id', 'invoice_date', 'due_date', 'invoice_total']
        
        args = invoice_args.parse_args()
        doc_id = args["index"]
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"}
        url = f'https://prt.docuware.cloud/DocuWare/Platform/Account/LogOn?returnUrl=/DocuWare/Platform/FileCabinets/e0a146d7-197c-4b21-8e7c-f3a137a3093a/Documents/{doc_id}'

        datalog = {'Username':'laurie', 'Password':'admin1234', 'Organization':'PRT Growing Services'}
        req = requests.post(url, data=datalog, headers=headers)
        try:
            json_results = xmltodict.parse(req.text)
            fields = json_results['Document']['Fields']['Field']
            my_dict = {}

            for i, value in enumerate(fields, 1):
                if i == 12:
                    my_dict['supplier_code'] = value['String']
                if i == 14:
                    my_dict['invoice_number'] = value['String']
                if i == 32:
                    my_dict['remit_id'] = value['String']
                if i == 33:
                    my_dict['invoice_date'] = value['Date']
                if i == 34:
                    my_dict['due_date'] = value['Date']
                if i == 42:
                    my_dict['invoice_total'] = value['Decimal']
        except:
            return{'msg': 'failed to connect to docuware', 'status': 500}
        
        
        if path.isfile('{}.csv'.format(f)):
            my_file = open('{}.csv'.format(f), 'a')
            writer = csv.DictWriter(my_file, fieldnames=fieldnames)
            with my_file:
                writer.writerow(my_dict)
        else:
            my_file = open('{}.csv'.format(f), 'a')
            writer = csv.DictWriter(my_file, fieldnames=fieldnames)
            with my_file:
                writer.writeheader()
                writer.writerow(my_dict)
        my_file.close
        return {'msg': 'success'}
        
api.add_resource(GLCode, '/invoice')


if __name__ == '__main__':
   app.run(debug = True)
