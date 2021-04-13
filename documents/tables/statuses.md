[English](../../documents_eng/tables/statuses.md)
# Statuses

| Name          | Type          | Description   |
|:------------- |:--------------|:--------------|
status_id | integer | -
telegram_id | integer | id пользователя из таблицы users
payment | float | необходимая пользователю сумма
finish_date | datetime | дата окончания статуса, если статус красный
create_date | datetime | дата создания статуса
type | varchar | тип статуса (red/orange)
---
> [README_rus](../../README.md)  |  [README_eng](../../README_eng.md)  
> [Описание бота прямой адресной помощи](../index.md)  
> [Смена статуса](../actions/change_status.md)  
