import csv
from os import path
import re
import datetime
from flask import Flask
import requests
import json
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

invoice_args = reqparse.RequestParser()
invoice_args.add_argument('index', type=int)

class Home(Resource):
    def get(self):
        return {'msg': 'we re here'}

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
                    my_dict['Vendor Number'] = data['Fields'][11]['Item']
                except:
                    my_dict['Vendor Number'] = ''
                try:
                    my_dict['Invoice Number'] = data['Fields'][13]['Item']
                except:
                    my_dict['Invoice Number'] = ''
                try:
                    my_dict['Debit Memo'] = data['Fields'][32]['Item']
                except:
                    my_dict['Debit Memo'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][33]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['Invoice Date'] = dateStr
                except:
                    my_dict['Invoice Date'] = ''
                try:
                    my_dict['Terms Code'] = data['Fields'][18]['Item']
                except:
                    my_dict['Terms Code'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][34]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['Due Date'] = dateStr
                except:
                    my_dict['Due Date'] = ''
                try:
                    date = int(re.findall(
                        "\d+", data['Fields'][38]['Item'])[0])
                    dateStr = datetime.datetime.fromtimestamp(date/1000)
                    my_dict['Apply Date'] = dateStr
                except:
                    my_dict['Apply Date'] = ''
                try:
                    my_dict['GL Account'] = item['ColumnValue'][2]['Item']
                except:
                    my_dict['GL Account'] = ''

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
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
