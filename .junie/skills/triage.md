# Triage Skill

## Trigger

This skill activates when the user types the `/triage` command. Examples include:

- "/triage"
- "/Triage"

Do NOT activate this skill for casual greetings or general questions — only when the user explicitly invokes `/triage`.

## Response Format

When triggered, respond with **all three** of the following, in this order:

### 1. Greeting

Reply with a warm, friendly greeting that matches the tone and time of day of the user's message. Keep it natural and conversational.

### 2. Top 5 Open Issues by Priority

Fetch and display the user's top 5 **open** Jira issues assigned to the currently authenticated user in the **FT** project, ordered **descending by priority** (most important issues first).

**Important:** Only show open issues — exclude any issues with a status category of "Done" (i.e., completed/resolved issues must not appear).

- Use JQL: `project = FT AND assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC`
- Limit results to 5.
- Display each issue in a concise list format including:
  - Issue key (e.g., `FT-42`)
  - Priority
  - Status
  - Summary

Example output format:

> 👋 Good morning! Hope your day is off to a great start!
>
> 📋 Here are your top 5 **open** issues by priority:
>
> | # | Issue | Priority | Status | Summary |
> |---|-------|----------|--------|---------|
> | 1 | FT-10 | Highest | In Progress | Fix critical auth bug |
> | 2 | FT-7  | High    | To Do       | Add export feature |
> | 3 | FT-15 | Medium  | In Progress | Update dashboard layout |
> | 4 | FT-3  | Medium  | To Do       | Refactor transaction model |
> | 5 | FT-20 | Low     | To Do       | Update README |
