### project-hktrambot

#### Description

* The project is a simple Telegram Bot which can retrieve the nearest tram stop and the estimated arrival time of next trams
* It is written in Python with the use of the Telegram Bot Framework Telepot and Geopy for the distance calculation
* The bot can be found at http://telegram.me/hktrambot

#### Heroku

This project is deployed on Heroku.
* To setup, the following environment variable(s) need to be set
  * `TOKEN=[Your Telegraam Bot Token]`
  * `ENDPOINT_LIST=[Endpoint to retrieve list of tram stops]`
  * `ENDPOINT_ETA[Endpoint to retrieve eta of specific tram stop]`
* My another project [project-hktram](https://github.com/wwong38519/project-hktram) which retrieves tram information is used for the endpoints. 