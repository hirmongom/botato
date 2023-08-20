.env variables
--------------
### ./.env ###
* TOKEN

    You should find this on the Discord Developer portal (https://discord.com/developers), after selecting
    the Application, head to the left side panel, enter the *Bot* category and get the Token.

* APPID

  You should find this on the Discord Developer portal (https://discord.com/developers), select your Application
  and on the *General Information* tab you should find the application id.

* MAIN_CHANNEL

  This represents the ID of the channel where the bot will primarily interact. To get this ID you can head to the Discord
  application, right-click the desired channel and select *Copy Channel ID* (You must have *Developer Mode* enabled on settings).

  (As of today 13/08/2023, this is only used in the ```daily_trigger()``` function in keys_cog.py)

* BROWSERPATH

  This should represent the full path to a Chromium based browser.
  (e.g. ```BROWSERPATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe```,
  or ```BROWSERPATH=/usr/bin/google-chrome```,
  or ```BROWSERPATH=/usr/bin/brave-browser```)


### ./utils/keys/chromedriver/ ###
--------------

  The execution might fail depending on the version compatibility between the webdriver and the browser, and/or the OS where it is being executed. To get the appropiate webdriver visit https://chromedriver.chromium.org/
  
  (I will keep the chromedriver I'm using commited since I share the same enviroment between multiple machines)