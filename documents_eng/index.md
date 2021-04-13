[Русский](../documents/index.md)

# Description of the capabilities and functions implemented in the MVP bot

There are three main types of user actions implemented in a  direct targeted assistance bot:
- user profile - allows you to select a status and indicate the basic data necessary for inclusion in the circle and providing direct targeted assistance;
- actions to provide assistance - from requesting assistance to confirming fulfillment of an obligation;
- the manifestation of a network of members connected by common circles of care, the ability to view members of your circle and expand your circle by helping other members.

## FAQ
- [About bot](faq/about_bot.md)
- [How to start using it](faq/how_start.md)
- [Symbols](faq/conventions.md)
- [Description of the menu](faq/menu.md)
- [Possible cases](faq/cases.md)

## User actions 

### Filling in the profile 👤
- [Setting and changing status](actions/change_status.md)
- [User information](actions/about_me.md)
- [Assignment and change of requisites](actions/change_requisites.md)
- [Language change](actions/change_language.md)
- [Remove from bot](actions/delete_from_bot.md)

(_links further will be translated later_)

### Actions in Organizer 🗓
**In favor of other network participants**
- [View and manage your intentions and commitments](actions/show_int_obl.md)
- [Intent creation](actions/create_intent.md)
- [Correction, cancellation or execution of an intention](actions/correction_my_intention.md)
- [Translation of intention into ](actions/creation_of_obligation.md)
- [Fulfillment of obligation](actions/obl_fulfilled.md)


**In their favor**
- [Viewing and managing intentions and obligation to your advantage](actions/show_int_obl_for_me.md)
- [Request to translate intent into obligation](actions/request_for_transfer.md)
- [Keeping or canceling an obligation](actions/save_obligation.md)
- [Request for performance of obligation](actions/request_for_execution.md)

**Archives of obligations**
- [Archive of fulfilled obligations](actions/archive_my.md)
- [Archive of obligations not fulfilled on time](actions/archive.md)

**[Creating a link-invitation to help yourself or needy members of your network](actions/create_invite.md)**

**[Reminder or confirmation of performance of obligation](actions/confirmation_of_transfer.md)**


### Participant lists in the main menu
- [View members and expand your circle](actions/show_circle.md)
- [List of members assisted by the user](actions/list_my_people.md)
- [List of participants who help the user](actions/list_other_people.md)

### Other
- [Getting help about bot operation](actions/faq.md)
- [Support Chat](actions/support_chat.md)

## Alerts
- [About changing the user's status in the circle](notifications/status_changed.md)
- [About creating intent towards the user](notifications/intention_created.md)
- [Request to translate intent into obligation](notifications/request_for_translation.md)
- [Notice of conversion of intention to obligation](notifications/obligation_created.md) 
- [Reminder of the expiration of the term for the fulfillment of the obligation](notifications/reminder_of_obligation.md)
- [Obligation fulfillment notification](notifications/obl_fulfilled.md)
- [Reminder of the need to confirm the fulfillment of the obligation](notifications/reminder_to_confirm.md)
- [Notification of confirmation of the fulfillment of the obligation by the recipient](notifications/obl_received.md)
- [Notification of completion of emergency collection](notifications/end_red.md)


## Database tables
- [users](tables/users.md)
- [events](tables/events.md)
- [statuses](tables/statuses.md)
- [intentions](tables/intentions.md)
- [requisites](tables/requisites.md)
- [circle](tables/circle.md)


---
> [README_rus](../README.md)  |  [README_eng](../README_eng.md)
