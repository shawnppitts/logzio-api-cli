from . import endpoints, common
import random, string
import time
import sys
import json

# ANSI color codes for CLI text
white = "\033[1,37m+"
green = "\033[0;32m"
yellow = "\033[1;33m"
blue = "\033[0;34m"
red = "\033[0;31m"
cyan = "\033[0;36m"
end_color = "\033[0m"
bold = "\033[1m"

def get_region_endpoint(region):
        if region == "us":
            return "api.logz.io"
        elif region == "au":
            return "api-au.logz.io"
        elif region == "ca":
            return "api-ca.logz.io"
        elif region == "eu":
            return "api-eu.logz.io"
        elif region == "nl":
            return "api-nl.logz.io"
        elif region == "uk":
            return "api-uk.logz.io"
        elif region == "wa":
            return "api-wa.logz.io"

def safely(action, items, items_chosen, api_url, api_token, account_id=0, flag=False, params={}):
    continue_after_warning = input(f"Please confirm action on the following items:{bold}{items_chosen}{end_color} by typing {green}y{end_color} or {red}n{end_color}: ")
    # print(f"{white}Arguments\n\taction: {action}\n\titems_chosen: {items_chosen}\n\tapi_url: {api_url}\n\tapi_token: {api_token}\n\taccount_id:{account_id}\n\tflag: {flag}\n\tparams: {params}\n{end_color}")
    
    # User agreed to continue copying
    if (continue_after_warning == "y"):
        # Loop over all src alerts
        for item in items:
            item_id = str(item['id'])
            # some items do not contain uid's such as log alerts
            try:
                item_uid = str(item['uid'])
            except:
                item_uid = "nouid" 
            item_title = item['title']
            # Loop over items to copy
            for y in range(len(items_chosen)):
                # Check to see if there is an id/uid to copy that matches an id/uid fetched
                if (item_id == items_chosen[y] or item_uid == items_chosen[y]):
                    # conditonal handling based on action. Some payloads need to be manipulated per endpoint
                    if (action == "create_log_alerts"):                       
                        print(f"\nCopying alert {blue}{item_title}{end_color}")
                        if (params["mode"] == "bulk"):
                            item["output"]["recipients"]["notificationEndpointIds"] = [int(params["notification_endpoints"][0])]
                            status = endpoints.create_log_alert(api_url, api_token, item, account_id)
                        elif (params["mode"] == "individual"):
                            item["output"]["recipients"]["notificationEndpointIds"] = [int(params["notification_endpoints"][y])]
                            status = endpoints.create_log_alert(api_url, api_token, item, account_id)
                    elif (action == "delete_log_alerts"):
                        print(f"\nDeleting alert {blue}{item_title}{end_color}")                        
                        status = endpoints.delete_alert("logging", item_id, api_url, api_token)
                    elif (action == "copy_metrics_alerts"):
                        item["folderUID"] = params["folder_uid"]
                        title = item["title"]
                        item["id"] = 0
                        item['ruleGroup'] = "alerts"
                        item["annotations"] = {}
                        item["uid"] = common.generate_UID()
                        item["data"][0]["datasourceUid"] = params["datasource_uid"]
                        print(f"\nCopying {bold}{title}{end_color}")                                                           
                        status, response = endpoints.create_grafana_alert(api_url, api_token, item)
                    elif (action == "delete_metrics_alerts"):
                        print(f"\nDeleting alert {blue}{item_title}{end_color}")
                        status = endpoints.delete_alert("metrics", item_uid, api_url, api_token)                    

                    # Output response status
                    if status >= 200 and status <= 299:
                        print(f"Status: {green}SUCCESS{end_color}")
                    else:
                        print(f"Status: {red}FAILED{end_color}\n")
                        print(f"{red}{response}{end_color}")
    elif (continue_after_warning == "n"):
        print(f"{action} {red}cancelled{end_color}. Returning to main menu...")

def display_menu():
    print("\n-----------------------------------------")
    print(f"\t{bold}ACTION MENU{end_color}")
    print(f"  u: update src account info")
    print(f"{green}Logging{end_color}")
    print(f"  l1. Copy Log Alerts")
    print(f"  l2. Delete Log Alerts")    
    print(f"  l3. Get all Log Alerts")

    print(f"{blue}Metrics{end_color}")
    print(f"  m1. Copy metrics alerts")
    print(f"  m2. Delete metrics alerts")
    print(f"  m3. Get all metrics alerts")
    print(f"  m4. Copy metrics dashboards")    

    print(f"{cyan}Admin{end_color}")
    print(f"  a1. Copy notification endpoints")
    print(f"  a2. Get shipping tokens")

    print(f"{red}q: Quit script{end_color}")
    print("------------------------------------------")

def unique_items_only(arr):
    unique_list = []
 
    # traverse for all elements
    for item in arr:
        if item not in unique_list:
            unique_list.append(item)

    return unique_list

def display_fetched(fetched_response, category):
    if (type(fetched_response) == dict):
        print("Error")
    
    notification_endpoint_list = []

    if category == "logging":
        for alert in fetched_response:
            alert_id = str(alert['id'])
            endpoint_ids = list(alert["output"]["recipients"]["notificationEndpointIds"])
            alert_title = alert['title'],
            alert_body = alert
            alert_title = list(alert_title)
            alert_title = alert_title[0]
            print(f"  {alert_id} - {alert_title}")
    elif category == "notification_endpoints":
        print(f"\n{green}Fetched notification endpoints:{end_color}")
        for endpoint in fetched_response:
            endpoint_id = endpoint['id']
            endpoint_type = endpoint['endpointType']
            endpoint_title = endpoint['title']
            endpoint_url = endpoint['url']
            print(f"{bold}id: {endpoint_id}| type: {endpoint_type}| title: {endpoint_title}| url: {endpoint_url} |{end_color}")
    elif category == "metrics_alerts":
        uids = []        
        print(f"\n{green}Fetched Grafana Alerts:{end_color}")
        for alert in fetched_response:
            alert_id = str(alert['id'])
            alert_uid = alert['uid']
            alert_title = alert['title']
            folder_uid = alert["folderUID"]
            alert_details = {alert_id:alert_uid}
            uids.append(alert_details)
            print(f"  {red}UID:{end_color} {alert_uid} | {green}Alert Name{end_color}: {alert_title}")
        return uids
    elif category == "metrics_folders":
        print(f"\n{green}Fetched Grafana Folders:{end_color}")
        for folder in fetched_response:
            folder_uid = str(folder['uid'])
            folder_title = folder['title']
            print(f"  {red}UID{end_color}: {folder_uid} | {green}Folder Name{end_color}: {folder_title}")
    elif category == "metric_dashboards":
        print(f"\n{green}Fetched Grafana Dashboards:{end_color}")
        for dashboard in fetched_response:
            dashboard_title = dashboard["title"]
            dashboard_uid = dashboard["uid"]
            print(f"  {red}UID:{end_color} {dashboard_uid} | {green}Dashboard Title{end_color}: {dashboard_title}")
    elif category == "metric_datasources":
        print(f"\n{green}Fetched Datasources:{end_color}")
        for source in fetched_response:
            source_uid = source["uid"]
            source_name = source["name"]
            source_type = source["type"]
            print(f"  {red}UID:{end_color} {source_uid} | {green}Source Name{end_color}: {source_name} | {cyan}Source Type{end_color}: {source_type}")            

def get_ids_to(action, category):
    alerts = ""
    if (category == "metrics"):
        ids = input(f"\n{cyan}Enter UIDs to {action} (comma seperated,no spaces) or q to return to menu{end_color}: ")
    elif (category == "metric_folders"):
        ids = input(f"\n{cyan}Enter UIDs to {action} (comma seperated,no spaces) or enter 'all' to {action} folders{end_color}: ")
    elif (category == "metric_folder"):
        ids = input(f"{cyan}Enter UID of folder to nest alert under (comma seperated,no spaces){end_color}: ")
    elif (category == "prometheus_datasource"):
        ids = input(f"{cyan}Enter UID of the prometheus datasource you would like to {action}{end_color}: ")
    elif (category == "elastic_datasource"):
        ids = input(f"{cyan}Enter UID of the elasticsearch datasource you would like to {action}{end_color}: ")        
    elif (category == "metric_dashboard_folder"):
        ids = input(f"{cyan}Enter UID of folder you would like to {action}{end_color}: ")        
    else:
        ids = input(f"{cyan}Enter id to {action} (comma seperated,no spaces) or q to return to menu{end_color}: ")

    if (ids.lower() == "q"):
        alerts = "None"
        return alerts
    else:
        ids = ids.split(',')
        return ids

def generate_UID():
    uid = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(16))
    return uid
