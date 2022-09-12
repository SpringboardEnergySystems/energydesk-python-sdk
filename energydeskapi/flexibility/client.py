import requests
from datetime import datetime, timedelta
def cancel_dispatch(date):
    token="ebb44e807b185d0b4a410fec4b971fda9d8e4cad"
    headers = {'Authorization': 'Token ' + token}
    server_url = 'https://smartflex.springboard.energy/api/flexoptimizer/cancel_dispatch/'
    from_time = date.replace(hour=1, minute=0, second=0)
    until_time = date.replace(hour=23, minute=0, second=0)
    qry_payload = {
        "from_time": from_time.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        "until_time": until_time.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    }
    result = requests.post(server_url, json=qry_payload, headers=headers)
    print(result, result.text)

if __name__ == '__main__':
    print("Cancel dispatch")
    cancel_dispatch(datetime.today())   # Cancel all dispatches today
    cancel_dispatch(datetime.today() + timedelta(days=1)) #Cancel all dispatches tomorrow