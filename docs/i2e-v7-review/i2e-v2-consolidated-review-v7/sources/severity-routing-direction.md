# User direction: three-level severity, routing and Low observations

Source: C2C Free Work, chat `01a0a6de-7432-7860-b74b-25609038effb`, 2026-11-04.
Scope: revise the design proposal. The earlier instruction to keep the active workflow unchanged remains in force.

## User message 01a1a7d1-23e9-7343-948b-b5398fbf46ce

> i am also thinking we should follow what Steve Yegge's Articles talking about not reporting all the P3s to reduce the review costs and the operating costs for implementation and reviews and all that. Unless we have found the P3 bug or advice changes would break the workflow and be raised to, let's say, P2 or P1 or potentially even P0. That would break the business logic. Then we would change the according priorities and then act accordingly to. Do you think this is a valid move?

## User message 01a1a7d8-1b13-7bf3-a7fa-fbd14fe5b776

> Or do you think we can change the P3, P2, P1, P0 to, like, priority as high, medium, and low, and then we can just drop the low tier? Do you think that's a valid move compared to having, like, P0 to P4, or P3, like four levels or five levels?

## User message 01a1a7db-c6a4-7460-80d6-2c9d214a940f

> Yes, then modify the proposal or the versions to use the severity as the three, and we would also modify the agent routing accordingly. So for severity as high, priority as high, we would use Astra, and medium we would just keep it for so as like earlier plan designs, and for low, we can potentially just drop it, but also keep track of it in case we need to visit in the future.

## Implementation interpretation recorded for review

Use High / Medium / Low for finding severity and for a separate scheduling-priority field. Either High field or Critical technical risk selects Astra ownership. Medium remains Sol-led; Terra retains explicitly planned bounded routine implementation. Low incidental findings stay in existing observations without automatic tickets, repairs or re-reviews. Explicit user-requested work and existing acceptance/failure obligations remain. This interpretation is proposal text, not a claim of runtime enforcement or an independently approved decision.

