import requests
all_employee=["1234245",'242245345']
url="https://notification.pepper-coding.ru/notification/publish"
if len(all_employee)>1:
    data={"text":f"Краткая сводка на сотрудников {" ".join(all_employee)} готова."}
else:
    data={"text":f"Краткая сводка на сотрудника {all_employee[0]} готова."}
print(data)
response = requests.post(url, json=data)
