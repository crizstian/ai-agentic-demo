Correo de Cliente BAC

Buenas tardes, equipo:
Me gustaría invitarlos a una sesión con el equipo de Harness para analizar cómo la evolución de la IA Agéntica (Agentic AI) está transformando el desarrollo de software y cuáles son las estrategias que Harness está impulsando para responder a los desafíos y oportunidades que este nuevo paradigma presenta para la seguridad de aplicaciones.
Considero que este espacio será una excelente oportunidad para intercambiar inquietudes, plantear preguntas y comprender mejor cómo podemos prepararnos para los cambios que ya están impactando el ecosistema de desarrollo.
Objetivos de la sesión:
Revisar la posición y evolución de Harness frente a la IA Agéntica.
Analizar los principales retos y oportunidades que la IA Agéntica plantea para el desarrollo seguro y la seguridad de aplicaciones.
Conocer la visión y estrategia futura de Harness en este ámbito.
Recopilar comentarios, dudas y expectativas del equipo.
Quedo atento a cualquier consulta o comentario.
Saludos,

----------------------
Internal Slack Message

Rahul Sood  [7:41 PM]
:fire: off the heels of Agent DLC, we've got another big one today: Harness is launching a set of capabilities we're calling Security at Machine Speed.

The same frontier models that are helping our customers ship faster are also helping attackers find and exploit vulnerabilities faster. Time-to-exploit is now measured in hours, while the vulnerabilities still take 55 days to fix. LLM-based scanners are also helping customers find 10x more vulnerabilities, but at a cost - Comcast found 44% of those critical/high findings were false positives, and only 36% were exploitable. The bottleneck for security teams has become validation and remediation.

The customers we talk to are struggling with 4 things :
:arrow_right: Latent vulnerabilities waiting to be found
:arrow_right: Operationalizing Mythos, Codex for PR scanning
:arrow_right: Remediating with speed and confidence of not breaking their pipelines
:arrow_right: Having safety of run time protection while code fixes are being deployed

Here's how we think about it: use LLM scanners for what they're best at - deep, periodic hunting scans for your most critical apps, pair that with AI SAST doing the accurate, deterministic work in every single pipeline run. Then follow that with an agentic workflow to keep the backlog from building. Finally, patch the perimeter while the real fix ships..

In Security Testing Agent:

:white_check_mark: AI SAST pairs deterministic analysis with an AI confidence layer, cutting false positives by 79% and catching what pure dataflow scanning can't, like IDOR.
:white_check_mark: LLM Scan Orchestration helps you run LLM scanners more efficiently, scanning up to 67% faster while saving up to 82% in token costs.
:white_check_mark: Triage Agent combines CVSS, EPSS, and reachability so your team fixes real risk, not everything with a CVE number.
:white_check_mark: Remediation Agent writes and validates the fix, then opens a human-reviewed PR. Developers stay in control of what merges.
:white_check_mark: Function-level reachability traces down to the specific vulnerable function, not just "is the package called" - so Triage and Remediation Agents work off a sharper signal.
:white_check_mark: Zero-Day Agent skips the queue entirely for newly disclosed zero-days - maps blast radius in seconds, gets a fix ready for review.
In Runtime Protection Agent:

:white_check_mark: Virtual patching shields production on our WAAP the moment a vulnerability is found in testing, so the perimeter is covered while the real fix ships.

All of this runs on the same platform that's already deploying your code and holding chain of custody on every artifact - so finding something faster only matters because fixing and deploying it are just as fast now too.

PG focus 
Sales use this launch to have 4 types of customer conversations to drive deals in Q3 and Q4.

Fix and deploy at machine speed Software Delivery Agent and Security Testing Agent
Use AI in scanning using Security Testing Agent
Accelerate response to zero day supply chain attacks using Security Testing Agent
Protect your APIs and AI with Harness Runtime Protection Agent


Thank you to everyone who built this and everyone who shaped it through customer conversations along the way - proud of the work that got us here.

Let’s go help our customers get Mythos ready.

Please help us get the word out - share with your network.

FOLLOW-UP to come! 

---------------------

Harness public blog post

Harness
/
Blog
/
Technical
August 19, 2026
Harness Announces Capabilities That Enable Security At Machine Speed
Table of Contents
Scan without the guesswork: AI SAST and LLM Scan Orchestration
AI SAST 
LLM Scan Orchestration 
From finding to fix: Triage Agent and Remediation Agent
Triage Agent 
Remediation Agent 
Function-level reachability 
Zero-days don't wait in line: Zero-Day Agent
Shielding production while the fix is in flight
Security at machine speed
Want to learn more?

Vulnerabilities used to move at human speed. A researcher found one, disclosed it, and defenders had days - sometimes weeks - to respond before it was weaponized in the wild.

That window is gone. According to the Edgescan 2026 Vulnerability Statistics Report, it still takes an average of 55 days to fix a vulnerability - but the Zero Day Clock shows attackers going from disclosure to first exploit in as little as 6 hours. And per the 2025 DORA Report, once a fix is written, it can still take more than a week to get from commit to production. Security teams are trying to close a gap measured in hours with a process measured in weeks.

Frontier models like Claude Mythos are pulling on both ends of that gap at once. On one side, they're giving attackers a faster way to find and chain vulnerabilities. On the other, they're giving defenders a faster way to find vulnerabilities too. Point an LLM scanner at a codebase and it will surface far more findings than traditional tools ever did. Project Glasswing partners saw roughly 10x more vulnerabilities surfaced during testing. That's a good thing only for visibility. But it creates an operationalization challenge. Without any normalization, deduplication, reachability or integration with developer workflow, it just creates more backlog for a remediation process that was already too slow. Comcast, a Project Glasswing participant, put a number on that gap in its own testing: 44% of critical- and high-severity findings turned out to be false positives.

Security has to move at machine speed now, end to end: scan without drowning in noise or cost, triage what's actually worth fixing, remediate it, get the fix into production before the window closes, and still protect the perimeter while the fix is fully deployed. That's what this launch is about.

Scan Without The Guesswork: AI SAST And LLM Scan Orchestration

Everything downstream starts with the scan, so that's where machine speed has to start too.

LLM-based scanners are genuinely good at finding things traditional static analysis misses, which is exactly why they've generated so much attention. But they're still probabilistic: point the same model at the same code twice and you can get different findings, different false positives, latency that can hold up pipelines, and a token bill that scales with every file you scan. That's a real cost, and it makes it unrealistic to scan continuously in CI/CD. 

That’s why Harness is embracing the hybrid approach - use LLMs for one-off hunting scans, and a deterministic SAST augmented by AI in the pipeline.


AI SAST improves accuracy and reduces noise with AI confidence scoring
AI SAST 

Harness pairs a high-recall dataflow engine with an AI confidence layer that classifies each finding as confirmed risk, potential risk, or contextually safe. It's deterministic where LLM scanning is probabilistic: same code, same result, every time, with a traceable path from input to sink. In our own benchmarking against the OWASP Java corpus, that confidence layer cut false positives by 79% (from 454 down to 95) and lifted precision from 74% to 93%, while preserving 91% recall - almost no loss of signal for a large gain in precision. It also extends into broken access control (IDOR), a class dataflow analysis alone can't see because there's no malformed input to pattern-match, only a missing authorization check: 71% recall at 99% precision across a 390-case corpus spanning Go, Java, and Python.

LLM Scan Orchestration 

For teams that want to run LLM-based scanners, Harness now orchestrates them natively inside the CI/CD pipeline, reducing token spend, increasing scan speed, and feeding results into the same triage and remediation workflow as everything else - instead of a separate spreadsheet living outside your pipeline.

Which should you choose? AI SAST reduced the triage queue by 21% in our benchmark (1,746 flagged cases down to 1,381 actionable ones) without giving up coverage, and without paying a per-scan LLM bill to get there. LLM scanners still have a place, and Harness will keep making them faster and cheaper to run. But when the choice is between a probabilistic result and a deterministic one at comparable or better accuracy, the deterministic one should usually win by default.


From Finding To Fix: Triage Agent And Remediation Agent

A scanner - any scanner - is only useful if what it finds actually gets fixed. And the steady output of SAST and SCA scanning has a particular shape: a high volume of findings that need to be sorted by real risk before anyone starts fixing, because most security teams already have more open findings than they can act on in a sprint, let alone a day. And most of that backlog isn't as urgent as it looks: in the same Project Glasswing testing, only 36% of critical-severity and 33% of high-severity findings were confirmed exploitable. Sorting through that backlog by hand, then writing and validating each fix one by one, is exactly the kind of toil that doesn't scale with the volume scanning produces, so Harness is introducing an agentic workflow that does.

Triage Agent 

Harness’s Triage Agent prioritizes what's actually exploitable, combining CVSS, EPSS, and reachability analysis to cut a sprawling SAST/SCA finding list down to a clean, actionable backlog - so your team works on real risk, not everything with a CVE number.


Triage Agent automatically prioritizes remediation on the vulnerabilities that matter most.
Remediation Agent 

Once a finding is prioritized, the Remediation Agent applies the fix and validates it in your pipeline to prevent breaking builds, then opens a human-reviewed pull request. Developers stay in charge of what merges; the agent just does the work of getting them a validated fix instead of a bare finding.


Function-Level Reachability 

Reachability analysis doesn't stop at "is this vulnerable package called." Harness now traces the call path down to the specific vulnerable function, so a dependency only gets flagged if that exact function is reachable in your code. Both agents work off that sharper signal: fewer false positives for Triage Agent, and a precise code path to close for Remediation Agent.

Because these agents run on top of Harness's existing pipeline governance (policy gates, approvals, chain of custody), a fix doesn't just get written faster, it gets safely into production faster too. That's the piece that's easy to overlook: a fix sitting in a pull request isn't protection. A fix that's deployed with an audit trail through the same governed pipeline you already trust - that's protection.

Zero-Days Don't Wait In Line: Zero-Day Agent

Everything above assumes there's time to scan, triage, and prioritize before anyone acts. A zero-day doesn't give you that time. The clock starts the moment it's disclosed, and most of that time doesn't get spent writing a fix - it gets spent figuring out if you're even affected and waiting for a fixed artifact to work its way back through build, test, and deploy.

A newly disclosed zero-day doesn't need to wait in a triage queue behind the rest of the backlog; it needs an immediate, end-to-end response. Zero-Day Agent runs that response itself: it continuously monitors for newly disclosed zero-day vulnerabilities, automatically identifies every affected artifact and pipeline across your environment, and takes it the rest of the way - applying and validating a fix, then opening a human-reviewed pull request. No separate triage step, no handoff to another agent. Blast radius mapping that used to take days happens in seconds, and a fix is ready for review shortly after.


Zero-Day Agent improves response to newly disclosed zero-day vulnerabilities
Shielding Production While The Fix Is In Flight

Even with agents compressing the fix cycle to hours, hours are still a window. Harness closes that window from the other direction with virtual patching: when API testing discovers a vulnerability, it can create a virtual patch and deploy it on our WAAP - no tickets or code changes required. Production is shielded within minutes of discovery, while the permanent fix is worked in code. When the fix ships, the virtual patch comes down.

That's the same principle running through this whole launch: don't wait for the slowest step in the chain to gate every other step. Contain the risk immediately, fix it in parallel, and let each part of the system move as fast as it's capable of moving.

Security At Machine Speed

None of this works as a single point tool. The value comes from AI SAST, LLM scan orchestration, Triage Agent, Remediation Agent, Zero-Day Agent, and virtual patching all sitting on the same platform - the same one that's already deploying your code, governing your pipelines, and holding chain of custody on every artifact. Finding a vulnerability faster only matters if fixing it and deploying it are just as fast.

The organizations that build this operating rhythm now, those that scan without noise, triage in minutes, ship a validated fix in hours, shield production the whole time, will be the ones still moving confidently when attackers have the same frontier models defenders do. The ones that don't will keep measuring their response time in weeks while the threat measures its head start in hours.


--------------------
Harness blog post

Harness GM Rahul Sood: Most 
Harness GM Rahul Sood: Most "AI Remediation" Claims Don't Actually Work. Here's What Does.

appsec devsecops aisecurity applicationsecurity

Tom Smithverified
Backer
Leader
●44 ●242 ●427
calendar_today
5 days
ago
•
schedule
4 min read

more_vert
Application security has operated on human timelines for as long as it's existed: a scanner flags something, a ticket gets filed, developers and security argue over priority, and a fix ships weeks or months later, if it ships at all. Rahul Sood, GM of Application Security at Harness, points to Log4j as the cautionary tale everyone in the industry already knows by heart. "It was not uncommon for companies to say it took us almost one year to get rid of it," he said. "Right now, that does not work when attackers have AI that can identify vulnerabilities in your code, even if you thought your code was safe."

Harness is launching a set of AI-driven application security capabilities this week aimed at collapsing that timeline. The stakes are concrete: attackers are now going from disclosure to first exploit in as little as six hours, while the average vulnerability still takes more than 50 days to fix. Sood breaks into three required shifts: defenders need to actually use AI to find weaknesses in their own code, the window between discovering a vulnerability and fixing it needs to compress from months to hours, and organizations need to accept that not every fix will land before an attacker finds a way in, which means building a containment strategy alongside the fix itself.

Scanning with frontier models is real, and also too slow to run daily

Sood doesn't dispute that frontier models can scan code effectively. The problem is cost and speed. He cited a bank going through Anthropic's Glasswing program that took three months to scan its entire codebase using an LLM — and Glasswing partners broadly have surfaced roughly 10 times more vulnerabilities using LLM-based scanning than traditional tools find, a wave of visibility that just becomes a bigger backlog without a faster way to act. "The cost is it takes a lot of tokens. The output is not deterministic, and it's not easy for you to go and triage these vulnerabilities," he said.

Harness's answer is two separate capabilities rather than one. The first, LLM Scan Orchestration, is a native integration between its CI/CD security tooling and LLM-based scanning, supporting both Claude and OpenAI's Codex, so findings get triaged, deduplicated, and normalized into a developer's existing workflow instead of arriving as an unstructured wall of output. The second, AI SAST, layers AI reasoning on top of traditional static analysis, aiming to catch what conventional scanners miss (Sood pointed to business logic attacks as an example) while using that reasoning to cut false positives and explain why a finding matters. From there, a Triage Agent automatically prioritizes what's actually exploitable so teams can focus on real risk, and a Remediation Agent writes and validates a fix for a prioritized finding, opening a pull request for a developer to review and approve.

A zero-day agent that maps blast radius across your entire environment

For open-source and third-party code specifically, Harness is launching an agent that tracks newly disclosed zero-days and maps them against a customer's actual environment: artifacts, pipelines, and repos. Sood argues this is where Harness's position gives it an edge most competitors can't match, since the platform already has visibility into what's in production and what's being built. Once the blast radius is identified, policies can block new builds that carry the vulnerability while triage and remediation catch up. Sood's claim is that this compresses zero-day response from weeks or months down to hours.

The differentiator he leans on hardest, though, isn't detection. It's remediation that's actually been checked. "We don't just validate that the security vulnerability is being fixed. We also validate that the fix will not break your pipeline," he said. Because Harness manages the pipeline itself, a proposed fix gets tested against the customer's own unit tests before it ships, not just checked against the vulnerability in isolation.

Closing the loop with production shielding

Even with a compressed timeline, not every fix lands before an attacker moves. Harness's answer is a virtual patch at the perimeter, deployed against a specific API to block the traffic pattern that would exploit a known vulnerability. Customers choose between two modes: monitoring, where the patch alerts a human to assess, or blocking, where the traffic is stopped automatically. Sood said the choice comes down to a customer's confidence level, the criticality of the API, and their overall risk appetite, rather than a one-size-fits-all default.

That same logic extends to how much autonomy the underlying agents get generally. Sood expects most customers to start with a human in the loop and move toward more autonomous workflows only as trust builds, and the platform supports the full range, from fully manual to fully autonomous, configurable per customer and even per class of fix.

What changes for the developer staring at a vulnerability list

For engineers used to a scanner dumping a long, mostly-noise list of findings, Sood said the real shift isn't just fewer false positives, it's clarity on what's actually reachable and exploitable versus theoretical. Combined with a recommended fix that's been validated against a team's own test suite, the goal is to give developers back the time currently lost triaging vulnerabilities that were never going to matter. "Development teams are being completely overwhelmed by the huge number of vulnerabilities being generated by scanners," Sood said, to the point where it crowds out shipping actual business-relevant code.

What to be skeptical of

Asked what's overhyped in this space even as he's building in it, Sood didn't hedge. "This entire claim that agents can do all this work for you," he said, pointing specifically at remediation. "Most of it doesn't really work." His advice for developers and architects evaluating any vendor's AI remediation claims, Harness included: test it yourself, and be skeptical of a fix recommendation generated without real understanding of your specific environment and test cases. A recommendation that isn't validated against your actual code is still just a guess wearing a more confident outfit.

---------------------

Harness youtube video tutorial


0:000 secondsEvery company is adopting AI coding assistance. Developers can now create code faster than ever, but that creates a new problem. Code velocity is
0:077 secondsincreasing while delivery, security, governance, and production readiness are still stuck in manual workflows. This demo shows how harness turns AI
0:1515 secondsgenerated code into safe, governed, productionready software delivery.
0:1919 secondsStarting directly from the developer IDE, we begin with a customer-f facing issue in an embanking application. The
0:2626 secondsinterface is visibly broken. We will fix it using AI agents and that needs a safe path to production.
0:3333 secondsLet's review the harness pipeline and the flow we'll go through. After the fix and the PR is created by cursor, harness will come in with the PR validation.
0:4141 secondsHere our first AI worker agent will ensure that it's a safe change. After that, harness STTO will orchestrate multiple security scanners prioritizing
0:4949 secondsand dduplicating vulnerabilities in real time. Here we use governance policies to trigger our security worker agent only in case of critical or high vulnerabilities fixing it automatically.
1:001 minuteNext step is change management that is native in harness for approvals and ticket updates. After the PR is merged, we start our deploy stage. Here harness
1:091 minute, 9 secondsbrings you safety by rollouting gradually the change with a native canary deployment. Continuous verification uses AI to validate your business transaction health using your
1:171 minute, 17 secondsobservability tools as source. We finish it with automatic AI based UI testing and a critical topic is roll back.
1:241 minute, 24 secondsHarness provides automatic rollbacks for deployment and quality issues. [music] In our example, the first deploy will fail because a bad manifest and then worker agent will fix it automatically.
1:331 minute, 33 secondsSo let's move to action and see what an agentic developer experience looks like with cursor and harness. Okay, I'm in my cursor IDE and from here I have a
1:411 minute, 41 secondsseamless experience without context switching. In the left you can see the harness extension where I can have visibility on pipeline status, build
1:481 minute, 48 secondsartifacts, security issues and access step logs. Harness extension is also integrated with cursor agent allowing you to use harness MCP to troubleshoot
1:571 minute, 57 secondsand take any action quickly while bringing context from the current execution. Okay, let's troubleshoot this pipeline failure. By the time I ask here
2:052 minutes, 5 secondsin the extension and click submit, cursor agent has all the context needed and pass it along to harness MCP. Now we can see cursor and harness MCP working
2:132 minutes, 13 secondsin a analysis. So let's wait a couple seconds to complete. The result includes detailed information about the pipeline execution including details on the vulnerabilities detected by STTO.
2:232 minutes, 23 secondsHowever, the root cause of the failure was a policy guardrail that prevented the pipeline to continue with critical vulnerabilities. Now let's get to the
2:302 minutes, 30 secondsapplication fix. So let's prompt cursor agent for a troubleshoot and fix.
2:362 minutes, 36 secondsNow cursor is working in the inner loop analyzing the codebase and before fixing it's going to create a ticket which will be picked up by harnessed later for
2:432 minutes, 43 secondsagentic updates governance and approvals and also slack notifications to keep the communication aligned across the delivery life cycle.
2:552 minutes, 55 secondsNow we have the root cause identified.
2:572 minutes, 57 secondsThe code is fixed by cursor agent. The pull request generated by cursor with the suggested changes triggers the harness PR validation pipeline we
3:053 minutes, 5 secondsexplored earlier. Here we can see that cursor started to monitor it automatically. So now let's use harness extension to have a graphical visualization and execution details.
3:143 minutes, 14 secondsHarness is cloning the codebase using cache intelligence to speed up builds.
3:193 minutes, 19 secondsAlso faster unit tests by selecting only the tests related to the code changed.
3:233 minutes, 23 secondsAnd now our harness AI worker agent is reviewing the PR details to generate a verdict. Now it's time for security
3:303 minutes, 30 secondsscanning. Harness STTO is orchestrating two different scanners. And we can see here that it became read due a policy violation. Let's click in the security
3:383 minutes, 38 secondstab and explore the details. [music] Here we can see that 16 new vulnerabilities were introduced in this PR where seven are high. Let's explore
3:453 minutes, 45 secondsthat directly in STTO. We are now in the harness console with a prioritized and dduplicated vulnerabilities list across
3:523 minutes, 52 secondsall scanners. Let's deep dive in one vulnerability. Here we have all the details about the vulnerability including AI remediation. From here we
3:593 minutes, 59 secondscan create a new PR with the fix. We are not doing this for now because we have a worker agent in place that will not only fix it but also update the ticket and
4:084 minutes, 8 secondsopen the PR. Let's explore it. This is the pipeline execution visualization. We can see our security remediator worker agent acting after a policy evaluation
4:164 minutes, 16 secondsfailure in the security scanner. Now it's time to review the changes, merge and deploy the application.
4:234 minutes, 23 secondsI'm now in my code repository and you can see that we have two new pull requests. Let's review this one that was created by cursor and validated by
4:314 minutes, 31 secondsharness worker agent. This is the PR review from harness. As you can see, it's a very detailed report that assess
4:384 minutes, 38 secondschanges, risks, review tests, and make follow-up questions to the developer ensuring that there is no risk to move it ahead.
4:474 minutes, 47 secondsAlso, this is the Jira ticket with whole change history.
4:514 minutes, 51 secondsLet's come back to the IDE and review the PR review execution after the security remediation. Here we can see that the pipeline passed successfully.
4:594 minutes, 59 secondsNo security agent this time as high vulnerabilities are gone. With that, I confidently merged both PRs and the deploy stage was triggered. Let's review
5:075 minutes, 7 secondsit. Coming back to harness console, we can see that the canary deployment has failed. [music] The rollback strategy was immediately activated, automatically
5:145 minutes, 14 secondsundoing the change and also starting an AI Kubernetes agent for a review and fix. The harness worker agent found the
5:215 minutes, 21 secondsmanifest issue and automatically created the new PR with the fix. The PR contains all the details including the failed pipeline reference, root cause, evidence
5:305 minutes, 30 secondswith logs and the resolution. This saves engineering time and increased quality.
5:345 minutes, 34 seconds[music] So everything is in place right now and we are ready to redeploy. Let's merge this PR and see that in harness again.
5:435 minutes, 43 secondsOkay, after the autofix, the deployment stage was executed successfully. As we discussed before, we are using continuous verification with data dog to detect any anomaly in metrics or logs.
5:535 minutes, 53 seconds[music] The data dog metrics are healthy, so harness went ahead and did the full rolling deploy.
6:026 minutes, 2 secondsFinally, to ensure that the application UI is healthy and fixed, Harness executes an AI based browser test automation where we can see the
6:106 minutes, 10 secondsmisaligned boxes fixed and the transfer flow working correctly. Harness turns AI velocity into production confidence, governing, securing, remediating, and
6:186 minutes, 18 secondsverifying every change from the IDE to production. Thanks for watching.