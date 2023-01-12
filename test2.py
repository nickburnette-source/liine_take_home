import requests
import app

# TODO bug: store is closed if query time == close time
# TODO bug: returns 500 instead of 4xx code on bad ts request (handle 24:00:00)

# mins & maxes
# 0/24 open/close, new year, feb 29
# f'2023/01/0{} 23:59:59'
times = [f'2023/01/0{i} 00:00:00' for i in range(1, 8)]
times = [f'2023/01/0{i} 23:59:59' for i in range(1, 8)]
times = [f'2023/01/02 10:59:59']
expected = [True, True, True, True]

for ts in times:
    url = f'http://localhost:5000/?datetime={ts}'
    response = requests.get(url).json()['data']

# Possible tests
# 1. compare standized ts to db
# 2. compare db to hours





