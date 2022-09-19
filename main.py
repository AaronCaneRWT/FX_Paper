import requests
import urllib.parse
from datetime import date, timedelta, datetime
import os

API_KEY = os.getenv("TOKEN")

def post_currencyCIQ(last_number, last_day, currency_rate, ws_uuid):
    '''
    Send new record to CaptivateIQ
        Receive: 
            last_number(int):  Next UID in the CIQ worksheet 
            last_day(datetime): Next day in the CIQ worksheet 
            currency_rate(float) Next Fx Rate in the CIQ worksheet
            ws_uuid(str): worksheet id
        Return:
            NULL
    '''
    import_url = 'https://api.captivateiq.com/ciq/v1/data-worksheets/{}/records/'.format(ws_uuid)
    headers = {
        'Authorization': API_KEY,
        'Accept': "application/json",
        'Content-Type': 'application/json'
    }
    

    send_day = last_day.day
    send_month = last_day.month
    send_year = last_day.year

    if(send_day <= 9):
        send_day = '0{}'.format(send_day)
    else:
        send_day = str(send_day)

    if(send_month <= 9):
        send_month = '0{}'.format(send_month)
    else:
        send_month = str(send_month)

    send_date = f'{send_year}-{send_month}-{send_day}'

    payload = {
        "UID": last_number,
        "Date": send_date,
        "FX Rate": currency_rate,
    }
    response_post = requests.post(import_url, json=payload, headers=headers)
    if response_post.status_code ==201:
        print("Record Added:",payload)
    else:
        print("Bad request: ", response_post.status_code, response_post.text)
    return 


def currency(last_number, last_day, ws_uuid):
    '''
    Get current fx rate
        Receive: 
            last_number(int):  Last UID in the CIQ worksheet 
            last_day(datetime): Last day in the CIQ worksheet 
            ws_uuid(str): worksheet id
        Return:
            NULL
    '''
    today = date.today()
    today = today + timedelta(days=1)
    # parametros a envia a API fx rate
    base = 'USD'
    symbols = 'CAD'
    amount = "1"
    payload = {
        'base': base,
        'symbols': symbols,
        'amount': amount
    }

    last_day = datetime.strptime(last_day, '%Y-%m-%d')
    last_day = last_day + timedelta(days=1)
    last_number = int(last_number)

    while(last_day.strftime('%Y-%m-%d') != today.strftime('%Y-%m-%d')):
        # extrae numero
        day_url = last_day.day
        month_url = last_day.month
        year_url = last_day.year

        # convierte a cadena
        day_url = str(day_url)
        month_url = str(month_url)
        year_url = str(year_url)
        # concatena URL
        host_exchange = f'https://api.exchangerate.host/{year_url}-{month_url}-{day_url}'
        response_fx = requests.get(host_exchange, params=payload)
        if response_fx.status_code == 200:

            data_fx = response_fx.json()
            for item in data_fx['rates']:
                last_number = last_number+1
                currency_rate = data_fx['rates'][item]
                post_currencyCIQ(last_number, last_day, currency_rate, ws_uuid)

        else:
            print(response_fx.status_code, response_fx.text)

        last_day = last_day + timedelta(days=1)


def getLastDayCIQ():
    '''
    Get current fx rate
        Receive:
            NUL 
        Return: 
            last_number(int):  Last UID in the CIQ worksheet 
            last_day(datetime): Last day in the CIQ worksheet 
            ws_uuid(str): worksheet id
    '''
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    params = {
        "limit": "1000"
    }

    worksheet_url = 'https://api.captivateiq.com/ciq/v1//data-worksheets/'
    
    name_query = urllib.parse.quote_plus('daily')
    ws_response = requests.get(
        f'{worksheet_url}?name_contains={name_query}', headers=headers)

    ws_uuid = ws_response.json()['data'][0]['id']
    get_url = 'https://api.captivateiq.com/ciq/v1/data-worksheets/{}/records/'.format(ws_uuid)
    response_ciq = requests.get(get_url, headers=headers, params=params)
    
    if response_ciq.status_code == 200:

        response_fx = response_ciq.json()
        for item in response_fx['data']:
            last_number = item['data']['UID']
            last_day= item['data']['Date']
        return last_number, last_day, ws_uuid
    else:
        print(response_ciq.status_code, response_ciq.text)


    

if __name__ == "__main__":
    print("Starting")
    last_number, last_day, ws_uuid = getLastDayCIQ()
    print('Last record: {} {} {}'.format(last_number, last_day, ws_uuid))
    currency(last_number, last_day, ws_uuid)
