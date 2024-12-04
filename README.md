# Проектная работа 9 спринта

**Ссылка на проект**: [UGC Sprint 2](https://github.com/Benrise/ugc_sprint_2)

**Настроенный пайплайн в Github Actions**

![image](https://github.com/user-attachments/assets/4767d0fa-3251-409f-bd25-10214e474dab)

**Демонстрация работы оповещения CI**

<img src="https://github.com/user-attachments/assets/da076e78-7a9d-408b-ba3e-fdb114051750" width="300"/>

**ELK**

- в логах передается X-Request-Id
- реализовано для сервисов: auth, content, ugc, nginx
- в логах отсутствует приватная информация
- маршрутизация logstash по индексам
- взаимодействие с хранилищем логов через filebeat

![image](https://github.com/user-attachments/assets/ee759c1f-cd18-4640-9d8c-9828a0b0904c)
![image](https://github.com/user-attachments/assets/148cbec7-4bdb-4665-add1-2da61d4e51c1)
![image](https://github.com/user-attachments/assets/e590dcee-608c-4b28-b5bd-a9a6984f78c6)
![image](https://github.com/user-attachments/assets/99d12f81-e2c5-4340-a905-c299cbc14f0a)


**Hawk (сырая альтернатива Sentry)**

*В будущем потребуется [обновить](https://github.com/codex-team/hawk.python/issues/28) под модуль FastAPI. Сейчас работает только ручной вызов.*

Коммит для обновления - Use fastapi hawk version (a1789d8a0642987b059431ef0ca7c5d106c31a41)

![image](https://github.com/user-attachments/assets/694fad35-9ebc-4250-92b0-aabd1d733271)
