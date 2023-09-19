<details open><summary><h2>📚 Description</h2></summary>
This bot is designed to help people who are faced with the problems of obtaining housing, bought under a contract of participation. With its help you can calculate the penalty, estimate how much on average will get money from the developer for poorly made repairs or ask a question to AI-lawyer

</details>
<details><summary><h2>🛠️ Tech Stack</h2></summary>
<img src="https://img.shields.io/badge/Python-%2314354c.svg?logo=Python&logoColor=white&style=flat" alt="Python" /> <img src="https://img.shields.io/badge/Django-%23092e20.svg?logo=django&logoColor=white&style=flat" alt="Django" /> <img src="https://img.shields.io/badge/Django-REST-ff1709?style=flat&logo=django&logoColor=white&color=ff1709&labelColor=gray" alt="DRF" />  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white&style=flat" alt="Docker" /> <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white&style=flat" alt="PostgresQL" /> <img src="https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white&style=flat" alt="redis" />

</details>
<details ><summary><h2>🏗️ Installation</h2></summary>

```
git clone git@github.com:akkrn/help_ddu_bot.git
```
Create your own .env with data like in .env.example
Start to compose app:
```
sudo docker compose up
```

For the first time should be imported table from data by bash script
```
sudo ./sh/import_keyratecbr.sh
```

And rerun compose
```
sudo docker compose up --build
```
</details>
