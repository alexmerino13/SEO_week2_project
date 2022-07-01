import requests
import os
import pandas as pd
import sqlalchemy as db
from sqlalchemy import create_engine 

WGER_API_key: 3c260d137dc03da712b6a3b03463e45e1a065c48

base_url: https://wger.de/api/v2/

headers = {'Authorization': 'Token 3c260d137dc03da712b6a3b03463e45e1a065c48', 'Content-Type': 'application/json'}

r = requests.get(BASE_URL + 'exercise' + '?limit=<10>', headers=headers)
print(r.json())