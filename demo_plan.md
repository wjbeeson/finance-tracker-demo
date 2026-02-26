
# Junie AI Agent — Full Demo Plan

---

## Slide 1: Title & Meet Alex [INFO]

Visual: The presentation title. Below it, a simple graphic of "Alex," an Acme Corp Developer. Show the high-level presentation outline. No bullet points on screen — the scene is painted verbally.

Speaker Notes:
- Open with 2-3 quick, real stats about AI adoption among developers. Don't linger — these are table stakes, not the point.
- Pivot: acknowledge the audience already knows this. Reframe the session as something they haven't seen — a live, end-to-end walkthrough through a single developer's real workflow.
- Introduce Alex. Name, role, stack, one line. He's the lens, not a character study.
- State the demo goal plainly: one bug, one window, triage to merge.
- Let the slide visual do the heavy lifting — Alex's profile, the presentation outline. You're just bridging into the demo.

Example Script: "Over 75% of developers are already using AI in their workflow. The productivity numbers are everywhere — faster code generation, fewer context switches, shorter cycle times. But you all already know the stats. So today, instead of talking about what AI can do, I want to walk you through what it actually looks like — end to end, live, through the eyes of a real developer. This is Alex. Backend engineer at Acme Corp — Python, Flask, Redis. He's got a bug in his queue this morning. By the end of this session, that bug will be triaged, fixed, reviewed, merged, and closed in Jira — and Alex won't leave his IDE once. Let's get him set up."

---

## Slide 2: The Enterprise Blocker [INFO]

Visual: A graphic of a "Blocked" sign or a lock, representing Acme Corp's strict Security Lead.

Speaker Notes:
- Keep this inside Alex's story. The Security Lead is a character blocking Alex, not a prompt for audience participation.
- Acknowledge the immediate hurdle before any tooling: the Security Lead.
- Highlight the concern: codebase leaks, compliance risks, AI training on proprietary data.
- Pivot: solve this immediately so Alex can actually code. The audience will recognize the scenario without being asked to raise their hands.

Example Script: "Alex wants to get started, but he can't. Before he's allowed to use any AI tooling, Acme Corp's Security Lead has shut it down. The concern is straightforward: proprietary codebase data leaking to a third-party model, compliance risks, code being used to train someone else's AI. Until that's resolved, Alex isn't touching anything. So let's resolve it."

---

## Slide 3: LIVE DEMO: Security & Zero Data Retention [DEMO]

Visual: A high-resolution screenshot of the JetBrains Product Data Collection page, cropped to the key passage about organizational licenses. The critical phrases — "disabled by default" and "opt-in only" — are highlighted with an animated yellow underline. A second screenshot shows the JCP dashboard toggle.

Speaker Notes:
- Address the Security Lead's main fear: AI models training on proprietary code.
- Point to the blown-up screenshot of the official JetBrains legal page to prove Zero Data Retention and explicit data policies.
- Highlight that detailed code collection is strictly opt-in only.
- Switch live to the JetBrains Control Panel (JCP) to show the global opt-in/opt-out toggle.
- Present fallback options: on-premise deployment and Bring Your Own Key (BYOK).

Example Script: "Let's address the Security Lead's biggest fear: proprietary codebase data being used to train third-party AI models. Here is the exact passage from the official JetBrains Product Data Collection policy, blown up on screen. I want to highlight this specific line: detailed code-related data collection is strictly disabled by default. It is opt-in only, meaning it requires explicit consent from a company admin. Now, let me switch over live to the JetBrains Control Panel. Right here is where Alex's admins have total control over that global opt-in or opt-out button. Alex's code stays his. And finally, if these strict cloud security policies still aren't enough, we also offer fully on-premise deployment options and Bring Your Own Key — so Alex's team can connect their own existing API keys directly, with no data routed through JetBrains at all."

Demo Actions:
- Display the blown-up screenshot of the key passage with animated highlights over "disabled by default" and "opt-in only."
- [BROWSER] Switch live to the JCP dashboard.
- [BROWSER] Point out the global opt-in/opt-out toggle button.
- Fallback: Pre-recorded GIF of the JCP toggle in case of connectivity issues.

---

## Slide 4: The Platform (ACP) [INFO]

Visual: A clean graphic defining ACP (Agent Client Protocol) connecting IDEs to Agents.

Speaker Notes:
- Security is cleared; Alex needs flexibility.
- Define ACP: agent-agnostic platform standard.
- Frame the value as future-proofing and protection from lock-in, not just a technical protocol.
- Use a memorable closing line to make the concept stick.

Example Script: "Security is cleared. Now, Alex wants to set up his tools, but he wants flexibility. At JetBrains, we standardize on ACP — the Agent Client Protocol. It's an agent-agnostic platform standard. Six months from now, a better agent might exist. Maybe Alex's team wants to try it. With ACP, they swap it in with one click — no migration, no re-tooling, no vendor lock-in. JetBrains built the platform, not the cage."

---

## Slide 5: LIVE DEMO: Installing the Brain [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE.

Speaker Notes:
- Show one-click install of OpenCode to demonstrate ACP's openness.
- Explain the swap to Junie with explicit justification for why a third-party agent was shown first.
- Value: Junie is explicitly tuned for optimal performance inside JetBrains IDEs.

Example Script: "Installing a new agent shouldn't be a DevOps ticket. Watch: Alex opens the ACP Registry, one click, and he has OpenCode running inside PyCharm. I'm showing you this because in enterprise, different teams may already have preferred agents. ACP means they're not locked out. But because Alex is living inside a JetBrains IDE today, he's going to swap over to our agent, Junie. Junie is tuned specifically for optimal performance and deep integration inside JetBrains IDEs — it leverages the full power of the IDE's inspections, refactorings, and compiler under the hood."

Demo Actions:
- Open the ACP Registry.
- Quick-install OpenCode (or Mistral).
- Swap the active agent from OpenCode to Junie.
- Fallback: Pre-recorded GIF of the ACP registry install and agent swap.

---

## Slide 6: LIVE DEMO: Configuration & The Brain [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE settings. When discussing the three-layer architecture, display the following chart:

| Layer              | Model                      | What It Does                                              |
|--------------------|----------------------------|-----------------------------------------------------------|
| Code Completion    | Mellum (JetBrains)         | Predicts new code at cursor as you type                   |
| Next Edit Suggest. | Separate SLM (JetBrains)   | Predicts changes to existing code based on recent edits   |
| Agentic Reasoning  | Configurable (e.g., Opus 4.6) | Multi-step planning, multi-file changes                |

Speaker Notes:
- Junie is installed, but Alex needs to configure it to fit his specific needs.
- Show the base model swap feature.
- Select Opus 4.6 — tops the leaderboards, most consistent and reliable outputs for complex enterprise logic.
- Briefly introduce the three-layer AI architecture using the on-screen chart. Keep the explanation concise — save deep technical details (parameter counts, training methodology) for Q&A if asked.
- Transition: the brain is set, but it needs tools (MCP).
- Reference: [[1]](https://blog.jetbrains.com/ai/2025/04/mellum-how-we-trained-a-model-to-excel-in-code-completion/) — Mellum is JetBrains' proprietary 4B-parameter code completion model trained from scratch on ~4T tokens of permissively licensed code. Uses fill-in-the-middle (FIM) training, refined with RLAIF. Sub-200ms latency, zero quota cost. Specialized variants: mellum-python, mellum-jotlin, mellum-web. Can run locally via Ollama/LM Studio.
- Reference: [[2]](https://blog.jetbrains.com/ai/2025/12/next-edit-suggestions-now-generally-available/) — NES uses a separate, larger SLM (not Mellum). Context is recent edit history, not current file. Leverages deterministic IDE refactoring actions (e.g., Rename) for multi-file propagation. Sub-200ms latency, zero quota cost.
- Reference: [[3]](https://www.jetbrains.com/help/ai-assistant/next-edit-suggestions.html) — Configurable at Settings | Tools | AI Assistant | Features. Options for chaining suggestions, per-language control, refactoring suggestions.

Example Script: "Junie is installed, but it still needs to be configured. Alex needs a model that can handle complex enterprise logic. Right here in the settings, Alex can swap the underlying base model to whatever works best for his current task. For this demo, he's going to set it to Opus 4.6 — it currently tops the leaderboards and delivers the most consistent, reliable outputs for complex enterprise reasoning, which is exactly what Alex needs. Quick note: Opus 4.6 isn't the only AI running in Alex's IDE. There are actually three layers. This chart breaks it down. Mellum — JetBrains' own model — handles code completion at the cursor as Alex types. Next Edit Suggestions — a separate model — watches Alex's edits and propagates changes to related code. And the base model powers Junie's agentic reasoning. Mellum and NES are both built by JetBrains, both under 200 milliseconds, both zero quota cost. The chart's on screen if you want a photo. But while the brain is powerful, it still can't see Alex's specific project ecosystem. To fix that, we need to move to the biggest configuration of all: MCP."

Demo Actions:
- Open Junie's configuration settings.
- Click the base model dropdown.
- Select Opus 4.6.
- Display the three-layer architecture chart.
- Fallback: Pre-recorded GIF of the settings panel and model dropdown.

---

## Slide 7: LIVE DEMO: The Toolbelt (MCP) [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE.

Speaker Notes:
- Introduce MCP — the Model Context Protocol.
- Install Websearch MCP live.
- Demo: ask a contextually relevant Redis/Flask question in Chat Mode.
- Show preconfigured Jira and Git MCP servers.
- Foreshadow scoping: mention that MCP servers and skills can be scoped globally or locally — more on this soon.

Example Script: "To give Junie access to external tools, we use MCP — the Model Context Protocol. MCP is how Alex connects Junie to everything outside the IDE. Let me install one live right now — Websearch. Alex has a Redis caching bug on his plate today, so let's ask Junie: 'What are the common pitfalls of Redis cache invalidation in Flask applications?' See — Alex didn't leave the IDE, didn't open a browser tab, didn't break his flow. For the heavy lifting later, I've also preconfigured Junie with Jira and Git MCP servers, along with a few custom skills. I've scoped these tools specifically to this project — we'll dig into how scoping works in a moment."

Demo Actions:
- Open the MCP configuration panel and install Websearch.
- Open Chat Mode, ask: "What are the common pitfalls of Redis cache invalidation in Flask applications?" React to the answer.
- Show the installed Git and Jira MCP servers in the settings panel.
- Fallback: Pre-recorded MP4 of the Websearch install and Chat Mode query.

---

## Slide 8: The Playbook [INFO]

Visual: The Playbook Flowchart (Brainstorming vs. Writing Code decision tree).

Speaker Notes:
- Now that the tools are configured, Alex needs a framework for deciding which mode to use.
- Introduce the flowchart as the map for the rest of the demo.
- Tell the audience this will be referenced throughout — they should take a mental snapshot.

Example Script: "Alex's toolbelt is set. Now he needs to know how to use it. Not every task requires the same approach — and using the wrong mode wastes time or produces worse results. This flowchart is Alex's decision framework. Depending on the task, he'll use Junie in different modes. We'll reference this throughout the entire demo, so take a mental snapshot."

---

## Slide 9: The Incident (Story) [INFO]

Visual: The Jira board showing the P3 bug in the To Do column, assigned to Alex.

Speaker Notes:
- Set the scene: 10:00 AM, coffee is ready, bug drops.
- Show the Jira board with the ticket in To Do. This is the "before" state — the audience will see it move to Done on Slide 20.
- Quantify the pain explicitly: name every tool Alex would normally context-switch through. This gives the audience a mental scoreboard to track for the rest of the demo.
- Transition to live demo to show the fix.

Example Script: "Alright, Alex's environment is perfectly tuned. Let's get back to his story. It's 10:00 AM, his coffee is finally cool enough to drink, and a P3 bug drops into his queue. Let me show you the board right now — there's the ticket, sitting in To Do. In a typical workflow, this bug takes Alex through six different tools: Jira to read the ticket, his browser to research the issue, the IDE to write the fix, the terminal to run tests, GitHub to open the PR, and back to Jira to close the ticket. Six context switches. Today: one window, zero switches. Let's watch."

Demo Actions:
- [BROWSER] Open the Jira board. Show the P3 ticket in the To Do column.

---

## Slide 10: LIVE DEMO: Triage & Ask Mode [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE.

Speaker Notes:
- Use a /triage command to trigger a custom skill that pulls Jira tickets automatically.
- Reference the flowchart: brainstorming + context spread across many files = Junie Ask Mode.
- Ask Junie to walk through the plan step by step AND flag anything missing or underspecified in the requirements.
- Emphasize maturity: Ask Mode is read-only. Better plans = better generation.
- When Junie flags the missing acceptance criteria, react naturally. This is a key moment — the AI caught something humans missed before any code was written.
- Alex acknowledges the gap but scopes it out of the current fix. He'll flag it back to the PM. This is realistic developer behavior.

Example Script: "Alex starts his day. He types /triage — a custom command I've configured as a Junie skill. Junie automatically checks his Jira MCP, pulls down the active P3 issue, and presents a summary. No browser. No alt-tab. No Jira board. Now, referencing our playbook flowchart: Alex needs to brainstorm a fix, but the context for this bug touches several different files. This is not a quick inline change — so Chat Mode isn't the right fit. Alex switches to Junie Ask Mode. He asks Junie to walk him through how it would solve this issue step by step, and to flag anything that seems missing or underspecified in the acceptance criteria. Why Ask Mode and not Auto Mode? Ask Mode is read-only — it prevents the AI from modifying any code. This is a mature workflow: Alex fully understands and can edit the plan before anything executes. And here's the key insight — AI always generates better code when it has a clear plan first. (Wait for Junie to respond.) Now look at this. Junie didn't just write a plan — it flagged a gap in the acceptance criteria. The ticket says the cache should invalidate when data is updated, but it says nothing about what happens when Redis is unreachable. Alex didn't catch it. The PM didn't catch it. Junie identified a missing failure-handling case before a single line of code was written. This is why we plan first. Alex notes it — he'll flag it back to the PM later — but the P3 fix doesn't require it. He moves forward with the current scope."

Demo Actions:
- Type: /triage
- Watch Junie automatically pull the active Jira ticket via the custom skill.
- Swap to Junie Ask Mode.
- Prompt: "Walk me through how you would solve this issue step by step. Flag anything that seems missing or underspecified in the requirements."
- React to the missing acceptance criteria flag when Junie surfaces it.
- Fallback: Pre-recorded MP4 of the /triage command pulling the Jira ticket, generating the plan, and flagging the missing AC.

---

## Slide 11: STRATEGY: Skills vs. Guidelines [INFO — INTERMISSION 1]

Visual: Simple two-column layout. Left: "Skills" labeled "Conditional" with an on-demand icon. 
Right: "Guidelines" labeled "Unconditional" with an always-on icon. Below, show the /triage 
skill file and the guidelines.md file side by side from Alex's project.

Speaker Notes:
- Transition naturally: Junie is working on its plan, so use the moment to dig 
  deeper into the /triage skill that was just executed.
- Frame the two configuration methods: conditional (Skills) and unconditional (Guidelines).
- Skills = conditional instructions. "When the user asks for this, do this." The 
  /triage skill is simply a prompt: when the user types /triage, pull Jira issues 
  ordered by priority and give a custom greeting.
- Guidelines = unconditional instructions, automatically appended to every request. 
  Alex's guidelines file has two rules: never recurse into node modules, and only 
  work in the FT Jira space. These are included every time, no matter what.
- Address the natural question: how do you decide which is which? Any guideline 
  could technically be repackaged as a skill — the boundary is blurry.
- General principle: prefer Skills when possible, because they minimize context 
  buffer usage which leads to better performance.
- Explain why the recurse rule stays in Guidelines despite this: if Junie recurses 
  into node modules even once, it tries to read tens of thousands of files and hangs 
  for several minutes. That happening even once is catastrophic for productivity, 
  so it stays in guidelines where it's always enforced.
- Tease next slide: scope of execution.

Example Script: "Let's leave Junie to work for a moment. While it's making its plan, I want to dig a little deeper into the skill I just executed. You can append custom instructions to your prompt in two ways with Junie — conditionally, and unconditionally. Conditional instructions are called Skills. When the user asks for this, do this. My /triage skill was very simply a prompt that said 'when the user types /triage, pull down all Jira issues and order them by priority, and give a custom greeting.' Unconditional instructions are called Guidelines, which are automatically appended to every request. My guidelines file right now only has two rules: never recurse into node modules, and only work in the FT space in Jira. These are appended to every request I send Junie, automatically. So how do you know what should be a Skill and what should be in Guidelines? After all, any guideline could technically be repackaged as a skill — which would accomplish functionally the same thing. In general, it's better to use Skills for what you can, because it minimizes context buffer usage, which leads to better performance. The reason I chose to keep the recurse rule in Guidelines is to ensure it never happens. If it does, Junie will try to read all of the tens of thousands of files inside of node modules and will hang for several minutes. That happening even once is catastrophic for productivity — so it stays in guidelines."

---

## Slide 12: LIVE DEMO: Executing the Fix [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE.

Speaker Notes:
- Review the Ask Mode plan.
- Swap to Auto Mode to execute the approved plan.
- Justify the mode switch: plan is approved, multiple files need modification — this is Auto Mode territory.
- Tie the transition directly to Alex's story: Junie just modified multiple files in a project with hundreds. Pose the question that leads into the RAG intermission using Alex's tech lead as a character.

Example Script: "Back in the IDE, Junie has given Alex a solid step-by-step plan. Alex reviews it, and it looks great. Now, referencing the flowchart: Alex has an approved plan that requires modifications across multiple files. This is exactly when Alex swaps to Auto Mode — the mode designed for executing large, multi-file changes. Alex simply tells Junie, 'Please implement this exact plan.' Now, while Junie works — Alex's tech lead is going to look at this and ask a very reasonable question: Junie just touched three files in a project with two hundred. How did it know which three?"

Demo Actions:
- Flip back to the IDE.
- Briefly show the Ask Mode step-by-step plan.
- Swap to Junie Auto Mode.
- Tell Junie: "Please implement this exact plan."
- Hit enter, and immediately transition to Slide 13.
- Fallback: Pre-recorded MP4 of the plan review and Auto Mode execution.

---

## Slide 13: UNDER THE HOOD: Semantic Search vs. Vector DB [INFO — INTERMISSION 2]

Visual: Diagram showing RAG architecture.

Speaker Notes:
- Frame the intermission as answering Alex's tech lead's question from the previous slide — keep the narrative thread alive.
- The problem: massive context windows degrade performance.
- The solution: RAG (Retrieval-Augmented Generation).
- Explain Semantic Search (what Junie uses for speed and simplicity).
- Explain Vector DB (chunking, embedding, indexing, storing). Used for massive third-party scale.
- Demonstrate understanding of limitations: semantic search can miss edge cases in very large monorepos where relevant code doesn't share obvious semantic similarity with the query. That is where a Vector DB becomes worth the overhead.

Example Script: "Here's the answer for Alex's tech lead. Even though LLM context windows have gotten enormous, there is a clear degradation in performance the more context you stuff into them. Dumping the entire codebase into the prompt doesn't work. To fix this, Junie uses RAG — Retrieval-Augmented Generation. It intelligently searches the project and appends only the exact code snippets it needs to the prompt. Now, there are two approaches to RAG. A Vector Database involves chunking your data, embedding it into vector representations, indexing it, and storing it — to ensure absolutely nothing is missed at a massive scale. However, for IDE performance and simplicity, Junie relies on fast Semantic Search — it understands the meaning of Alex's query and finds the most relevant code without the overhead of maintaining a full vector index. Now, to be transparent about the tradeoff: semantic search can miss edge cases in very large monorepos where the relevant code doesn't share obvious semantic similarity with the query. That's where a Vector DB becomes worth the overhead. If Alex's enterprise requires that scale — millions of documents, massive monorepos — third-party providers easily plug into this architecture. That's the flexibility of the platform."

---

## Slide 14: LIVE DEMO: Quick Actions & Code Refinement [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE.

Speaker Notes:
- Check diff. Code is written.
- Introduce Quick Actions — the right mode for small, targeted inline refinements.
- Start practical: generate docs for a new method.
- Introduce custom commands.
- Show the "Mock" custom Quick Action for a laugh.

Example Script: "Junie just finished the code. Let's look at the diff. Now, referencing the flowchart one more time: Alex doesn't need a full plan or a multi-file execution. He just wants a small, targeted inline refinement on a single method. This is Quick Actions territory. Alex highlights this new method, opens the Quick Menu, and clicks 'Generate Documentation.' Instantly, standard docstrings. But Alex isn't limited to the defaults. He can use custom commands to do literally anything. For example, as a joke, I created a custom Quick Action called 'Mock.' If Alex highlights the original code and runs it... Junie will lightly roast the developer who originally wrote this. (Show result, laugh.) Very funny, but in reality, Alex uses these custom actions to enforce standard formatting or tweak variables instantly — saving him from annoying his code reviewers later."

Demo Actions:
- Show the code diff.
- Highlight the new method, open the Quick Menu, click "Generate Documentation."
- Point out the custom command input bar.
- Highlight the original code, run the custom "Mock" action. Read the roast.
- Fallback: Pre-recorded GIF of the Quick Action menu and the "Mock" roast.

---

## Slide 15: The Admin Burden (Story) [INFO]

Visual: Split screen showing a happy coding developer vs. a frustrated developer doing paperwork.

Speaker Notes:
- The code is done. Now the paperwork begins.
- Alex is a great coder, but a terrible/reluctant writer.
- Transition: let's see how Junie helps Alex finish the day.
- Recovery note: if Slides 10-14 failed and golden run video was used, quietly checkout the FT-4-backup branch during this slide while talking.

Example Script: "Alex fixed the bug. But if you're a developer, you know the day isn't over. It's time for the part Alex dreads — where he stops coding and starts writing about the code he wrote. Alex is a brilliant engineer, but he isn't the most detailed technical writer, and he hates writing PR summaries. Let's see how Junie helps him automate the paperwork."

---

## Slide 16: LIVE DEMO: The Commit & Push [DEMO]

Visual: Blank or subtle background to focus attention on the live IDE / Browser.

Speaker Notes:
- Alex asks Junie to commit. It auto-triggers the commit-workflow.md skill.
- Explain the skill: branch matches Jira ticket for auto-linking.
- Pop open GitHub Actions to show Junie running the PR.
- Important: a subtle test error has been pre-seeded in the codebase. The CI pipeline will catch it. Do not mention this yet — let it surface naturally on Slide 18.
- Add one sentence about branch protection: in a real enterprise workflow, this would be gated behind branch protection rules and required reviews. Junie works within those guardrails, not around them.

Example Script: "Alex tells Junie, 'Commit these changes.' Junie automatically realizes it should run Alex's custom commit-workflow.md skill. Let's look at this skill file: it instructs Junie to create a new branch named after the active Jira ticket, so Alex's Jira integration will automatically link them. It commits, and it pushes. Of course, in a real enterprise workflow, Alex's team would gate this behind branch protection rules and required reviews — Junie works within those guardrails, not around them. Now, let's briefly open up GitHub. Over here in the Actions tab, you can actually see Junie spinning up headlessly to evaluate the PR, run tests, and write the summary. While that runs, let's talk about what's actually happening under the hood."

Demo Actions:
- Prompt Junie: "Commit these changes."
- Open and briefly show the commit-workflow.md skill file.
- [BROWSER] Open GitHub to the Actions tab to show the pipeline running.
- Fallback: Pre-recorded MP4 of the commit flow and GitHub Actions tab.

---

## Slide 17: UNDER THE HOOD: The CLI Engine [INFO — INTERMISSION 3]

Visual: Screenshot of GitHub logs showing CLI auth, alongside a terminal window.

Speaker Notes:
- Frame the intermission using a character: Alex's DevOps engineer, Sam, runs Jenkins — not GitHub Actions. Sam is going to push back.
- GitHub Junie is just a headless CLI runner.
- Show logs proving CLI install/auth.
- Open WSL terminal to prove it runs locally.
- Use cases: Jenkins, pre-commit hooks, Makefiles, GitLab.

Example Script: "Alex loves this. But his DevOps engineer — let's call her Sam — runs Jenkins, not GitHub Actions. Sam's going to say, 'Cool demo, but this doesn't work for us.' Here's what Alex shows Sam. What's running in GitHub right now isn't a proprietary GitHub plugin. If you look at these logs, it is simply a runner installing the Junie CLI headlessly and authenticating. To prove it, I'll open up my Junie terminal app right here in Windows WSL. Using this exact same CLI method, Sam could embed an AI agent into literally any custom workflow. We have it in GitHub and GitLab, but it drops just as easily into Jenkins, local pre-commit hooks, Bash scripts, or Makefiles. It's a CLI — it runs wherever a terminal runs."

Demo Actions:
- [BROWSER] Show the raw GitHub Action logs proving it's a CLI install.
- Open Windows Terminal (WSL) and run a quick junie --help or simple status command.

---

## Slide 18: LIVE DEMO: The PR Finale [DEMO]

Visual: Blank or subtle background to focus attention on the live PyCharm IDE.

Speaker Notes:
- Return to PyCharm. Open the Pull Requests tool window.
- Show the rich PR summary drafted by Junie.
- Reveal the test failure: the pipeline caught a subtle regression. This was pre-seeded before the demo. The audience has watched everything go smoothly — this is the moment of real-world tension.
- Show Junie's PR comment identifying and explaining the failure.
- Do NOT rerun the pipeline. The catch is the moment, not the fix. Acknowledge that in a real workflow, Alex would tell Junie to fix it and re-push, but the critical takeaway is that it was caught before it hit main.
- Then: merge and close the PR directly from the IDE (or explain that Alex would merge after the fix in a real workflow — choose based on what flows better live).
- Signpost: explain the final Jira automation, transition to the recap while it runs.

Example Script: "Let's jump back to Alex's workflow. Now, Alex could open the browser, but remember our goal today: Alex never leaves the IDE. PyCharm has native GitHub PR integration built right in. If Alex opens the Pull Requests tool window here, he can see the PR that Junie just drafted, complete with a detailed summary. But hold on — the pipeline caught something. A test failed. Let's look at what Junie flagged. (Show the PR comment.) See that? Alex didn't catch this. The code review didn't catch this. The CI agent caught a regression in a test that Alex didn't even touch today — a subtle issue that was already in the codebase before his fix. This is why you don't just use Junie for writing code — you use it as your last line of defense before merge. In a real workflow, Alex would tell Junie to fix the failing test and re-push. For today, the important thing is: it was caught before it ever hit main. Now, Alex approves the fix, merges, and closes this PR right from his editor. And for the grand finale: Alex has one last workflow configured. By closing this PR, Junie detects the linked Jira ticket he pulled this morning, leaves a resolution comment, and moves the ticket to 'Done.' Alex's day is officially over. While we wait for that final Jira automation to finish running in the background, let's talk about everything we've seen today."

Demo Actions:
- Switch back to PyCharm.
- Open the Pull Requests tool window.
- Show the generated summary and PR comment.
- Point out the test failure and Junie's explanation in the PR comment.
- React naturally to the failure — this is a strength, not an embarrassment.
- Merge and close the PR within the IDE UI (or verbally explain the next step if skipping the merge).
- Verbally explain the final Jira automation that triggers upon closing.
- Fallback: Pre-recorded MP4 of the PR with the test failure comment, merge, and Jira ticket transition.

---

## Slide 19: The Developer's AI Playbook [INFO]

Visual: The decision tree diagram (same as Slide 8's flowchart, now the centerpiece).

Speaker Notes:
- Summarize the entire journey.
- Recap the flowchart rules with explicit mode justifications.
- Deliver the context-switch payoff: call back to the challenge set in Slide 1. Name the number. Let the contrast land.
- Check back on the Jira ticket to prove the final automation worked. This is the "after" — the audience last saw the board on Slide 9 with the ticket in To Do.

Example Script: "You just watched Alex traverse an entire software development lifecycle — from triage to deployment — without ever leaving his IDE. When you go back to your desks, this playbook flowchart on the screen is your guide: If Alex is brainstorming with wide context spread across many files, he uses Junie Ask Mode — read-only, plan first. If Alex has an approved plan and needs to execute a massive multi-file change, he triggers Auto Mode. If Alex just needs a fast inline refactor — or a joke about his coworker's code — he uses Quick Actions. And if Alex needs a quick web search or a simple question answered without codebase context, he opens Chat Mode. Now — remember the challenge from the start? If you were counting, Alex would have context-switched at least eight times today across six different tools. He switched zero. Take a screenshot of this tree — this is exactly how you eliminate context-switching. Speaking of which, let's take one last peek at our Jira integration. (Show the board.) There it is. Done."

Demo Actions:
- Leave the diagram on screen while talking.
- [BROWSER] Open the Jira board. Show the ticket in the Done column. Let the before/after land.

---

## Slide 20: The Onboarding Checklist [INFO]

Visual: A live preview or screenshot of the interactive Seismic one-pager. Show the URL or QR code prominently.

Speaker Notes:
- This is the final differentiator moment. Reveal the onboarding checklist as a customer deliverable — not a slide, a real resource.
- Frame it as something Alex's team lead can use to roll this out across the org.
- This is the last thing the audience sees before Q&A. It reframes the conversation: they are no longer evaluating a candidate — they are talking to someone who already built them a deliverable.

Example Script: "One last thing. If Alex's team lead wants to roll this out across the entire org, I've built something for that. This is an interactive onboarding checklist that walks through everything we covered today — security configuration, agent setup, MCP toolbelt, the playbook, CI/CD integration — all in one place. It's already hosted and ready to share. Here's the link. Everything Alex learned today, his entire team can follow step by step."

---

## Slide 21: Getting Started & Plans [INFO]

Visual: A simple, clean slide showing pricing/licensing plans.

Speaker Notes:
- Reframe pricing inside the Alex narrative.
- Keep this strictly under 30 seconds. Do not linger.

Example Script: "Alex is sold. He walks over to his team lead and says, 'I need this for the whole team.' The team lead asks the inevitable question: 'What does it cost?' Here's exactly what Alex sends them. (Briefly walk through the plans on screen.) That's it — straightforward, no surprises."

---

## Slide 22: Q&A [INFO]

Visual: "Questions?" text alongside a QR code linking to the Seismic onboarding checklist and documentation.

Speaker Notes:
- Open the floor to specific team workflows and processes.
- End with a confident, warm close.

Example Script: "I'd love to hear about your specific team workflows and see how we can map Junie to your exact processes. What questions do you have?"