import json
import re
import sys
import scripts.endpoints as endpoints
import scripts.common as common
import scripts.grafana_utils as grafana_utils

green = "\033[0;32m"
yellow = "\033[1;33m"
cyan = "\033[0;36m"
blue = "\033[0;34m"
red = "\033[0;31m"
end_color = "\033[0m"
bold = "\033[1m"

# Flags
delete_notif_endpoint_flag = False
prompt_for_source_details = False
ask_again_at_prompt = False
src_endpoint = ""
src_token = ""
menu_option = ""

print(f"Welcome to the {yellow}Logz.io API CLI{end_color}!")
print("Reminders:")
print(f"  1. You can locate your API token within the Logz.io App under Settings > Manage Tokens > API")
print(f"  2. All functionality is built on endpoints found at https://docs.logz.io/api/")
print(f"  3. Source account refers to where your fetching data {bold}from{end_color}")
print(f"  4. Destination account refers to where your going to copy {bold}to{end_color}")
print(f"  5. This project is maintained by shawn.pitts@logz.io. Email for feature requests or bugs found :)\n")
# while user does not want to quit program continue on
while (menu_option != "q"):
    # While user does not want to save the credentials continue on but ask for every prompt
    while (prompt_for_source_details == False):
        temp_endpoint, temp_token = endpoints.get_source_info()
        save_credentials = input(f"{bold}Would you like to save these credentials as your source account (y/n)?: ")
        if (save_credentials == "y"):
            src_endpoint = temp_endpoint
            src_token = temp_token
            prompt_for_source_details = True
            ask_again_at_prompt = False
        else:              
            print(f"{yellow}WARNING: Not saving credentials. You will need to enter this for further account actions{end_color}")
            prompt_for_source_details = True
            ask_again_at_prompt = True

    common.display_menu()
    menu_option = input("\nSelect option from menu: ")

    # Conditional logic based on choice
    if menu_option == "l1": # COPY LOG ALERT
        # Step 1a. fetch and output list of src alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()

        src_alerts = endpoints.get_alerts("logging", src_endpoint, src_token)

        print(f"\n{bold}{green}Fetched alerts from source account{end_color}")
        common.display_fetched(src_alerts, "logging")

        alerts_to_copy = common.get_ids_to("copy", "logging")

        print(f"\n{yellow}WARNING: The notification endpoints discovered in the above alerts may not be on the destination account.{end_color}")
        continue_with_copying = input(f"{yellow}Would you like to continue copying alerts (y/n):{end_color} ")
        
        if (continue_with_copying == "y"):
            delete_notif_endpoint_flag = True
        else:
            print("Please consider copying over notification endpoints prior to alert copying (enter a1). Returning to action menu...")
            continue

        if (alerts_to_copy == "None"):
            continue           

        dst_endpoint, dst_token, dst_accountId = endpoints.get_destination_info()

        dst_notification_endpoints = endpoints.get_all_notification_endpoints(dst_endpoint, dst_token)
        print(f"We have detected the following notification endpoints on this account.")
        common.display_fetched(dst_notification_endpoints, "notification_endpoints")

        notification_endpoints = {
            "notification_endpoints":[]
        }
        invalid_option = "yes"
        while(invalid_option == "yes"):
            print(f"\nWould you like to\n  1. Bulk update all copied alerts to use a single endpoint\n  2. Choose an endpoint for each alert\n  q. Return to action menu\n")
            endpoint_decision = input("Please make selection: ")
            if (endpoint_decision == "1"):
                invalid_option = "no"
                print(f"\n{green}Global alert modifications:{end_color}")
                endpoint_to_use = common.get_ids_to("use", "logging")
                notification_endpoints["notification_endpoints"].append(endpoint_to_use[0])
                notification_endpoints["mode"] = "bulk"
            elif endpoint_decision == "2":
                invalid_option = "no"
                for alert in alerts_to_copy:
                    print(f"\nAlert {green}{alert}{end_color} modifications:")
                    endpoint_to_use = common.get_ids_to("use", "logging")
                    notification_endpoints["notification_endpoints"].append(endpoint_to_use[0])
                    notification_endpoints["mode"] = "individual"
            elif endpoint_decision == "q":
                invalid_option = "no"
                print("Returning to main menu...")
                break

        # beginning of alert copying process
        warning_message = print(f"\n{yellow}WARNING! all copied alerts will be duplicated on the destination account if they already exist!{end_color}")
        common.safely("create_log_alerts", src_alerts, alerts_to_copy, dst_endpoint, dst_token, account_id=dst_accountId, flag=delete_notif_endpoint_flag, params=notification_endpoints)
    elif menu_option == "l2": # DELETE log alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
        src_alerts = endpoints.get_alerts("logging", src_endpoint, src_token)

        print(f"\n{bold}{green}Fetched alerts from source account{end_color}")
        endpoints_list = common.display_fetched(src_alerts, "logging")

        alerts_to_delete = common.get_ids_to("delete", "logging")

        if (alerts_to_delete == "None"):
            continue
        else:     
            common.safely("delete_log_alerts", src_alerts, alerts_to_delete, src_endpoint, src_token)
    elif menu_option == "l3": # GET all log alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
        src_alerts = endpoints.get_alerts("logging", src_endpoint, src_token)

        print(f"\n{bold}{green}Fetched alerts from source account{end_color}")
        endpoints_list = common.display_fetched(src_alerts, "logging")     
    elif menu_option == "m1": # COPY metrics alerts
        # Step 1. Get Source alerts 
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
        # Step 2. Output list of alerts for user to see
        src_alerts = endpoints.get_alerts("metrics", src_endpoint, src_token) 
        common.display_fetched(src_alerts, "metrics_alerts")
        
        # Step 3. Ask user which alerts theyd like to copy
        alerts_to_copy = common.get_ids_to("copy", "metrics")
        # Return to main menu if they dont want to perform step 3
        if (alerts_to_copy == "None"):
            break 

        # Step 4. Get account details for destination
        dst_endpoint, dst_token, dst_accountId = endpoints.get_destination_info()
        
        # Step 5. Get all folders 
        dst_folders = endpoints.get_grafana_folders(dst_endpoint, dst_token)
        dst_datasources = endpoints.get_grafana_datasources(dst_endpoint, dst_token)

        common.display_fetched(dst_folders, "metrics_folders")
        common.display_fetched(dst_datasources, "metric_datasources")
        
        # Step 6. Does user want to nest all copied alerts under 1 folder or get to choose for each individual alert?                         
        invalid_option = "yes"

        while invalid_option == "yes":
            folder_decision = input(f"\nEnter {bold}1{end_color} to bulk update copied alerts under one folder OR {bold}2{end_color} choose a folder per alert: ")            
            if (folder_decision == "2"):
                invalid_option = "no"            
                for alert in alerts_to_copy:
                    print(f"\n------------------------------------------------------------")
                    print(f"Alert {yellow}{alert}{end_color} modifications:")
                    grafana_folder_id = common.get_ids_to("nest", "metric_folder")
                    prometheus_datasource = common.get_ids_to("use", "prometheus_datasource")
                    alert_body = endpoints.get_grafana_alert_by_uid(alert, src_endpoint, src_token)
                    alert_body["id"] = 0
                    alert_body["uid"] = common.generate_UID()
                    alert_body["folderUID"] = grafana_folder_id[0]
                    alert_body["data"][0]["datasourceUid"] = prometheus_datasource[0]
                    status, response = endpoints.create_grafana_alert(dst_endpoint, dst_token, alert_body)
                    if status >= 200 and status <= 299:
                        print(f"{alert} Copy Status: {green}SUCCESS{end_color}")
                    else:
                        print(f"{alert} Copy Status: {red}FAILED{end_color}\n")
                        print(f"{red}{response}{end_color}")
                    print(f"------------------------------------------------------------")
            elif (folder_decision == "1"):
                invalid_option = "no"
                print(f"Global alert modifications:")
                grafana_folder_id = common.get_ids_to("nest", "metric_folder")
                prometheus_datasource = common.get_ids_to("use", "prometheus_datasource")
                for alert in alerts_to_copy:
                    alert_body = endpoints.get_grafana_alert_by_uid(alert, src_endpoint, src_token)
                    alert_body["id"] = 0
                    alert_body["uid"] = common.generate_UID()
                    alert_body["folderUID"] = grafana_folder_id[0]
                    alert_body["data"][0]["datasourceUid"] = prometheus_datasource[0]
                    status, response = endpoints.create_grafana_alert(dst_endpoint, dst_token, alert_body)
                    if status >= 200 and status <= 299:
                        print(f"Status: {green}SUCCESS{end_color}")
                    else:
                        print(f"Status: {red}FAILED{end_color}\n")
                        print(f"{red}{response}{end_color}")                                        
            else:
                print(f"{red}invalid selection. Please try again{end_color}")
                invalid_option = "yes"         
    elif menu_option == "m2": # DELETE metrics alerts
        # Step 1a. fetch and output list of src alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()        

        src_alerts = endpoints.get_alerts("metrics", src_endpoint, src_token) 
        alert_uids = common.display_fetched(src_alerts, "metrics_alerts")    
        alerts_to_delete = common.get_ids_to("delete", "metrics")

        if (alerts_to_delete == "None"):
            break

        common.safely("delete_metrics_alerts", src_alerts, alerts_to_delete, src_endpoint, src_token)
    elif menu_option == "m3": # GET metrics alerts
        # Step 1a. fetch and output list of src alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
        elif ask_again_at_prompt == False:
            print("")

        src_alerts = endpoints.get_alerts("metrics", src_endpoint, src_token) 
        common.display_fetched(src_alerts, "metrics_alerts")
    elif menu_option == "m4": # COPY metrics dashboards
        # Step 1. Fetch src account info if needed
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()

        # Step 2. Get folders in src account and ask which folder they would like to search across
        src_folders = endpoints.get_grafana_folders(src_endpoint, src_token)        
        print("We have detected dashboards nested under the following folders:")
        common.display_fetched(src_folders, "metrics_folders")
        folders_to_search = common.get_ids_to("search across", "metric_folders")

        for folder in folders_to_search:
            dashboard_list = []
            if (folder == "all"):
                dashboard_list = endpoints.get_all_grafana_dashboards(src_endpoint, src_token)
            else:
                dashboard_list = endpoints.get_grafana_dashboard_by_uid(src_endpoint, src_token, folder)
    
            common.display_fetched(dashboard_list, "metric_dashboards")        
        # Step 3. Ask user what they want to copy and capture all the uids
        dashboards_to_copy = common.get_ids_to("copy", "metrics")
        # Step 4. Get account info for destination
        dst_endpoint, dst_token, dst_accountId = endpoints.get_destination_info()        
        """
        Step 5. Since all dashboards have a folder they are nested under in Grafana, we will need to
        get a list of folders on the dst account and ask user for each dashboard being copied which folder to nest under        
        """
        folders = endpoints.get_grafana_folders(dst_endpoint, dst_token)
        datasources = endpoints.get_grafana_datasources(dst_endpoint, dst_token)

        common.display_fetched(folders, "metrics_folders")
        common.display_fetched(datasources, "metric_datasources")        
        invalid_option = "yes"

        while invalid_option == "yes":
            datasource_decision = input(f"\nEnter {bold}1{end_color} to bulk update copied dashboards with a datasource OR {bold}2{end_color} to choose a datasource per dashboard: ")            
            if (datasource_decision == "2"):
                invalid_option = "no"            
                for dashboard in dashboards_to_copy:
                    print(f"\n------------------------------------------------------------")
                    print(f"Dashboard {yellow}{dashboard}{end_color} modifications:")
                    prometheus_datasource_uid = common.get_ids_to("use", "prometheus_datasource")
                    elastic_datasource_uid = common.get_ids_to("use", "elastic_datasource")
                    folder_uid = common.get_ids_to("nest dashboard under", "metric_dashboard_folder")
                    dashboard_content = endpoints.get_dashboard_by_uid(src_endpoint, src_token, dashboard)
                    # Modifications to dashboard json
                    dashboard_content["meta"] = {}
                    dashboard_content["folderUid"] = str(folder_uid[0])
                    dashboard_content["dashboard"]["id"] = "null"
                    dashboard_content["dashboard"]["uid"] = common.generate_UID()
                    dashboard_content = json.dumps(dashboard_content)
                    dashboard_content = re.sub('{"type": "prometheus", "uid": "\\w+"}', '{"type": "prometheus", "uid": "prometheus_datasource_uid"}', dashboard_content)
                    dashboard_content = re.sub('{"type": "elasticsearch", "uid": "\\w+"}', '{"type": "elasticsearch", "uid": "elastic_datasource_uid"}', dashboard_content)                    
                    dashboard_content = re.sub('prometheus_datasource_uid', str(prometheus_datasource_uid[0]), dashboard_content)
                    dashboard_content = re.sub('elastic_datasource_uid', str(elastic_datasource_uid[0]), dashboard_content)                                  
                    status = endpoints.create_dashboard(dst_endpoint, dst_token, dashboard_content)                
                    if status['status'] == "success":
                        print(f"Dashboard Creation: {green}SUCCESS{end_color}")                        
                    else:
                        print(f"Status: {red}FAILED{end_color}\n")
                        print(f"{red}{response}{end_color}")                    
                    print(f"------------------------------------------------------------")
            elif (datasource_decision == "1"):
                invalid_option = "no"
                print(f"Global dashboard modifications:")
                prometheus_datasource_uid = common.get_ids_to("use", "prometheus_datasource")
                elastic_datasource_uid = common.get_ids_to("use", "elastic_datasource")
                folder_uid = common.get_ids_to("nest dashboard under", "metric_dashboard_folder")                
                for dashboard in dashboards_to_copy:
                    dashboard_content = endpoints.get_dashboard_by_uid(src_endpoint, src_token, dashboard)
                    # Modifications to dashboard json
                    dashboard_content["meta"] = {}
                    dashboard_content["folderUid"] = str(folder_uid[0])
                    dashboard_content["dashboard"]["id"] = "null"
                    dashboard_content["dashboard"]["uid"] = common.generate_UID()
                    dashboard_content = json.dumps(dashboard_content)
                    dashboard_content = re.sub('{"type": "prometheus", "uid": "\\w+"}', '{"type": "prometheus", "uid": "prometheus_datasource_uid"}', dashboard_content)
                    dashboard_content = re.sub('{"type": "elasticsearch", "uid": "\\w+"}', '{"type": "elasticsearch", "uid": "elastic_datasource_uid"}', dashboard_content)                    
                    dashboard_content = re.sub('prometheus_datasource_uid', str(prometheus_datasource_uid[0]), dashboard_content)
                    dashboard_content = re.sub('elastic_datasource_uid', str(elastic_datasource_uid[0]), dashboard_content)                                  
                    status = endpoints.create_dashboard(dst_endpoint, dst_token, dashboard_content)                
                    if status['status'] == "success":
                        print(f"Dashboard Creation: {green}SUCCESS{end_color}")                        
                    else:
                        print(f"Status: {red}FAILED{end_color}\n")
                        print(f"{red}{response}{end_color}")
            else:
                print(f"{red}invalid selection. Please try again{end_color}")
                invalid_option = "yes"
    elif menu_option == "a1": # COPY notification endpoints
        # Step 1a. fetch and output list of src alerts
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
            
        notification_endpoints = endpoints.get_all_notification_endpoints(src_endpoint, src_token)
        if len(notification_endpoints) == 0:
            print(f"{red}No notification endpoints found! Returning back to action menu{end_color}")
            continue
        common.display_fetched(notification_endpoints,"notification_endpoints")
        ids_list = common.get_ids_to("copy","logging")
        dst_endpoint, dst_token, dst_accountId = endpoints.get_destination_info()

        for endpoint in notification_endpoints:
            endpoint_id = str(endpoint['id'])
            endpoint_title = endpoint['title']
            for y in range(len(ids_list)):
                if endpoint_id == ids_list[y]:
                    print(f"\nCopying endpoint {blue}{endpoint_title}{end_color}")
                    status = endpoints.create_slack_endpoint(dst_endpoint, dst_token, endpoint)
                    if status == 200 or 201:
                        print(f"Status: {green}{status}{end_color}")      
                    else:
                        print(f"Status: {red}{status}{end_color}")
    elif menu_option == "a2": # GET shipping tokens
        if ask_again_at_prompt == True:
            src_endpoint, src_token = endpoints.get_source_info()
        
        endpoints.get_shipping_tokens(src_endpoint, src_token)       
    elif menu_option == "u":
        src_endpoint, src_token = endpoints.get_source_info()