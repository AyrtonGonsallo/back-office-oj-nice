import requests

url = "https://api-control.nash-project.name/profile"

payload = {}
files=[
  ('file',('import nice test.xlsx',open('C:/Users/Ayrton/Downloads/import nice test.xlsx','rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
]
headers = {
    'Accept': 'application/json',
    "Content-Type": "multipart/form-data"
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response)



