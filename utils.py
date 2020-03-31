import requests
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import send_file,request, redirect
def security():
     #use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    log = client.open("Tennis Shipment User Authentication").sheet1
    # Extract and print all of the values
    list_of_hashes = log.get_all_records()
    babolatlog=[d for d in list_of_hashes if d['brand'] =='babolat']
    babolatsecurity = {x['username']:x['password']for x in babolatlog}
    wilsonlog=[d for d in list_of_hashes if d['brand'] =='wilson']
    wilsonsecurity={x['username']:x['password']for x in wilsonlog}
