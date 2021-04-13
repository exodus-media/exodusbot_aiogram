[Русский](../../documents/actions/change_status.md)
# User statuses

There are ​​three types of User statuses:

- [Green ✅](../statuses/green.md) - "I am ready to support other network members, also I am not in need right now". Such a participant can help others, the status of the current request and the details for assistance are not shown for him.
- [Orange 🔆](../statuses/orange.md) - "I need monthly support; I can still support other network members". For such a participant, the amount of Intentions in his favor and the amount that remains to be funded are shown to every member of his Circle of Support.
- [Red 🆘](../statuses/red.md) - "I need urgent support within a limited time".

# Change of status

After registration, the user is given the "Green ✅" status by default. Then they can change the status in their user profile. When a user changes their status to "Red 🆘" or "Orange 🔆", then participants from his Circle of Support will receive a corresponding [notification](../ notifications / status_changed.md).

## Green -> Orange

If the user needs monthly assistance, they can set the status "Orange 🔆".
In this case, the status "orange" is written in the status field in [the users table](../tables/users.md).
In [the statuses table](../tables/statuses.md), in the line with the required uid and type, the payment and sdate fields are filled.

## Green -> Red

If the user needs urgent help, they can set the status "Red 🆘".
In this case, the status "red" is written in the status field in the users table.
In the statuses table, in the line with the required uid and type, the payment, sdate, ndays fields are filled.

## Orange, Red -> Green

If the user does not already need Support, they can set the status "Green ✅".
In this case, the status "green" is written in the status field in the users table.
All Intentions in favor of this participant are canceled. But the Obligations in their favor remain and must be Fulfilled.

## Orange -> Red
If the user needs urgent help, they can set the status "Red 🆘".
In this case, the status "red" is written in the status field in the users table.
In the statuses table, in the line with the required uid and type, the payment, sdate, ndays fields are filled.
All users who have declared Intentions in their favor are notified with a request to convert Intentions into Obligations.
This user's Intentions and Obligations in favor of the other their network members are Canceled, or "frozen".

## Red -> Green / Orange
After the declared Support is received or the declared urgent period is over, the user returns to their previous status.
In this case, the status "green" / "orange" is written in the status field in the user table.

---
> [README_rus](../../README.md)  |  [README_eng](../../README_eng.md)     
> [Description of the bot for direct targeted assistance](../../documents_eng/index.md)  | [Menu Description](../faq/menu.md)
