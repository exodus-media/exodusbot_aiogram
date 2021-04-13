[English](../../documents_eng/actions/show_circle.md)

# Просмотр участников и расширение своего круга

Пользователь, помогая или принимая помощь, образует связи с другими пользователями. Данная функция позволяет просмотреть всех участников, с которыми связан пользователь. Для каждого участника показывается краткая информация - его [статус](../actions/change_status.md) и текущая ситуация сбора. Для участника в ["Оранжевом 🔆"](../statuses/orange.md) статусе показывается сумма намерений в пользу этого участника ❤️ и недостающая сумма сбора 🙏. Для участников в ["Красном 🆘"](../statuses/red.md) статусе - недостающая сумма сбора 🙏 и оставшийся срок в днях. 

Есть вариант дополнительно расширить свой круг. Это происходит за счет исполнения следующего функционала:
- получаем свой круг -> для каждого участника моего круга строится его круг -> проходим круг каждого из участников и добавляются в круг оранжевые, которых еще нет в круге.  

Данные связи фиксируются в таблице [circle](../tables/circle.md). Пара значений uid и pid указывают на связь пользователей с данными id (ребро социального графа).

---
> [README_rus](../../README.md)  |  [README_eng](../../README_eng.md)  
> [Описание бота прямой адресной помощи](../index.md)