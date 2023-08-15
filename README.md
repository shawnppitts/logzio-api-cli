# logzio-api-cli
This CLI was built to be able to automate CRUD operations that cannot be performed easily within the application. This includes actions such as:
  - Copy Log Alerts
  - Delete Log Alerts
  - Get all Log Alerts
  - Copy metrics alerts
  - Delete metrics alerts
  - Get all metrics alerts
  - Copy metrics dashboards
  - Copy notification endpoints

## Running as Docker Image:
```
$ docker pull shawnpitts/logzio-cli
$ docker run -it shawnpitts/logzio-cli
```

## Running in standalone Python:
```
$ pip -r requirements.txt
$ python3 script.py
```