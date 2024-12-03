# Проектная работа 9 спринта

**Ссылка на проект**: [UGC Sprint 2](https://github.com/Benrise/ugc_sprint_2)

**Демонстрация работы оповещения CI**

<img src="https://github.com/user-attachments/assets/da076e78-7a9d-408b-ba3e-fdb114051750" width="300"/>

**ELK**

- в логах передается X-Request-Id
- посредством filebeat реализовано для сервисов: auth, content, ugc
- в логах отсутствует приватная информация
- маршрутизация logstash по индексам

![image](https://github.com/user-attachments/assets/ee759c1f-cd18-4640-9d8c-9828a0b0904c)
![image](https://github.com/user-attachments/assets/148cbec7-4bdb-4665-add1-2da61d4e51c1)
![image](https://github.com/user-attachments/assets/e590dcee-608c-4b28-b5bd-a9a6984f78c6)