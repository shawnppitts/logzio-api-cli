import requests
import time
import json
from . import common, grafana_utils

# ANSI color codes for CLI text
white = "\033[1,37m"
green = "\033[0;32m"
yellow = "\033[1;33m"
blue = "\033[0;34m"
red = "\033[0;31m"
cyan = "\033[0;36m"
end_color = "\033[0m"
bold = "\033[1m"
RETRY_LIMIT = 3

# USER PROMPTS
def get_source_info():
    print(f"{bold}Please enter source account details:{end_color}")
    src_region = input(f"  {cyan}account region (us,au,ca,eu,nl,uk,wa){end_color}: ")
    while src_region not in ["us","au","ca","eu","nl","uk","wa"]:
        src_region = input(f" {red}Invalid region code{end_color}. {cyan}Please enter valid region{end_color}: ")
    
    source_api_endpoint = common.get_region_endpoint(src_region)
    source_api_token = input(f"  {cyan}account API token{end_color}: ")
    return source_api_endpoint, source_api_token
def get_destination_info():
    print(f"{bold}Destination account details:{end_color}")

    valid_account_id = False
    while (valid_account_id == False):
        dst_account_id = input(f"  {cyan}Destination account ID{end_color}: ")
        if dst_account_id.isdigit():
            valid_account_id = True
        else:
            print(f"{red}Not a valid account id. Please try again.{end_color}")
            valid_account_id = False

    dst_region = input(f"  {cyan}account region (us,au,ca,eu,nl,uk,wa){end_color}: ")
    while dst_region not in ["us","au","ca","eu","nl","uk","wa"]:
        dst_region = input("  Invalid region code. \nPlease enter valid region: ")
    
    dst_api_endpoint = common.get_region_endpoint(dst_region)
    dst_api_token = input(f"  {cyan}account API token{end_color}: ")
    return dst_api_endpoint, dst_api_token, dst_account_id

# DASHBOARDS
def get_all_grafana_dashboards(api_url, token):
    url = f"https://{api_url}/v1/grafana/api/search?type=dash-db"
    payload={}
    headers = {
        "X-API-TOKEN": str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    if (type(response) is dict):
        print(f"{red}Request Error{end_color}: {bold}Please verify region and api token are correct{end_color}")
        exit
    else:
        return response    
def get_grafana_dashboard_by_uid(api_url, token, folder):
    url = f"https://{api_url}/v1/grafana/api/search?type=dash-db"
    payload={}
    headers = {
        "X-API-TOKEN": str(token)
    }
    time.sleep(1)
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    dashboards = []
    for dashboard in response:
        try:
            dashboard_url = dashboard['folderUrl']
            if folder in dashboard_url:
                dashboards.append(dashboard)            
        except:
            exit
    return dashboards
def get_dashboard_by_uid(api_url, token, dashboard_uid):
    url = f"https://{api_url}/v1/grafana/api/dashboards/uid/{dashboard_uid}"
    payload={}
    headers = {
        "X-API-TOKEN": str(token)
    }
    time.sleep(1)
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response    
def create_dashboard(api_url, token, payload):
    url = f"https://{api_url}/v1/grafana/api/dashboards/db"
    headers = {
        "X-API-TOKEN": str(token)
    }
    time.sleep(1)
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    return response    

# ALERTS
def get_alerts(alert_type, api_url, token):
    if alert_type == "logging":
        url = f"https://{api_url}/v2/alerts"
        payload={}
        headers = {
            "X-API-TOKEN": str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        if (type(response) is dict):
            print(f"{red}Request Error{end_color}: {bold}Please verify region and api token are correct{end_color}")
            exit
        else:
            return response
    elif alert_type == "metrics":
        url = f"https://{api_url}/v1/grafana/api/v1/provisioning/alert-rules"
        payload={}
        headers = {
            "X-API-TOKEN": str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        if (type(response) is dict):
            print(response)
            print(f"{red}Request Error{end_color}: {bold}Please verify region and api token are correct{end_color}")
            exit
        else:
            return response        
def get_grafana_alert_by_uid(alert_uid, api_url, token):
    url = f"https://{api_url}/v1/grafana/api/v1/provisioning/alert-rules/{alert_uid}"
    payload={}
    headers = {
        'X-API-TOKEN': str(token)
    }
    time.sleep(0.5)
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()            
def get_grafana_datasources(api_url, token):
    url = f"https://{api_url}/v1/grafana/api/datasources/summary"
    payload={}
    headers = {
        'X-API-TOKEN': str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()    
def get_grafana_folders(api_url, token):
    url = f"https://{api_url}/v1/grafana/api/folders/?"
    payload={}
    headers = {
        'X-API-TOKEN': str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()   
def get_grafana_folder_by_uid(folder_uid, api_url, token):
    url = f"https://{api_url}/v1/grafana/api/folders/{folder_uid}"
    payload={}
    headers = {
        'X-API-TOKEN': str(token)
    }
    time.sleep(0.5
        )
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()       
def create_grafana_folder(folder_name, api_url, token):
    url = f"https://{api_url}/v1/grafana/api/folders"
    payload={"title":folder_name}
    payload = json.dumps(payload)
    headers = {
        'X-API-TOKEN': str(token),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    print(response)
    return response
def create_log_alert(api_url, token, body, account_id):    
    body["subComponents"][0]["queryDefinition"]["accountIdsToQueryOn"] = [int(account_id)]
    url = f"https://{api_url}/v2/alerts"
    headers = {
        'X-API-TOKEN': str(token),
        'Content-Type': 'application/json'
    }
    payload = json.dumps(body)
    
    retry_count = 0
    while(retry_count <= RETRY_LIMIT):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if 400 <= response.status_code <= 499:
                retry_count = retry_count + 1
                print(f"Failed! Retrying creation...")

            return response.status_code
            time.sleep(3)    
        except Exception as e:
            print(f"Connection to {url} failed. Retrying creation...")
            retry_count = retry_count + 1
            time.sleep(3)
def create_grafana_alert(api_url, token, body):
    url = f"https://{api_url}/v1/grafana/api/v1/provisioning/alert-rules"
    payload = json.dumps(body)
    headers = {
        'X-API-TOKEN': str(token),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code, response.text
def delete_alert(alert_type, alert_id, api_url, token):
    if (alert_type == "logging"):
        url = f"https://{api_url}/v2/alerts/{alert_id}"
        payload={}
        headers = {
            "X-API-TOKEN": str(token)
        }
        response = requests.request("DELETE", url, headers=headers, data=payload)

        print(f"{alert_id} has been {red}DELETED{end_color}!")
        return response.status_code
    elif (alert_type == "metrics"):
        url = f"https://{api_url}/v1/grafana/api/v1/provisioning/alert-rules/{alert_id}"
        payload={}
        headers = {
            "X-API-TOKEN": str(token)
        }
        response = requests.request("DELETE", url, headers=headers, data=payload)

        print(f"{alert_id} has been {red}DELETED{end_color}!")
        return response.status_code

# NOTIFICATION ENDPOINTS
def get_all_notification_endpoints(api_url, token):
    url = f"https://{api_url}/v1/endpoints"
    payload={}
    headers = {
        'X-API-TOKEN': str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()
def create_slack_endpoint(api_url, token, body):
    url = f"https://{api_url}/v1/endpoints/slack"
    payload = json.dumps(body)
    headers = {
        'X-API-TOKEN': str(token),
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    request_count = 0
    while(request_count <= RETRY_LIMIT):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            request_count = 4         
            return response.status_code
            time.sleep(3)    
        except Exception as e:
            print(f"Connection to {url} failed. Retrying creation...")
            request_count = request_count + 1
            time.sleep(3)
def get_endpoint_by_id(api_url, token, endpoint_id):

    endpoint_id = str(endpoint_id)
    url = f"https://{api_url}/v1/endpoints/{endpoint_id}"
    payload = ""
    headers = {
        'X-API-TOKEN': str(token)
    }
    request_count = 0
    while(request_count <= RETRY_LIMIT):
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            request_count = 4         
            return response.json() 
        except Exception as e:
            print(f"Connection to {url} failed. Retrying creation...")
            request_count = request_count + 1
            time.sleep(3)

# ADMIN TASKS
def get_shipping_tokens(api_url, token):
    url = f"https://{api_url}/v1/log-shipping/tokens/search"
    print(url)
    payload = json.dumps({
      "filter": {
        "enabled": True
      },
      "pagination": {
        "pageNumber": 1,
        "pageSize": 100
      }
    })
    print(payload)
    headers = {
        "X-API-TOKEN": str(token),
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    print(response)
    return response        