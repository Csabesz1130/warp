# TwinForge — 90-Day Execution Plan v1.0

*Solo technical founder, three tracks running in parallel: TECHNICAL (build the demo and the substrate), GTM (build the pilot pipeline), FUNDRAISING (build the round). Each track has weekly deliverables. Cross-dependencies are flagged. End state at day 90: live demo, 3 pilot conversations advanced, pitch deck closed against 5+ first meetings, $3–5M seed in serious diligence with at least one term sheet expected by day 120.*

---

## Strategic stance

**The single most failure-prone thing for a solo technical founder is over-investing on the technical track and under-investing on the other two.** Every week of this plan budgets time across all three. If you blow your time budget, the rule is: GTM > Fundraising > Technical. The technical track is what you're best at and most enjoy, which is exactly why it's the one that runs over.

**Time budget per week (60-hour week assumption):**
- Technical: 30 hours (50%)
- GTM: 18 hours (30%)
- Fundraising: 12 hours (20%)

If you're working 80h/week, scale up. If 40h, scale down — but do not change the *ratios*.

---

## Day 0 prep (this week, before the 90 starts)

Three things you must do before week 1 even starts. They unlock everything else.

1. **Lock the brand and the URL.** TwinForge.ai or twinforge.io if available. One-page landing site with a "request a demo" form. Mailchimp or HubSpot starter behind it. ~$500, 4 hours.
2. **File a defensive provisional patent** on (a) trace-grounded JEPA for physical systems and (b) hyperbolic equivariant encoder for hierarchical state spaces. Use a flat-fee patent attorney (LegalZoom-grade, $1500–3000). 2–3 hours of your time. This protects your moat slide.
3. **Write the 1-page teaser.** Pulled from slides 1, 2, 4, 6, 11 of the pitch deck. PDF, 1 page, branded. This is what goes in cold-outreach emails.

If any of these three are not done, stop reading and do them first. Everything else assumes them.

---

## Weeks 1–4 — Foundation & Demo

### Goals at end of week 4
- ✅ Live TwinForge demo running on a public building dataset (LBNL FLEXLAB, Pecan Street, OpenEI, or synthetic)
- ✅ Demo has been screen-recorded; recording is on the landing site
- ✅ 30 cold-outreach emails sent to property managers, REIT asset managers, FM-group decision-makers
- ✅ 5 first-meeting conversations scheduled or completed
- ✅ Pitch deck v1.0 reviewed by 3 outside readers (one founder, one investor, one domain expert)
- ✅ Top-25 target investor list built and prioritized

### Week 1 — Demo backbone

**TECHNICAL (30h):**
- Day 1–2: Pick the public dataset. Recommendation: **LBNL Building 59** (high-quality, ~3 years of HVAC + sensor data, public). Backup: Pecan Street commercial subset. Fallback: synthetic via OpenStudio + EnergyPlus.
- Day 3–4: Strip the dataset to a clean training format: timestamped (sensor reading, control input, weather) tuples, 5–15 minute resolution.
- Day 5: Stand up a tiny TwinForge twin — at this scale, a 50-state thermal RC network calibrated by gradient descent is fine. The REASONER-JEPA-NEXT physics substrate plugs in later. The demo doesn't need the 1B model to be impressive; it needs the 24-hour-fit-then-optimize loop to be visible.

**GTM (18h):**
- Build the target list of **75 potential first customers**: 25 office REITs/operators, 25 industrial / data-center facility managers, 25 university / hospital / municipal facility teams. LinkedIn Sales Navigator + a paid Apollo/Clearbit seat ($150). Pull names of FM directors, sustainability VPs, asset managers.
- Draft three cold-outreach templates (one per buyer segment). Total ~150 words each. Subject line is the key — test with "[Building name] HVAC: 18% reduction without a retrofit" or "[Regulation] compliance — our pilot has openings for Q[X]".
- Send the first 10 emails Friday. Track opens.

**FUNDRAISING (12h):**
- Pitch deck v1.0 (use the template in PITCH_DECK.md as starting point). Don't iterate beyond v1.0 yet — get it out for review.
- Build investor list: 60 funds. Prioritize **(a) climate-tech generalists** (Energy Impact Partners, Lowercarbon, Clean Energy Ventures, Generation Investment, Galvanize), **(b) vertical-SaaS funds** (Bessemer, Bond, Insight, OMERS Ventures), **(c) AI funds with vertical thesis** (Conviction, Costanoa, Greylock for B2B-AI partners). Filter by check-size match: $500K–$3M lead checks.
- Identify warm intros for the top 25. List who knows whom. The first 10 meetings should be all warm-intro, no cold.

### Week 2 — Demo polish + outreach acceleration

**TECHNICAL (30h):**
- Day 1–2: Build the optimization loop. Given a fitted twin, generate setpoint schedules that minimize predicted energy subject to comfort constraints (zone temps within ±1°C of setpoint band, ventilation at code minimum). MPC over a 24-hour horizon, re-planned every 15 min in the demo.
- Day 3: Build the dashboard. React + Recharts. Three views: (a) live twin state, (b) energy savings vs baseline curve, (c) operator-approval queue. Hosted on Vercel free tier or a $5/mo Fly.io instance.
- Day 4: Screen-record a 5-minute demo. Voice-over: 30s problem statement, 2 min twin fit, 2 min optimization recommendation, 30s savings summary.
- Day 5: Upload to Loom or YouTube unlisted. Drop the URL into the landing site and the cold-email signature.

**GTM (18h):**
- Send 30 cold-outreach emails this week (split across the three buyer segments).
- Schedule any responders for 30-minute discovery calls. Format: 5 min pitch, 15 min on their building portfolio + pain points, 10 min Q&A.
- Track every conversation in a CRM (Attio, Streak, or even a Notion table). Fields: contact, company, building portfolio size, regulatory exposure (LL97/BERDO/etc.), buying authority, next step.

**FUNDRAISING (12h):**
- Pitch deck v1.0 → 3 outside readers. Ask for: "what's confusing? what's not credible? what would you cut?" Do not ask "is this good?" — that's the wrong question.
- Iterate to v1.1 based on reads. Tightest single bottleneck: slide 3 (competitive positioning) almost always needs work.

### Week 3 — First conversations land

**TECHNICAL (30h):**
- Day 1–2: Add a "compliance reporting" view to the dashboard. Mock LL97 emissions calculation, mock BERDO letter-grade, mock EPBD energy class. This is the slide-7 stickiness story made concrete.
- Day 3–4: Build a 14-day forecast view. The twin predicts the next 2 weeks of energy at current vs optimized setpoints. This is the "$X annual savings" number the customer sees.
- Day 5: Buffer day. Use it to fix whatever the demo viewers (your investors, your customer prospects) called out as confusing.

**GTM (18h):**
- 30 more cold emails. Total at week 3 end: 60 emails sent.
- First 3–5 discovery calls happen this week. After each call, write a 3-line summary: "company X has Y buildings facing Z regulation, decision-maker is W, next step is V." Keep the discipline.
- Ask every call ending positively for **one warm referral** to a peer FM director. This is how you build pipeline 2× faster than cold.

**FUNDRAISING (12h):**
- Send first 5 cold investor emails to the top of your warm-intro-impossible list. Subject: "TwinForge — buildings, REASONER-JEPA-NEXT, [their portfolio company they'd want to see this against]."
- Reach out to 5 founders in your network whose investors might be relevant. Ask for double-opt-in intros. Target: 3 confirmed warm intros by end of week.

### Week 4 — Reality check

**TECHNICAL (30h):**
- Day 1–3: Wire REASONER-JEPA-NEXT (S100M Stage 1) into the demo as the *physics encoder*. The twin's latent state is now a learned embedding, not a hand-built RC network. This is the moment the substrate slide stops being aspirational and becomes real. Reference: the data plan's Week 3 milestone (S100M Stage 1+2 run) lands exactly here.
- Day 4: Re-record the demo with the substrate-powered twin. The savings curve should be visibly tighter (smaller error bars, better optimization).
- Day 5: Buffer.

**GTM (18h):**
- 30 more emails (total 90). 5–8 conversations completed by end of week 4.
- First in-person or extended-call meeting with a serious prospect. Format: 60 minutes, demo, two-page proposal of pilot scope.
- **Stretch goal:** first verbal "we'd consider a pilot" by end of week 4. If not, the messaging needs refinement. Recheck the top-of-funnel email subject lines.

**FUNDRAISING (12h):**
- 5–8 investor first meetings scheduled by end of week 4 (warm-intro pipeline + the cold ones that responded).
- After each investor meeting, write a debrief: what resonated, what objected, what they asked for in follow-up. This is the data that makes the deck v2.0 better than v1.0.
- **Day 28 review:** spend 90 minutes alone, no Slack, no email. Re-read this plan. What's behind? What's ahead? Reallocate the next 4 weeks accordingly.

---

## Weeks 5–8 — Pipeline & Substrate

### Goals at end of week 8
- ✅ S100M REASONER-JEPA-NEXT clears the falsifiability gate (per data plan Section 1.5)
- ✅ Demo upgraded to use Stage 1+2+3 ablation models
- ✅ 1 paid POC signed OR 3 paid-POC verbal commits (~$10–25K each, 60-day scope)
- ✅ 10–15 investor first meetings done; 3+ in second-meeting territory
- ✅ Pitch deck v2.0 incorporates investor feedback; demo updated

### Week 5 — Substrate cleared

**TECHNICAL (30h):**
- Run the S100M Stage 1 + Stage 2 ablation per the data plan. ~$460 cloud compute, ~24 hours wall.
- Falsifiability check: AIME 2024 hybrid eval ≥+3pp over raw baseline; trace prediction loss decreasing; equivalence-pair separation ≥3×. **If any gate fails, debug architecture before proceeding.** (Most likely failure: encoder collapse — apply SIGReg, increase weight, recheck.)
- If clear: proceed to Stage 3 ablation. Write the production rollout generator (`scripts/generate_rollouts.py` per the v0.2.0 ship note, ~600 LoC).

**GTM (18h):**
- 30 emails. Total at week 5 end: 120.
- Convert at least 2 of the 5–8 prior conversations into a pilot proposal. Pilot scope: **60 days, single building, $15K–25K paid POC, mutual NDA, success criteria spelled out** (e.g. >5% verifiable HVAC reduction = success, both parties move to annual contract).
- Building data prep: ask each engaged customer for 30 days of historical BMS data under NDA. Even if they don't sign, the data starts your real-customer corpus.

**FUNDRAISING (12h):**
- 5 more first meetings. By end of week 5, you've had 10–13 total.
- Send pitch deck + demo URL after every first meeting within 24 hours.
- Decline pre-emptive term-sheet conversations until end of week 8 — you'll get better terms with a stronger pipeline. The exception: if a top-tier fund (Sequoia, USV, a16z, Founders Fund, Index, Lux, Khosla) wants to lead, take the meeting and entertain the offer.

### Week 6 — Pipeline pressure-test

**TECHNICAL (30h):**
- Stage 3 DAPO RL ablation. Per data plan Section 3 — ~$60 compute. The actual rollout generator is what takes this week.
- Day 4–5: Wire the ablation outputs into the demo. The customer-facing dashboard should now reflect the latest model's predictions and confidence intervals.

**GTM (18h):**
- 30 emails. Total at week 6 end: 150. Conversion rate to first-meeting around 4–6% is healthy; if you're below 2%, the email is the problem.
- Customer #1 (the pilot lead) does a deeper integration call. Walk through their BMS topology, identify the 1–3 buildings best for the POC.
- Begin BACnet/IP integration prep: stand up a sandbox BACnet stack (open-source, BACnet4J or BACpypes), validate read-only points on a public building dataset.

**FUNDRAISING (12h):**
- 5 more first meetings. Cumulative: 15–18.
- Identify the **3–5 funds most likely to lead** based on responses so far. Begin the second-meeting / partner-meeting cadence with them.
- Ask each likely lead: "what would you need to see in 60 days to write?" Their answer is your week-7-to-week-12 roadmap.

### Week 7 — First pilot signed (target)

**TECHNICAL (30h):**
- Day 1–2: Production deploy infrastructure. Modal or Lambda Labs for inference; Postgres + S3 for customer data; Datadog for monitoring. Estimate: $50–200/mo per deployed building.
- Day 3–5: Customer #1 BACnet integration. Read-only points: zone temps, setpoints, supply air temp, AHU airflow, chilled/hot water valve positions, electric meter pulses. ~50–200 points typical.

**GTM (18h):**
- **Pilot #1 signed by end of this week.** $15–25K, 60-day scope, single building. Even if everything else slips, this is the milestone that changes the fundraising story.
- 20 more emails this week (total 170). Slowing email volume slightly to focus on the live conversations.
- Begin the customer-success workflow: weekly check-in cadence with the pilot customer; send week-1 progress report Friday.

**FUNDRAISING (12h):**
- Update deck to v2.0 with: "first paid pilot signed [name under NDA, sector + building size disclosed], deployment in progress."
- Send v2.0 to all the funds in second-meeting cadence. The pilot is the proof point that re-opens stalled conversations.
- Partner-meeting target: 1–2 of them this week.

### Week 8 — Substrate + pipeline + deck = round forming

**TECHNICAL (30h):**
- Day 1–3: Pilot #1 twin fit and shadow-mode deployment. The first time TwinForge runs on a real customer's data. **This is the riskiest day of the 90.** Allocate buffer.
- Day 4–5: Iterate on whatever broke. (Something will. The demo data has been pristine; real BMS data has gaps, drift, miscalibrated sensors. Plan for it.)

**GTM (18h):**
- Pilot #1 demo running. Pilot #2 (and ideally #3) verbal commits in hand.
- 20 more emails (total 190). The cold-outreach top of funnel is now ~5% of your time vs 15% in week 1; the conversations you have are doing the work.

**FUNDRAISING (12h):**
- **Day 56 review.** What's the round look like? You should have:
  - 18–25 investor first meetings done.
  - 4–6 in second-meeting / partner-meeting cadence.
  - 1–2 verbal "we want to lead" or "we want to participate" signals.
- If yes → tighten to the 5 most-likely funds, push for term sheets at week 12.
- If no → the deck or the demo is the bottleneck. Revisit with brutal honesty.

---

## Weeks 9–12 — Term Sheet & First Verified Savings

### Goals at end of week 12
- ✅ Pilot #1: 30 days of shadow-mode data, first verified savings number (target ≥10% projected, doesn't need to be locked in yet)
- ✅ Pilots #2 and #3 signed and starting integration
- ✅ At least 1 term sheet in hand, ideally 2–3 in competition
- ✅ Round closing within next 30–60 days

### Week 9 — Pilot #1 evidence

**TECHNICAL (30h):**
- Pilot #1 has been in shadow mode for 1–2 weeks. Generate the first interim report: predicted vs actual energy, savings projection, comfort-violation count, recommended setpoint changes.
- Customer review meeting. They approve some changes; you make them.
- Begin pilot #2 onboarding (BACnet integration, data pull).

**GTM (18h):**
- 15 emails this week (total 205). Top of funnel now mostly inbound from referrals + warm-intro chains.
- Pilot #2 signed; #3 in active negotiation.
- First **case-study draft** for pilot #1 — anonymized, used in investor diligence.

**FUNDRAISING (12h):**
- 3 partner meetings this week. Bring pilot #1 interim numbers.
- Begin prepping the diligence room: financial model, customer references, IP/patent status, technical deep-dive.

### Week 10 — Diligence acceleration

**TECHNICAL (30h):**
- Pilot #1 closes shadow mode; first **closed-loop** setpoint changes go live (with operator approval per change). Tight monitoring; 3-day rollback plan in case of comfort complaints.
- Pilot #2 in shadow mode.
- S1B compute commit decision: do you spin up the larger model or wait? Data plan says wait for ablation gate to clear. By now you have the answer.

**GTM (18h):**
- Pilot #1 customer becomes the first reference call. With their permission, set up 2 reference calls for serious investors who ask.
- Pilot #3 signed.

**FUNDRAISING (12h):**
- **First term sheet expected this week.** If not, push the most-engaged fund to commit by week 11 with: "we have 3 funds in partner meetings; we'd like to give you priority but need a decision."
- Begin pre-negotiating round structure (lead $1.5–2.5M, 5–10 strategic angels at $25–100K each, 1–2 follower funds).

### Week 11 — Term sheet competition

**TECHNICAL (30h):**
- Pilot #1: first verified-savings number (10–18% range likely; the exact number depends on the building, season, baseline period).
- Pilots #2 and #3 in shadow mode.
- Hire #1 (ML engineer): begin interviewing. Ideal: someone who's deployed ML in production at a vertical-AI startup.

**GTM (18h):**
- Public-facing case study from pilot #1 ready to launch (with customer permission). LinkedIn announcement, blog post on the landing site, send to all in-flight investor conversations.
- Reference-call infrastructure: 2 customers willing to talk to investors.

**FUNDRAISING (12h):**
- Multiple term sheets ideally in hand. Negotiate. Best terms come from competition.
- Set the close date for the round: target week 14–16.

### Week 12 — Close the round (or close the gap)

**TECHNICAL (30h):**
- Pilot #1: second verified savings reading. Trend line showing.
- Hire #1 close. Hire #2 (BMS engineer) interviewing.

**GTM (18h):**
- Pipeline at week 12 should look like: **3 paid pilots live, 5–10 in active conversation, $40–75K of POC revenue or commitments.** This is what week 13–24 will turn into 10 paying customers.

**FUNDRAISING (12h):**
- **Day 84 milestone:** lead investor selected, term sheet signed.
- Day 84–90: legal docs, diligence final, signature target.
- **Day 90 close target:** $3–5M seed wired.

---

## Tracking — what to instrument from day 1

A weekly metrics sheet you keep yourself honest with. Every Friday, fill in.

| Metric | W1 | W4 | W8 | W12 | Goal at W12 |
|---|---|---|---|---|---|
| Cold emails sent (cumulative) | 10 | 90 | 190 | 220 | — |
| First meetings (customers) | 0 | 5 | 12 | 20 | — |
| Pilots signed | 0 | 0 | 1 | 3 | **3** |
| POC revenue committed ($) | 0 | 0 | $20K | $60K | **$50K+** |
| Investor first meetings | 0 | 5 | 18 | 28 | — |
| Investor partner meetings | 0 | 0 | 4 | 8 | — |
| Term sheets in hand | 0 | 0 | 0 | 1–3 | **1+** |
| S100M ablation gate cleared (Y/N) | N | N | Y | Y | **Y** |
| Pilot #1 verified savings (%) | — | — | — | 10–18% | **>5%** |

If at any week-end review (W4, W8, W12) the numbers are off pace, the rule is: GTM-track problems are existential, fix this week. Technical-track problems are usually fixable within the next sprint. Fundraising-track problems are usually downstream of GTM problems — fix the GTM, the round catches up.

---

## What NOT to do in these 90 days

- **Don't build the whole REASONER-JEPA-NEXT 1B model.** The data plan correctly says wait for S100M to clear. The pitch is strong with S100M + ablation; the 1B is a 6–12 month follow-up the seed funds.
- **Don't over-customize for pilot #1.** Build for a clean BACnet/IP integration; resist all "but our building has this weird X" requests in the first 90 days.
- **Don't chase brand-name pilots.** Brookfield and Boston Properties have 12-month buy cycles. A medium-portfolio operator (50–500 buildings, single decision-maker) closes in 60–90 days. Chase those.
- **Don't pitch "we're building AGI"** even when the substrate is exciting. The pitch is *energy savings with proof*. The substrate is the moat slide.
- **Don't hire before week 8.** A bad hire at week 4 costs you 4 weeks of management time you don't have. Wait until pilots are landing and money is incoming.
- **Don't take a non-lead investor's term sheet first.** Weak signal; closes the round at lower terms; lead-quality matters more than speed in seed rounds.

---

## What to do if a pilot lands earlier than week 7

If you sign pilot #1 in week 3 or 4 (it happens — sometimes warm intros are faster than the plan), then:
- Compress the technical track: delay S100M ablation by 2 weeks; prioritize the live customer integration.
- Accelerate fundraising: the pilot proves the wedge faster than expected, term sheets come at week 6–8 instead of 10–12.
- Round size goes up: from $3–5M to $5–8M, post-money from $15–25M to $30–50M.

The plan adapts; the milestones don't change, the dates compress.

## What to do if no pilot by week 8

If week 8 ends with zero pilots signed:
- Stop fundraising for 2 weeks. Investor conversations get harder, not easier, with stale "still-no-pilot" updates. Pause and regroup.
- Diagnose: is it the **product** (the demo is unconvincing), the **price** ($25K is too high or too low), the **buyer** (you're talking to wrong title), or the **message** (the email doesn't land)? Test all four in parallel.
- Free-pilot offer to one warm prospect: "we'll deploy for free for 60 days, you give us BMS access and a reference call if it works." This is an emergency move; don't lead with it.
- Re-target if needed: data centers (faster cycles, larger ACV), university campuses (slower but predictable), hospitals (regulated but high-pain).

---

## Day 90 outcomes — three scenarios

**Strong case:** 3 pilots live, $60K+ POC revenue, 2–3 term sheets, $5M seed closing at $25M post. → Move to scaling plan: 25 customers in next 12 months, S1B model in compute, Series A target Q[X+18].

**Median case:** 1–2 pilots live, $25–40K POC revenue, 1 term sheet, $3–4M seed closing at $15–20M post. → Fine. Scale to 10 customers, prove the wedge, raise A on traction.

**Weak case:** 0 pilots, deep investor conversations but no term sheet. → Honest reset. Either the product needs more substance (4–8 more weeks of technical) or the market needs more validation (4–8 more weeks of GTM). Choose one, do not do both. Bridge $500K from angels if needed.

In every scenario, the substrate (REASONER-JEPA-NEXT) is the long moat. The 90 days are about proving the wedge, not the substrate.

---

*v1.0 — TwinForge 90-day execution plan. Update weekly with reality.*


# TwinForge — Pitch Deck v1.0

*Format: 12 slides, ~1 idea per slide, talk-track in italics. Slide titles are the pitch the audience remembers; bullets are the proof points the founder defends. Inline notes mark where the deck upgrades when pilots/LOIs land.*

---

## Slide 1 — Title

# TwinForge
### Physics-grounded digital twins that cut commercial-building HVAC energy 15–25% — in software, in 24 hours, with no hardware swap.

*Csaba [last name] — Founder & CEO*
*[Date] · Series Seed*

> **Talk track (~30s):** "Buildings waste 30–40% of their energy on heating, cooling, and ventilation. The fix isn't new equipment — it's continuously fitting the building's controls to how it actually behaves. We do that with physics-grounded digital twins. One twin per building, fit to live sensor data in 24 hours, running continuous optimization. 15–25% HVAC reduction, 18-month payback. We're raising [$3–5M] to deploy across 25 buildings in the next 18 months."

---

## Slide 2 — The problem

## Commercial buildings burn $200B/yr in wasted HVAC energy. Regulation just made it a fineable offense.

- Commercial buildings consume **40% of US energy**; HVAC is **40–50% of that**.
- 30–40% of HVAC energy is **structural waste** — wrong setpoints, conflicting control loops, drift from commissioning, unused zones.
- Building Performance Standards (NYC LL97, Boston BERDO, Denver, Boulder, Washington State, EU EPBD recast 2024) make this a **regulatory deadline, not a sustainability nice-to-have**.
- NYC LL97 fines start 2024–2030: **$268/ton CO₂ over budget**. A 500K sq ft non-compliant office: **$1–2M/yr in fines** by 2030.
- Owners want a fix that doesn't require ripping out HVAC equipment they just paid for.

> **Talk track:** "This is no longer 'should we save energy.' It's 'how do we avoid seven-figure fines without a $20M retrofit.' That's the buyer's question. We answer it."

---

## Slide 3 — Why nobody has solved it yet

## Existing tools optimize one valve. We optimize the whole building's physics.

| Approach | What they do | Why it's not enough |
|---|---|---|
| **BMS / BACnet vendors** (Siemens, Honeywell, JCI) | Rule-based control, manual tuning | Drifts within months; no learning |
| **Analytics dashboards** (Cylica, BuildingIQ legacy) | Show waste; don't fix it | Insight without action |
| **First-gen AI HVAC** (BrainBox, PassiveLogic, Phaidra) | Reinforcement learning per-zone | Per-zone models miss whole-building dynamics; $$$ to deploy |
| **CFD / Modelica twins** (IES, EnergyPlus consultants) | High-fidelity physics | Weeks-to-months to build; static; doesn't learn |

**The gap:** nobody combines *physics fidelity* with *automatic 24-hour fitting* with *continuous learning from live data*. That's the wedge.

> **Talk track:** "Each of these is a real product with real customers. None of them get to 15%+ savings consistently across a portfolio because they can't simultaneously be physics-correct, fast to deploy, and self-learning. Our architecture does all three."

---

## Slide 4 — The product

## One twin per building. 24 hours from BMS connection to first optimization. Continuous improvement after that.

**Day 0:** Read-only BMS / BACnet integration. Pull 14 days of sensor history.

**Day 1:** TwinForge fits a physics-grounded latent twin to that history. Conservation laws baked in: thermal balance, airflow continuity, equipment curves. The twin predicts setpoint → energy → comfort with calibrated uncertainty.

**Day 2–7:** Twin runs in shadow mode. Generates optimized control schedules. Operator reviews and approves.

**Week 2+:** Closed-loop optimization. The twin keeps re-fitting as the building changes (weather, occupancy, equipment drift). Monthly automated re-commissioning report.

**What the customer sees:** kWh dashboard, $-saved-vs-baseline, comfort-violations log, audit trail for compliance reporting.

> **Talk track:** "The deployment is software-only. We don't replace anything. We sit on top of the BMS the way Stripe sits on top of card networks — read access first, then progressively more authority as trust builds."

---

## Slide 5 — Why we win technically

## TwinForge is built on REASONER-JEPA-NEXT — our proprietary physics-grounded reasoning architecture that learns from execution traces, not just text.

The substrate (one slide, one paragraph, then move on):

- **Joint-embedding predictive architecture** (LeCun's JEPA family, our extension) — the model predicts behavior in semantic space, not pixel/token space. **5–10× more sample-efficient** than autoregressive models on physics tasks.
- **Trace-grounded** — trained on 200B+ tokens of executed code and physical-system traces. Most LLMs have never seen what their predictions actually *do*. Ours is trained on what happens next.
- **Hyperbolic encoder** — depth-aware geometric capacity for hierarchical systems. A building has zones inside floors inside the envelope; the math matches.
- **Energy-based verification** — every prediction has a calibrated confidence. Hallucinations get caught before they touch a setpoint.
- **Same substrate generalizes**: clinical signals (PhysioField), molecules (MolecularJEPA), urban systems (UrbanPulse). One platform, many wedges.

> **Talk track:** "I won't drag you through the architecture in this room. The takeaway: the same model that runs the building twin runs every other domain we're entering. The moat is the architecture and the trace data — both compounding monthly."

> **Note for technical audience:** swap this slide for the architecture diagram from the REASONER-JEPA-NEXT report. Most VCs don't need it; some do.

---

## Slide 6 — Traction

### *(Honest version, N=0 today)*

## Three building-portfolio pilots in active conversation. First deployment in Q[X]. Lighthouse customer commitment by month 6.

- **Pilot pipeline (named under NDA):**
  - Office portfolio operator, [N] buildings, [city]
  - Industrial / data-center facility, [city]
  - University campus / district heating system, [city]
- **Letters of intent / paid POCs:** [list any]
- **Founder access:** [any direct relationships with property managers, REITs, FM groups, ESCOs that materially shorten sales cycles]
- **Demo:** working twin running on a public dataset (LBNL FLEXLAB, Pecan Street, or a synthetic building corpus) showing the 24-hour fit and the optimization loop. *(See slide 12 for the demo URL.)*

> **Talk track:** "We're pre-pilot-revenue. What we have is a working demo on public data, three serious conversations, and a founder network that opens doors faster than cold outbound. The seed gets us to three signed pilots by month 6 and lighthouse revenue by month 12."

> **Edit-in-place when reality changes:**
> - **1+ pilot signed:** replace this slide with logos + ARR + savings %. The pitch tightens substantially.
> - **3+ paid pilots live:** the round shape changes from $3–5M seed to $5–10M seed-extension or A; renegotiate.

---

## Slide 7 — Business model

## Per-building SaaS. Land $15K, expand to $40K, multi-year. Software-only gross margin.

- **Pricing tier (commercial office):**
  - Starter (single building, 50–250K sq ft): **$15K/yr** — twin + optimization + reporting
  - Standard (250K–1M sq ft, BACnet integration): **$30K/yr**
  - Enterprise (portfolio, 1M+ sq ft, custom integrations, compliance reporting): **$75–150K/yr**
- **Land-and-expand:** typical customer enters Starter on one trophy building, expands to portfolio within 12 months once savings are proven.
- **Gross margin:** **80%+** at scale. Cost of goods is cloud + integration support; both scale sub-linearly.
- **CAC payback:** estimated **6–9 months** based on comparable SaaS-for-buildings (BrainBox, Phaidra, Cylica) — to validate during seed.
- **Net revenue retention:** target **130%+** at year 2 via portfolio expansion.

> **Talk track:** "This is a textbook vertical SaaS. The energy savings number is what gets us in the door. The compliance reporting is what makes it sticky."

---

## Slide 8 — Market

## $50B+ TAM, regulation-tailwinded, and the buyers have a deadline.

- **TAM:** Global commercial buildings AI/optimization market: **$8B in 2024 → $50B+ by 2030** (multiple analyst sources; IEA + ABI Research).
- **SAM (initial wedge):** US + EU office, retail, hospitality, industrial buildings >50K sq ft: **~600K buildings**, average $25K ACV = **$15B**.
- **SOM (5-year, realistic):** 0.5–1% capture in the wedge segment by year 5: **$75–150M ARR**.
- **Tailwinds (2024–2030):**
  - NYC LL97, Boston BERDO 2.0, Boulder Building Performance Ordinance, Denver, Washington State CETA, EU EPBD recast (2024), CSRD reporting.
  - Net-zero commitments from REITs (Brookfield, Boston Properties, Blackstone, Tishman Speyer) — all need a tool to actually hit them.
- **Comparable exits:** BrainBox AI acquired by Trane (~$700M+ implied), PassiveLogic Series B at ~$800M post-money (2024).

> **Talk track:** "Generalist climate funds and B2B-SaaS funds both engage on this market. The reason the comparable exits exist is the regulation has a deadline — the buyer has to act, not just want to."

---

## Slide 9 — Why now

## Three things converged in the last 24 months that make TwinForge possible today.

1. **Regulation has teeth.** LL97 fines hit 2024; EU EPBD compliance deadline 2030. Buyers can no longer wait.
2. **BACnet/REST APIs are universal.** 90%+ of commercial buildings >100K sq ft now have IP-addressable BMS. Integration is days, not months.
3. **Foundation-model architectures finally do physics.** JEPA-family models (V-JEPA 2, DINO-WM, our REASONER-JEPA-NEXT) bring sample efficiency that lets us fit a building twin in 24 hours instead of weeks. Pre-2024, this product was technically infeasible at our price point.

> **Talk track:** "The same product idea was tried in 2017 and 2020. It failed both times because either the regulation wasn't biting or the AI wasn't good enough. Both gates opened in the last 18 months."

---

## Slide 10 — Team

## Founder builds across the full stack. Hiring plan funds first 5 hires from the seed.

- **Csaba [last name], Founder/CEO**
  - [1-line bio: prior wins, technical depth, what makes you the right founder]
  - Built REASONER-JEPA-NEXT (the substrate); architectural lead, full pipeline (data → SSL → RL → deployment)
  - Portfolio of related research: WorldForge, ForgeGraph, NEWTON.A1, TwinForge — proves multi-domain breadth
- **Hiring plan from seed (first 18 months):**
  - **Hire 1:** ML engineer — owns the building-twin fine-tune pipeline
  - **Hire 2:** BMS/controls engineer — owns BACnet integration + on-site customer success
  - **Hire 3:** Founding GTM — owns pilot pipeline + customer conversations
  - **Hire 4:** Full-stack engineer — owns the customer dashboard + reporting
  - **Hire 5:** Senior systems engineer — owns deployment + reliability

- **Advisors / introductions in pipeline:** [list 1–3 if real; otherwise "advisor pool TBD by close"]

> **Talk track:** "I'm a technical founder doing the unsexy thing — selling and deploying at the same time as building. The seed funds the team that lets me stop being the only person in three roles."

> **Edit-in-place:** if you have a co-founder, this slide changes substantially — show two faces, split responsibilities clearly. If you have an advisor with a big logo (former exec at JCI/Siemens, prominent VC, named ML researcher), name them.

---

## Slide 11 — The ask & use of funds

## Raising $3–5M seed. 18-month runway. Three concrete milestones.

| Use | Allocation | Outcome |
|---|---|---|
| **Engineering (5 hires + founder)** | ~$2.5M | Productionize TwinForge MVP; deploy across 10 buildings |
| **GTM** | ~$0.7M | Hire founding GTM; close 3 pilots → 10 paid customers |
| **Compute (cloud H100 + inference)** | ~$0.5M | Train REASONER-JEPA-NEXT 1B; deploy inference on a single H100 |
| **Compliance / regulatory** | ~$0.2M | Verified savings methodology audited (IPMVP / ASHRAE 14) |
| **Buffer + ops** | ~$0.6M | 6-month runway extension cushion |
| **Total** | **$4.5M** | |

**Milestones funded by this round:**
- Month 6: 3 paid pilots live, first verified savings reports.
- Month 12: 10 paying customers, $300K–500K ARR.
- Month 18: 25 customers, $1M+ ARR, Series A-ready metrics.

**Series A target:** $15–25M at $60–100M post, Q[X] 2027, on the dual narrative of TwinForge revenue + REASONER-JEPA-NEXT substrate expanding into clinical (PhysioField) and material discovery (MolecularJEPA).

> **Talk track:** "Eighteen months gets us to a clean A. The substrate compounds across domains, so the A isn't just bigger TwinForge — it's TwinForge revenue plus the next vertical lit up. That's how a $5M seed turns into a $1B platform."

---

## Slide 12 — Demo + close

## See it run.

**Live demo:** [URL] — TwinForge fitting a public building dataset (LBNL FLEXLAB) and producing optimization recommendations in real time.

**Architecture deep-dive (technical audience):** [URL to REASONER-JEPA-NEXT documentation / arXiv preprint when published]

**Sample pilot deployment report (anonymized):** [URL]

> **Talk track:** "I'd rather you see it than I tell you about it. Five-minute demo on the way out — it'll show you the 24-hour fit and the savings curve on a real building."

---

## Appendix slides (use selectively, per investor)

### A1 — Competitive positioning detail (vs BrainBox / Phaidra / PassiveLogic / IES)

| Dimension | TwinForge | BrainBox | Phaidra | PassiveLogic | EnergyPlus consultants |
|---|---|---|---|---|---|
| Time-to-deploy | **24h** | 2–4 weeks | 6–12 weeks | 4–8 weeks | 8–24 weeks |
| Whole-building physics | ✅ | partial (zone-RL) | ✅ (Modelica-derived) | ✅ (Quantum-twin) | ✅ |
| Continuous learning | ✅ | ✅ | partial | partial | ❌ |
| Cross-vertical platform | ✅ (REASONER-JEPA-NEXT) | ❌ HVAC-only | ❌ industrial | ❌ buildings-only | ❌ |
| Compliance reporting | ✅ (LL97, BERDO, EPBD) | ✅ HVAC | partial | partial | ✅ |
| Hardware-light | ✅ | ✅ | ✅ | partial (proprietary controller) | ✅ |

### A2 — Technical defensibility

- **REASONER-JEPA-NEXT: 200B+ token trace corpus** (proprietary).
- **Hyperbolic Lorentz embedding** + LeJEPA SIGReg + DAPO RL pipeline (described in our public technical posts; full implementation closed-source).
- **18-month head start** on competitors converging on similar architecture.
- **Cross-portfolio data flywheel:** every TwinForge deployment generates new physics traces that improve PhysioField, MolecularJEPA, UrbanPulse simultaneously.
- **Patent application filed on:** trace-grounded JEPA training for physical systems; hyperbolic equivariant encoder for hierarchical state spaces. *(File before pitch if not done.)*

### A3 — Verified-savings methodology

- IPMVP Option C (whole-facility, regression-based) baseline.
- ASHRAE Guideline 14 statistical confidence intervals.
- Third-party verification optional, included in Enterprise tier.
- Sample report attached in due-diligence package.

### A4 — Risks and mitigations

| Risk | Mitigation |
|---|---|
| Long enterprise sales cycle | Founding GTM hire + warm-intro-only outbound for first 12 mo |
| BMS integration complexity per building | Standardize on BACnet/IP first; expand to Modbus/proprietary later |
| Comfort complaint blowback | Shadow-mode default; operator approves every setpoint change for first 90 days |
| Savings claim verification | IPMVP-compliant baselines from day 1; third-party audit option |
| Competitor IP / patents | FTO opinion before scale; defensive filings on trace-grounded JEPA |
| Foundation-model commoditization | Substrate is the moat, not the wrapper; vertical depth + trace corpus protects |

### A5 — Long-term portfolio thesis

```
                    REASONER-JEPA-NEXT (substrate)
                              │
        ┌──────────────────┬──┴────────────────┬─────────────────┐
        │                  │                    │                 │
   TwinForge          PhysioField         MolecularJEPA       UrbanPulse
   (buildings)        (clinical signals)  (drug discovery)    (urban systems)
        │                  │                    │                 │
   Year 1–2           Year 2–4              Year 3–5           Year 4+
   $1–10M ARR         FDA-pathway          IP licenses        Smart-city deals
```

Each vertical reuses ~70% of the substrate and adds a domain-specific encoder + RL fine-tune. Each new vertical takes ~30% of the engineering effort of the first one. Compounding moat.

---

## Pitch logistics — what to send when

| Stage | Document |
|---|---|
| Cold outreach (email) | 1-page teaser: slides 1, 2, 4, 6, 11 only |
| First meeting (30 min) | Full deck, slides 1–12 |
| Partner meeting / second call | Full deck + appendices A1–A4 |
| Diligence | Architecture deep-dive (REASONER-JEPA-NEXT report), customer references, financial model, IP/patent status |

---

*v1.0 — TwinForge pitch deck. Iterate weekly as pilots progress.*
