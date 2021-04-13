[Русский](../../documents/about_exodus/algoritms.md)   

# Interaction algorithms in the Exodus concept

Algorithms and rules for maintaining records of mutual intentions and obligations, according to the Exodus concept, are described.

## Organization of monthly support in the bot for direct targeted assistance
(_Implemented in a working prototype, a telegram bot_)

The algorithm for providing monthly support is as follows:  
1. Filling out the profile, indicating the monthly amount: SS💰 = 🙏 required support amount = missing support amount; information about the user, chat for communication with them, payment details or conditions for assistance.  
2. 👥->n❤️ - members of this user's support circle, in response to the request, set their intentions, the amount of intentions is shown (nn❤️/SS🙏).  
3. If nn <SS or nn> SS then the participants can adjust their intentions by increasing or decreasing them, or by inviting additional participants.  
4. Participants who are sure they want and can help a given user, translate the intention into an obligation ❤️-> 🤝; the obligation must be fulfilled; the obligation immediately reduces the required amount of the goal 🙏 = 🙏 - mm🤝; participants can immediately fulfill the intention, then the current amount of the goal is reduced as well, follows the point 7.  
5. The obligation is kept until demanded or until the end of the month, and can be requested for fulfillment; (in the developed version, the obligations must be cleared between participnts at the end of the month (approximately on the 25th day of each month)).  
6. As soon as the obligation is fulfilled, the sender notifies the recipient about it: 🤝-> 👍. 
7. The recipient must confirm the fulfillment. 
8. The fulfilled obligation 👍 is stored in the archive.  

Оn the 1st day of every month:
1. Unfulfilled intentions are nullified, and their author leaves the circle of assistance to the user.
2. Fulfilled obligations are automatically renewed as an intention and can later be adjusted, canceled, or fulfilled.
3. Unfulfilled and unconfirmed obligations are transferred to the archive of uncompleted transactions.

All participants can see the status and current state of the user's fundraising process. Help Circle members can see the contributions of everyone who has shown intent to support that member. Circle members can negotiate strategies and terms of assistance outside the bot.

# Organization of emergency support in the bot for direct targeted assistance

(_Implemented in a working prototype, a telegram bot_)

The algorithm for providing emergency support is as follows:

1. Filling out the profile, indicating the amount for emergency assistance SS💰 = 🙏 = missing amount and the deadline for receiving assistance in days (until the end of the current month); information about the user, chat for communication with them, details or conditions for providing assistance.
2. All members of the user's network see a request for help. The more members a given user has helped before, the more powerful their support network will be. All members of the support network can invite their friends to help anyone in need within their network.
3. In emergency assistance, support is accepted only in the form of an obligation 🤝; each obligation reduces the goal 🙏 = 🙏-🤝 that the network members see.
4. The obligation in case of the emergency must be fulfilled before the fixed deadline.
5. The recipient must confirm the fulfillment of the obligation in his favor.
6. As soon as the amount of the fulfilled obligations reaches or exceeds the originally declared amount of the fundraising 💰, the collection is considered to be successfully completed.
7. Upon completion of the collection or upon expiration of the stated collection period, the user returns to his previous status.

For all network participants, the rule is first to close all emergency requests. Though, the principle of voluntariness and feasibility of assistance remains - the participant may consider the situation of force majeure to be unreliable or insignificant and leave the circle of support of the one who requested assistance. They can stay in common circles through connections with other members.

## Clearing of mutual obligations
(_А challenge to develop algorithms and solutions_)

Once a month - every 25th of the month, for example - it is necessary to analyze stored and unfulfilled obligations. It is important to mind that some targeted obligations cannot be transferred to another network user.

1. Just before the clearing procedure, the network participants receive a notification that the end of the month is approaching and obligations must be fulfilled. They also receive a message about the upcoming procedure of clearing of mutual obligations.
2. The user marks in the database the obligations that they intend to mutually subtract with someone in the network.
3. Then, using the social graph, closed chains of obligations between the participants are revealed.
4. The value of each obligation is reduced by the value of the smallest obligation in the chain.
5. Obligations that fell under the reduction are automatically transferred to the status of fulfilled.
6. Users receive updated data on their obligations and a reminder to fulfill them by the end of the month.

We can also implement an algorithm for the direct transfer of obligations in chains from one user to another: 
1. If user A has an obligation to user B, and user B has the same obligation to user C, then these two obligations are replaced by one final - user A to user C.
2. All participants in such a chain must receive appropriate notifications of changes in their obligations.
3. Within such algorithm, the way of transferring fulfilled obligations to the archive may differ (independently or depending on the final obligation's fulfillment.

Possible algorithmic solutions for the clearing of obligations:
- [Finding closed cycles in a graph](https://coderoad.ru/29244965/%D0%9D%D0%B0%D1%85%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B2%D1%81%D0%B5%D1%85-%D0%B7%D0%B0%D0%BC%D0%BA%D0%BD%D1%83%D1%82%D1%8B%D1%85-%D1%86%D0%B8%D0%BA%D0%BB%D0%BE%D0%B2-%D0%B2-%D0%B3%D1%80%D0%B0%D1%84%D0%B5)
- [Solving the problem of the maximum flow in these cycles of the graph. Deduction of the maximum flow](https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B4%D0%B0%D1%87%D0%B0_%D0%BE_%D0%BC%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%BC_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA%D0%B5#:~:text=%D0%92%20%D1%82%D0%B5%D0%BE%D1%80%D0%B8%D0%B8%20%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8%20%D0%B8%20%D1%82%D0%B5%D0%BE%D1%80%D0%B8%D0%B8,%D1%81%D1%83%D0%BC%D0%BC%D0%B0%20%D0%BF%D0%BE%D1%82%D0%BE%D0%BA%D0%BE%D0%B2%20%D0%B2%20%D1%81%D1%82%D0%BE%D0%BA%20%D0%BC%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0) 
- [Python-ready libraries](https://networkx.org/documentation/networkx-1.9.1/reference/generated/networkx.algorithms.cycles.simple_cycles.html#simple-cycles)

_There may be other algorithms for the reduction of mutual obligations in the reference network. It is a problem for further development_.

## Pool of mutual intentions
(_There are no stable digital tools ready for the user yet, but there is a core of the system that registers common initiatives, keeps accounts of intentions and obligations, implies the rules of their transformation and execution according to the principles of the Exodus concept. The platform has an API for developing external applications_)

1. Participants of the virtual register set the rules and algorithms for the future interaction within the pool, in case of an insured event: notification rules, validation check, response time, a form of assistance, the minimum and maximum amount of assistance, etc. 
2. At the beginning of the month, a pool of participants is formed by fixing an intention - the maximum amount of each's contribution if an insured event occurs. It is a pre-recorded agreement on participating in the future. The amount of intention is voluntary and depends on the participant's ability to be in the zone of their personal "harmlessness".  
3. Everyone knows the value of the total pool as the sum of everyone's intentions. The resources remain with each user until the insured event occurs.
4. The intention pool itself is virtual. It is not stored or accumulated anywhere, no one alone disposes of it.  
5. When an insured event occurs, the user of the register informs all participants of the pool about the emergency and announces the amount of the request 💰 to cover damage or compensate for costs.
6. The share of participation for each in the pool is determined as the ratio of the declared amount to the pool's volume. Share of one's participation = request / total pool.  
7. The contribution of each is defined as the part of their originally recorded intentions. Participation = share of the declared goal * intent originally recorded.  8. The pool members discuss the situation within the agreed period - for example, within a day.
9. Everyone decides whether to participate. You can either translate your intention into obligation or leave the pool by withdrawing the intention. This approach makes it possible to implement the principles of parity relations and mutual responsibility.
10. Since the network is referential and transparent, the reliability of events is either obvious to many or not. During the discussion, a reconfiguration of the insurance pool around the given user may occur:
- several people will fall out of the pool, having withdrawn their intentions - by terminating the contract of participation in the given pool;
- the situation will not be recognized as trustworthy and the pool with this user will disintegrate;
- the situation will be recognized as trustworthy, and the participants will confirm their intention to participate;
- pool members can recognize the situation as trustworty, but adjust the request amount within reasonable limits.
11. Losing a member of the pool increases the share of participation for those who remain. By leaving a pool, a participant loses support from the participants of that pool. It is a self-regulating and self-adjusting process. The obligation amount of each in such case is updated automatically.
12. Members who have left a certain pool can create another pool, with their own rules and circle of participants.
13. The participants of the previous pool fulfill their obligations within the agreed period.
14. The total pool available is recalculated, as the amount of assistance already provided is deducted from it.
15. At the end of the month, the entire monthly insurance pool may have covered participants' requests, or a virtual reserve remained.
16. Pool members decide what is done with the reserve. These funds can be used to expand and develop a network of trust, be distributed among those in need of monthly support, etc.

When, due to the arrival of new participants and an increase in the total pool, the reserve in the virtual register becomes significant, it is possible to expand from joint damage / cost coverage to joint social design.

## Social design in the Exodus paridigm

(_There are no stable digital tools ready for the user yet, but there is a core of the system that registers common initiatives, keeps accounts of intentions and obligations, implies the rules of their transformation and execution according to the principles of the Exodus concept. The platform has an API for developing external applications_)

1. Each initiative has a goal and a price for its achievement, which is announced within the social network.
2. Participants who share this goal use intentions to indicate their interest and opportunity to participate, immediately reinforcing their desires with available resources.
3. The sum of the intentions is compared to the "cost of the issue".
4. If the funds raised are insufficient, then either:
- the participants will increase their intentions;
- they will invite other participants;
- they will refuse to participate in this case;
- or the applicant will reduce his ambitions, etc.  
A balancing of what is desired and what is possible occurs. Moreover, all funds are decentralized and are not frozen for the collection period.
5. When the sum of intentions has reached the required "goal," the collection participants get notified of it and proceed to the implementation stage, agreeing on the rules and steps necessary to achieve the common goal. If the initiative has not collected sufficient funds by the set deadline, it is considered irrelevant, and all intentions in its favor are canceled.
6. The initiative disappears from the "active collections".
7. In the case of a successful collection, participants fulfill their obligations in a form convenient to everyone, creating rules for interaction in that specific context.
8. The initiator of the collection confirms the fulfillment of obligations. All fulfilled obligations are noted in the archive.
9. All participants of the collection remain in the same network and are notified of the initiative's progress.

# Elements of a decentralized network of trust and the Exodus ecosystem

- Circle of Help - people who provide direct support to the Exodus user;
- Local Decentralized Support Network - Exodus network users linked together through common support circles;
- Insurance pool - members of the Exodus network, who have declared their intentions of mutual support in case of agreed insured events;
- Social design network - members of a social network of trust, supporting each other's initiatives, organizing crowdfunding, crowdinvesting, crowdsourcing, etc. 
The network is expanding due to an increase in the number of people who receive regular support, get invited in insurance pools, and participate in social initiatives.

_Need to be developed: possibility to display the graph of user's social connections and help circles. User should be able to see and filter out different elements: network members who need monthly support, current fees, etc._

----
> [README_rus](../../README.md)  |  [README_eng](../../README_eng.md)    
> [How to interact in a decentralized web of trust](../about_exodus/paradigma.md)  
> [Features of mutual assistance in the Exodus concept](../about_exodus/features.md)   
> [Description of the bot for direct targeted assistance](../../documents_eng/index.md)  | [Change of status](../../documents/actions/change_status.md)



