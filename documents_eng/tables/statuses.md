[Русский](../../documents/tables/statuses.md)
# Statuses

| Name          | Type          | Description   |
|:------------- |:--------------|:--------------|
status_id | integer | -
telegram_id | integer | user id from the users table
payment | float | the amount required by the user
finish_date | datetime | end date of the status, if the status is red
create_date | datetime | status creation date
type | varchar | status type (red/orange)

---
> [README_rus](../../README.md)  |  [README_eng](../../README_eng.md)   
> [Description of the bot for direct targeted assistance](../../documents_eng/index.md)  
> [Change of status](../actions/change_status.md) 
