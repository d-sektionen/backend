import requests

files = [("file", open("/home/felix/Documents/a.txt")), ("file", open("/home/felix/Documents/b.txt"))]
header = {}
headers={'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ0OTQ4MjA4LCJqdGkiOiJmMzY1Y2EwNThmMjE0ODA0YjFkY2Y5ZDgyOTg2YTVhZCIsInVzZXJfaWQiOjF9.GtOxYA7qz0nh5lTfkbPlpmrf-Uh425SBIbvvrZ4u-KY"}
data = {"committee":"1","date":"2023-01-01T01:01","name":"Test", "articles":"[]", "description":"test_dec","clearingNr":"123456", "bankNr":"987654", "bankName":"DBank", "location":"Linköping"}
r = requests.post(
    "http://localhost:8000/budget/expense-entries/", 
    files=files,
    headers=headers,
    data=data)

print(r.json())