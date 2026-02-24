# Commit Workflow Skill

## Rules for ALL Commits

### 1. Jira Ticket Requirement
- Every commit MUST be associated with a Jira ticket.
- If no Jira ticket is provided by the user, ASK for one before doing any work.
- The space for this project is "Finance Tracker ("FT")
- The Jira ticket ID (e.g., `FT-42`) is used directly as the branch name. Never include any other characters. 

### 2. Branch Management
Before making any commits, follow this workflow:

1. **Fetch from origin:**
   ```
   git fetch origin
   ```
2. **Check if a remote branch exists** with the ticket ID as the name:
   ```
   git ls-remote --heads origin <TICKET-ID>
   ```
3. **If the remote branch exists**, check it out and pull latest:
   ```
   git checkout <TICKET-ID>
   git pull origin <TICKET-ID>
   ```
4. **If the remote branch does NOT exist**, create a new local branch:
   ```
   git checkout -b <TICKET-ID>
   ```

### 3. Branch Naming Convention
- The branch name IS the Jira ticket ID. Nothing else. Capitalize the letters.
- Example: `FIN-42`, `PROJ-108`, `DEMO-7`

### 4. Commit Message Format
- Every commit message MUST be prefixed with the Jira ticket ID (which is also the branch name) in square brackets.
- Every commit message MUST include `@junie-agent` at the end.
- Format: `[<TICKET-ID>] <description> @junie-agent`
- Example: `[FIN-42] Add transaction filtering endpoint @junie-agent`

### 5. Commit Flow Summary
For every task:
1. Identify or request the Jira ticket number
2. Fetch from origin and check if a branch named exactly `<TICKET-ID>` exists remotely
3. Pull the remote branch OR create a new local branch with that name
4. Make changes and commit with `[<TICKET-ID>]` prefix and `@junie-agent` tag in the message
5. Push the branch to origin

### 6. CI Integration (Optional)
- If the commit is intended for automated PR creation and Junie analysis,
  append `@junie-agent` to the commit message.
- Example: `[FIN-42] Add transaction filtering endpoint @junie-agent`
