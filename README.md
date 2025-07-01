
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

to add interpreter using uv in pycharm, go to `Add New Interpreter` -> `Add Local Interpreter`, In `Type` dropdown select Type `uv` from the list, then path to the `uv` executable, which is usually located in your home `bin` directory (e.g., `~/.local/bin/uv`).
![image](https://github.com/user-attachments/assets/d34981b7-e70c-47f3-9440-74657f745e05)
