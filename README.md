
### .env file example
```bash  

DRIVER={ODBC Driver 17 for SQL Server}
CSDIGITAL_SERVER=AUS2-PHX-DSQL01.na.drillinginfo.com
CSDIGITAL_DATABASE=CS_Digital
CSDIGITAL_UID=cs_updates
CSDIGITAL_PWD=********

PYTHONWARNINGS="ignore"
```


### to run: 
use the following command
```bash

uv run --env-file .env --python python3 main.py
```
