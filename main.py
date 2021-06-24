import csv
from os import path
import re
import datetime
from flask import Flask
import requests
import json
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)
CORS(app)

invoice_args = reqparse.RequestParser()
invoice_args.add_argument('index', type=int)

class Home(Resource):
    def get(self):
        return {'msg': "yoooooooooooo"}

class GLCode(Resource):

    def post(self):
        f = datetime.datetime.now().strftime("%Y_%m_%d-%H")
        fieldnames = ['Company', 'Vendor Number', 'Invoice Number', 'Debit Memo',
                      'Invoice Date', 'Terms Code', 'Due Date', 'Apply Date', 'GL Account']

        args = invoice_args.parse_args()
        doc_id = args["index"]
        headers = {'Accept': 'application/json',
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"}
        url = f'https://prt.docuware.cloud/DocuWare/Platform/Account/LogOn?returnUrl=/DocuWare/Platform/FileCabinets/e0a146d7-197c-4b21-8e7c-f3a137a3093a/Documents/{doc_id}'

        datalog = {'Username': 'joseph', 'Password': 'admin1234',
                   'Organization': 'PRT Growing Services', 'HostId': 'this_is_a_test'}

        try:
            req = requests.post(url, data=datalog, headers=headers)
            data = json.loads(req.text)
            my_dict = {}
            for item in data["Fields"][43]['Item']['Row']:
                try:
                    my_dict['Company'] = data['Fields'][28]['Item']
                except:
                    my_dict['Company'] = ''
                try:
                    my_dict['VendorNumVendorID'] = data['Fields'][11]['Item']
                except:
                    my_dict['VendorNumVendorID'] = ''
                try:
                    my_dict['InvoiceNum'] = data['Fields'][13]['Item']
                except:
                    my_dict['InvoiceNum'] = ''
                try:
                    my_dict['DebitMemo'] = data['Fields'][32]['Item']
                except:
                    my_dict['DebitMemo'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][33]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['InvoiceDate'] = dateStr
                except:
                    my_dict['InvoiceDate'] = ''
                try:
                    my_dict['TermsCode'] = data['Fields'][18]['Item']
                except:
                    my_dict['TermsCode'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][34]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['DueDate'] = dateStr
                except:
                    my_dict['DueDate'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][38]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['ApplyDate'] = dateStr
                except:
                    my_dict['ApplyDate'] = ''
                try:
                    my_dict['GL Account'] = item['ColumnValue'][2]['Item']
                except:
                    my_dict['GL Account'] = ''
                
                my_dict['RateGrpCode'] = 'MAIN'
                my_dict['APInvDtl#LineType'] = 'M'

                try:
                    my_dict['ScrDocInvoiceVendorAmt'] = 'total'
                except:
                    my_dict['ScrDocInvoiceVendorAmt'] = ''
                
                try:
                    my_dict['APInvDtl#InvoiceLine'] = 'index of line item'
                except:
                    my_dict['APInvDtl#InvoiceLine'] = ''
                my_dict['APInvDtl#InvoiceLine'] = 1
                my_dict['APInvDtl#DocUnitCost'] = 500
                my_dict['APInvDtl#PUM'] = 500
                my_dict['APInvDtl#ScrVendorQty'] = 500
                my_dict['APInvExpTGLC#GLAccount'] = "profileCenter, GL code, phaseCode"
                my_dict['APInvExpTGLC#IsExternalCompany'] = 'intercompany'

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
            return {'msg': 'success'}, 200
        except ConnectionError:
            return {'err': 'there is a connection problem'}, 503
        except KeyError:
            return {'err': 'Document does not exist'}, 404
        except:
            return {'err': 'Unknown error'}, 500


api.add_resource(GLCode, '/invoice')
api.add_resource(Home, '/home')


if __name__ == '__main__':
    app.run(debug=True)
