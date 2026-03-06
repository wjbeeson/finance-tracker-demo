---
name: create-jira-issue
description: "Guides the user through creating a new Jira issue in the FT project with required acceptance criteria, then confirms before submitting."
---

# Create Jira Issue Skill

## Rules for Creating New Jira Issues

### 1. Required Information — Ask the User

Before creating a Jira issue, you MUST gather the following information from the user. If any required field is missing, ASK for it before proceeding.

#### Required Fields (always ask):
1. **Summary** — A clear, concise title for the issue.
2. **Acceptance Criteria** — This is the MOST IMPORTANT part of any ticket. Every issue MUST include well-defined acceptance criteria. Do NOT create an issue without them.
3. **Issue Type** — e.g., `Task`, `Bug`, `Story`, `Epic`. If not provided, ask the user.

#### Optional Fields (ask if relevant):
4. **Assignee** — Who should work on this issue?
5. **Priority** — e.g., `High`, `Medium`, `Low`.
6. **Labels** — Any labels to categorize the issue.
7. **Components** — Any relevant project components.

### 2. Acceptance Criteria Standards

Acceptance criteria MUST be:
- **Specific** — Clearly state what is expected, not vague or ambiguous.
- **Testable** — Each criterion should be verifiable as done or not done.
- **Written as a checklist** — Use a checklist format so progress can be tracked.

Example format for acceptance criteria in the issue description:
```
## Acceptance Criteria
- [ ] The user can create a new transaction with a name, amount, and date
- [ ] Validation errors are displayed if required fields are missing
- [ ] The transaction list updates immediately after a new entry is added
- [ ] An API endpoint `POST /transactions` exists and returns 201 on success
```

If the user provides vague or incomplete acceptance criteria, help them refine it into specific, testable items before creating the issue.

### 3. Jira Project

- All issues MUST be created in the **Finance Tracker** project with key **FT**.
- Never create issues in any other project or space.

### 4. Issue Description Format

Structure every issue description as follows:

```
## Summary
<Brief description of the task or problem>

## Acceptance Criteria
- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] <Criterion 3>

## Additional Context
<Any extra details, links, or references>
```

### 5. Workflow Summary

1. Ask the user what issue they want to create.
2. Ensure acceptance criteria are provided — if not, ask for them explicitly.
3. Confirm the summary, issue type, and acceptance criteria with the user before creating.
4. Create the issue in the **FT** project using the Jira tools.
5. Report back the created issue key (e.g., `FT-123`) to the user.
