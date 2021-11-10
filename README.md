## Auto renew lending.
1. Install dependency in requirement.txt
2. Create a `.env` file in the same folder and fill your api key, secret and other setting in this file.
```
KEY=API_KEY
SECRET=API_SECRET
SUB_ACCOUNT=SUB_ACCOUNT_NAME
LEND_COIN=TOKEN
```
3. Create a cron job to run script, go to termainl and type `crontab -e`.

example: 
```
*/20 * * * * your_python_path/python script_path/auto_update_lending.py
```
