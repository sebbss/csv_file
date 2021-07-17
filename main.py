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
        return {'msg': "hello"}

class GLCode(Resource):
    # def get(self):
    #     xml = 'foo'
    #     resp = app.make_response(xml)
    #     resp.mimetype = "text/xml"
    #     return resp

    def post(self):
        f = datetime.datetime.now().strftime("%Y_%m_%d")
        fieldnames = ['Company', 'VendorNumVendorID', 'BankID', 'InvoiceNum',
                      'DebitMemo', 'InvoiceDate', 'TermsCode', 'DueDate', 'GroupID', 'Description','CurrencyCode',
                      'RateGrpCode', 'ApplyDate','APInvDtl#LineType','ScrDocInvoiceVendorAmt','APInvDtl#InvoiceLine','APInvExp#InvExpSeq',
                      'APInvDtl#DocUnitCost','APInvDtl#PUM','APInvDtl#ScrVendorQty','APInvExpTGLC#IsExternalCompany',
                      'APInvExp#ExtCompanyID', 'GlbAPIETGLC#GLAccount','APInvExpTGLC#GLAccount']

        args = invoice_args.parse_args()
        doc_id = args["index"]
        headers = {'Accept': 'application/json',
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"}
        url = f'https://prt.docuware.cloud/DocuWare/Platform/Account/LogOn?returnUrl=/DocuWare/Platform/FileCabinets/e0a146d7-197c-4b21-8e7c-f3a137a3093a/Documents/{doc_id}'

        datalog = {'Username': 'laurie', 'Password': 'admin1234',
                   'Organization': 'PRT Growing Services', 'HostId': 'this_is_a_test'}

        try:
            req = requests.post(url, data=datalog, headers=headers)
            data = json.loads(req.text)
            my_dict = {}
            try:
                if data['Fields'][31]['Item']:

                    
                    for index, item in enumerate(data["Fields"][48]['Item']['Row'], 1):
                        try:
                            my_dict['Company'] = data['Fields'][28]['Item']
                        except:
                            my_dict['Company'] = ''
                        try:
                            my_dict['VendorNumVendorID'] = data['Fields'][11]['Item']
                        except:
                            my_dict['VendorNumVendorID'] = ''
                        try:
                            my_dict['BankID'] = data['Fields'][30]['Item']
                        except:
                            my_dict['BankID'] = ''
                        try:
                            my_dict['InvoiceNum'] = data['Fields'][13]['Item']
                        except:
                            my_dict['InvoiceNum'] = ''
                        try:
                            my_dict['DebitMemo'] = data['Fields'][32]['Item']
                        except:
                            my_dict['DebitMemo'] = 'No'
                        try:
                            date = int(re.findall(
                                "\d+", data['Fields'][37]['Item'])[0])
                            dateStr = datetime.datetime.fromtimestamp(date/1000)
                            my_dict['InvoiceDate'] = dateStr.strftime('%m-%d-%Y')
                        except:
                            my_dict['InvoiceDate'] = ''
                        try:
                            my_dict['TermsCode'] = data['Fields'][18]['Item']
                        except:
                            my_dict['TermsCode'] = ''
                        try:
                            date = int(re.findall(
                                "\d+", data['Fields'][38]['Item'])[0])
                            dateStr = datetime.datetime.fromtimestamp(date/1000)
                            my_dict['DueDate'] = dateStr.strftime('%m-%d-%Y')
                        except:
                            my_dict['DueDate'] = ''
                        my_dict['GroupID'] = f
                        try:
                            my_dict['Description'] = data['Fields'][36]['Item']
                        except:
                            my_dict['Description'] = ''
                        try:
                            my_dict['CurrencyCode'] = data['Fields'][33]['Item']
                        except:
                            my_dict['CurrencyCode'] = ''
                        my_dict['RateGrpCode'] = "MAIN"
                        try:
                            date = int(re.findall(
                                "\d+", data['Fields'][42]['Item'])[0])
                            dateStr = datetime.datetime.fromtimestamp(date/1000)
                            my_dict['ApplyDate'] = dateStr.strftime('%m-%d-%Y')
                        except:
                            my_dict['ApplyDate'] = ''
                        my_dict['APInvDtl#LineType'] = 'M'
                        try:
                            my_dict['ScrDocInvoiceVendorAmt'] = data['Fields'][46]['Item']
                        except:
                            my_dict['ScrDocInvoiceVendorAmt'] = ''
                        my_dict['APInvDtl#InvoiceLine'] = index
                        my_dict['APInvExp#InvExpSeq'] = 1
                        try:
                            try:
                                if(item['ColumnValue'][4]['Item']=='BC'):
                                    my_dict['APInvDtl#DocUnitCost'] = float(item['ColumnValue'][7]['Item'])*1.07
                                if(item['ColumnValue'][4]['Item']=='Saskatchewan'):
                                    my_dict['APInvDtl#DocUnitCost'] = float(item['ColumnValue'][7]['Item'])*1.06
                            except:
                                my_dict['APInvDtl#DocUnitCost'] = item['ColumnValue'][7]['Item']
                        except:
                            my_dict['APInvDtl#DocUnitCost'] = ''
                        try:
                            my_dict['APInvDtl#PUM'] = item['ColumnValue'][6]['Item']
                        except:
                            my_dict['APInvDtl#PUM'] = 'EA'
                        try:
                            my_dict['APInvDtl#ScrVendorQty'] = item['ColumnValue'][9]['Item']
                        except:
                            my_dict['APInvDtl#ScrVendorQty'] = 1
                        
                        my_dict['APInvExpTGLC#GLAccount'] = ''
                        
                        my_dict['APInvExpTGLC#IsExternalCompany'] = True
                        
                        try:
                            my_dict['APInvExp#ExtCompanyID'] = data['Fields'][28]['Item']
                        except:
                            my_dict['APInvExp#ExtCompanyID'] = ''
                        try:
                            my_dict['GlbAPIETGLC#GLAccount'] = "{}-{}-{}".format(
                                item['ColumnValue'][1]['Item'],item['ColumnValue'][2]['Item'],item['ColumnValue'][3]['Item'])
                        except:
                            my_dict['GlbAPIETGLC#GLAccount'] = ''
                        
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
            
            except KeyError:
                for index, item in enumerate(data["Fields"][48]['Item']['Row'], 1):
                    try:
                        my_dict['Company'] = data['Fields'][28]['Item']
                    except:
                        my_dict['Company'] = ''
                    try:
                        my_dict['VendorNumVendorID'] = data['Fields'][11]['Item']
                    except:
                        my_dict['VendorNumVendorID'] = ''
                    try:
                        my_dict['BankID'] = data['Fields'][30]['Item']
                    except:
                        my_dict['BankID'] = ''
                    try:
                        my_dict['InvoiceNum'] = data['Fields'][13]['Item']
                    except:
                        my_dict['InvoiceNum'] = ''
                    try:
                        my_dict['DebitMemo'] = data['Fields'][32]['Item']
                    except:
                        my_dict['DebitMemo'] = 'No'
                    try:
                        date = int(re.findall(
                            "\d+", data['Fields'][37]['Item'])[0])
                        dateStr = datetime.datetime.fromtimestamp(date/1000)
                        my_dict['InvoiceDate'] = dateStr.strftime('%m-%d-%Y')
                    except:
                        my_dict['InvoiceDate'] = ''
                    try:
                        my_dict['TermsCode'] = data['Fields'][18]['Item']
                    except:
                        my_dict['TermsCode'] = ''
                    try:
                        date = int(re.findall(
                            "\d+", data['Fields'][38]['Item'])[0])
                        dateStr = datetime.datetime.fromtimestamp(date/1000)
                        my_dict['DueDate'] = dateStr.strftime('%m-%d-%Y')
                    except:
                        my_dict['DueDate'] = ''
                    my_dict['GroupID'] = f
                    try:
                        my_dict['Description'] = data['Fields'][36]['Item']
                    except:
                        my_dict['Description'] = ''
                    try:
                        my_dict['CurrencyCode'] = data['Fields'][33]['Item']
                    except:
                        my_dict['CurrencyCode'] = ''
                    my_dict['RateGrpCode'] = "MAIN"
                    try:
                        date = int(re.findall(
                            "\d+", data['Fields'][42]['Item'])[0])
                        dateStr = datetime.datetime.fromtimestamp(date/1000)
                        my_dict['ApplyDate'] = dateStr.strftime('%m-%d-%Y')
                    except:
                        my_dict['ApplyDate'] = ''
                    my_dict['APInvDtl#LineType'] = 'M'
                    try:
                        my_dict['ScrDocInvoiceVendorAmt'] = data['Fields'][46]['Item']
                    except:
                        my_dict['ScrDocInvoiceVendorAmt'] = ''
                    my_dict['APInvDtl#InvoiceLine'] = index
                    my_dict['APInvExp#InvExpSeq'] = 1
                    try:
                        try:
                            if(item['ColumnValue'][4]['Item']=='BC'):
                                my_dict['APInvDtl#DocUnitCost'] = float(item['ColumnValue'][7]['Item'])*1.07
                            if(item['ColumnValue'][4]['Item']=='Saskatchewan'):
                                my_dict['APInvDtl#DocUnitCost'] = float(item['ColumnValue'][7]['Item'])*1.06
                        except:
                            my_dict['APInvDtl#DocUnitCost'] = item['ColumnValue'][7]['Item']
                    except:
                        my_dict['APInvDtl#DocUnitCost'] = ''
                    try:
                        my_dict['APInvDtl#PUM'] = item['ColumnValue'][6]['Item']
                    except:
                        my_dict['APInvDtl#PUM'] = 'EA'
                    try:
                        my_dict['APInvDtl#ScrVendorQty'] = item['ColumnValue'][9]['Item']
                    except:
                        my_dict['APInvDtl#ScrVendorQty'] = 1
                    try:
                        my_dict['APInvExpTGLC#GLAccount'] = "{}-{}-{}".format(
                            item['ColumnValue'][1]['Item'],item['ColumnValue'][2]['Item'],item['ColumnValue'][3]['Item'])
                    except:
                        my_dict['APInvExpTGLC#GLAccount'] = ''
                    
                    my_dict['APInvExpTGLC#IsExternalCompany'] = False
                    
                    my_dict['APInvExp#ExtCompanyID'] = ''
                    
                    my_dict['GlbAPIETGLC#GLAccount'] = ''

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
            return {'err': 'Document does not exist'}, 200
        except:
            return {'err': 'Unknown error'}, 500


api.add_resource(GLCode, '/invoice')
api.add_resource(Home, '/home')


if __name__ == '__main__':
    app.run(debug=True)
