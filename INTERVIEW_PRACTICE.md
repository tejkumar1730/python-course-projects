# Practice with the code open first, then close it

These prompts help you demonstrate understanding. They are not a script for claiming experience you do not have. Begin answers with the facts of this portfolio implementation and distinguish future improvements from completed features.

## Your two-minute project structure

1. **Problem:** one sentence describing what a candidate/employer or inventory/API user needs.
2. **Implementation:** name the interface, Python component, tables and MySQL connection.
3. **One flow:** explain an actual example from input through validation to stored data.
4. **One failure:** explain an invalid input or unauthorized action that the tests reject.
5. **Limit:** describe one missing production feature and what you would learn next.

## Cross-project questions

| Question | A useful answer to practice |
|---|---|
| What is CRUD? | Create, read, update and delete. Name a concrete command or endpoint for each in the project you are showing. |
| Why MySQL? | It provides relational tables, constraints and transactions. These projects use it to practice persistent data and relationships. Do not claim a performance comparison you did not run. |
| What is a primary key? | A unique row identifier. Foreign keys refer to it to connect related rows. Show one real relationship in the schema. |
| How do you prevent SQL injection? | Inventory passes parameters separately to the connector; Django/DRF use ORM queries. Never combine untrusted text into a SQL statement. |
| Why validate on the server? | A browser or API client can bypass frontend checks. The server must reject invalid or unauthorized changes. |
| Why database constraints too? | Another program or a simultaneous request can bypass an earlier application check. Constraints enforce rules at storage time. |
| What is a transaction? | Several database steps succeed together or roll back together. Stock balance and its movement record must agree. |
| How are passwords stored? | Django hashes login passwords through its user APIs. Environment files hold local database credentials and are excluded from Git. These are different types of secrets. |
| Authentication versus authorization? | A valid login/token identifies a user. Role checks and ownership filters control which records the user may change. |
| Why Decimal for money? | Binary floating-point cannot represent many decimal fractions exactly. Decimal and MySQL DECIMAL preserve fixed decimal amounts. |
| What is a migration? | A versioned Django schema change. `makemigrations` records model changes and `migrate` applies them. It is not the same as inserting demo rows. |
| What did tests prove? | Explain the named cases actually run in the validation record. Passing tests is evidence for those cases, not a guarantee against every bug or a load test. |
| Did you build it by yourself? | Explain the AI assistance honestly, then show the parts you reviewed, changed and can explain. |
| Was this a company project? | No. It is a personal learning portfolio using fictional sample data. |

## A blank practice log

Fill this in yourself. No boxes are pre-checked.

- [ ] I installed the dependencies and started MySQL.
- [ ] I ran all three demos myself.
- [ ] I read each project's models/schema, views/service and tests.
- [ ] I can explain the owner checks in the Job Portal and API.
- [ ] I can explain transaction rollback in Inventory.
- [ ] I tried a duplicate SKU, a negative value and an unauthorized request.
- [ ] I made and tested one small change without copying an answer blindly.
- [ ] I updated resume dates and wording to match my actual work.
- [ ] I can show GitHub commits and explain the current code.

Optional personal record (fill after doing the work):

| Date | Project | Change or experiment | Result | What I learned |
|---|---|---|---|---|
| | | | | |

## Telugu-English rehearsal prompts

- "Ee project personal portfolio kosam ippudu complete chestunnanu. Sample data tho practice chesanu" means you are completing it now; say you practiced only after actually doing so.
- "Ee request first validation ki, next database operation ki, last response ki velthundi" is a starting outline. Then point to the real files and explain each step.
- "Ee part ki AI assistance teesukunnanu; nenu review chesi ardham chesukunna parts explain chesthanu" acknowledges assistance. Do not memorize technical answers you cannot trace in the code.

Practice technical explanations in whichever language lets you reason clearly, then rehearse concise English answers for the interview.
