"""Objective-aware profiles for deterministic (demo mode) agent output.

A shared domain profile keeps Research, Planning and Communication aligned with
the user's actual objective. The profiles are only used when the LLM is absent
or fails; live LLM output is still prompted with the detected domain.
"""

from __future__ import annotations

DOMAIN_KEYWORDS = {
    "software_deployment": [
        "deploy",
        "deployment",
        "release to production",
        "rollout",
        "ci/cd",
        "cicd",
        "pipeline",
        "kubernetes",
        "docker",
        "staging",
        "production",
        "infrastructure",
        "devops",
        "environment variables",
        "secrets",
        "rollback",
        "observability",
        "microservice",
        "terraform",
    ],
    "data_migration": [
        "data migration",
        "database migration",
        "schema migration",
        "migrate",
        "migration",
        "cutover",
        "etl",
        "data transfer",
    ],
    "event": [
        "workshop",
        "conference",
        "seminar",
        "meetup",
        "hackathon",
        "summit",
        "bootcamp",
        "training",
        "webinar",
        "festival",
        "ceremony",
        "event",
        "students",
        "participants",
        "attendees",
    ],
    "marketing_campaign": [
        "campaign",
        "newsletter",
        "marketing",
        "social media",
        "advertising",
        "email sequence",
        "subscribers",
        "brand awareness",
        "lead generation",
        "content calendar",
    ],
    "hiring": [
        "hire",
        "hiring",
        "recruit",
        "recruitment",
        "staffing",
        "talent",
        "headcount",
        "candidates",
    ],
    "product_launch": [
        "product launch",
        "launch a product",
        "launch the product",
        "go-to-market",
        "gtm",
        "new product",
        "app launch",
        "feature launch",
        "launch a new",
        "launch the new",
    ],
}

# Earlier domains win ties.
PRIORITY = [
    "software_deployment",
    "data_migration",
    "event",
    "marketing_campaign",
    "hiring",
    "product_launch",
]


def _task(title, description, priority, fraction, depends_on=None):
    return {
        "title": title,
        "description": description,
        "priority": priority,
        "fraction": fraction,
        "depends_on": depends_on,
    }


PROFILES = {
    "software_deployment": {
        "label": "software deployment",
        "requirements": [
            "Define the target environments and deployment architecture",
            "Identify services, dependencies and infrastructure changes",
            "Establish a CI/CD pipeline with gated promotion",
            "Define environment configuration and secrets management",
            "Define automated tests, security checks, monitoring and rollback criteria",
        ],
        "constraints": [
            "Deployment must preserve uptime and data integrity",
            "Changes must pass automated tests and security checks before promotion",
        ],
        "missing_information": [
            "Cloud/provider and target environment details",
            "Required uptime/SLO and approved maintenance window",
            "Secret manager and access ownership",
            "Rollback owner and incident escalation path",
        ],
        "risks": [
            "Configuration drift between staging and production",
            "Missing or incorrect secrets and environment variables",
            "Schema or data changes without a tested rollback path",
            "Insufficient monitoring during rollout",
        ],
        "assumptions": [
            "A CI/CD system and staging environment exist or can be provisioned",
            "An on-call owner is available to approve and monitor the release",
        ],
        "tasks": [
            _task(
                "Define deployment architecture and environment requirements",
                "Document target environments, services, dependencies and infrastructure changes.",
                "high",
                0.10,
            ),
            _task(
                "Configure CI/CD pipeline",
                "Set up build, test and deployment stages with gated promotion.",
                "high",
                0.25,
                "Define deployment architecture and environment requirements",
            ),
            _task(
                "Prepare environment variables and secrets",
                "Provision configuration and store credentials in the approved secret manager.",
                "high",
                0.35,
                "Define deployment architecture and environment requirements",
            ),
            _task(
                "Run automated tests and security checks",
                "Execute unit, integration and security scans; block the release on failures.",
                "high",
                0.50,
                "Configure CI/CD pipeline",
            ),
            _task(
                "Deploy to staging and validate",
                "Release to staging, run smoke tests and verify behaviour with production-like data.",
                "high",
                0.65,
                "Run automated tests and security checks",
            ),
            _task(
                "Deploy to production with rollback and monitoring plans",
                "Execute the production rollout with a tested rollback path and live monitoring.",
                "high",
                0.90,
                "Deploy to staging and validate",
            ),
        ],
        "communication": {
            "intro": "🚀 Deployment plan: {objective}",
            "lead": "Here's the release plan and what happens next:",
            "cta": "Stakeholders: reply with any constraints or maintenance-window conflicts.",
            "summary": "Deployment announcement covering the release plan, validation and rollback readiness.",
        },
    },
    "event": {
        "label": "event",
        "requirements": [
            "Clarify the event format, audience and expected outcomes",
            "Confirm venue, date, budget and available people",
            "Define the programme, speakers and supporting material",
            "Establish a registration and communication channel",
            "Define how success will be measured",
        ],
        "constraints": [
            "Event delivery depends on venue and speaker availability",
        ],
        "missing_information": [
            "Budget range and funding source",
            "Preferred date, time and location",
            "Required speakers or stakeholders",
            "Registration or participation mechanism",
        ],
        "risks": [
            "Short timeline leaves little buffer for approvals",
            "Audience turnout may be lower than target",
            "Venue or speaker availability is unconfirmed",
        ],
        "assumptions": [
            "The event is feasible within the stated timeframe",
            "An owner is available to approve external communication",
        ],
        "tasks": [
            _task(
                "Define scope and success criteria",
                "Confirm the event format, audience and measurable outcomes.",
                "high",
                0.05,
            ),
            _task(
                "Secure venue, budget and resources",
                "Confirm location, funding and the people required to deliver.",
                "high",
                0.20,
                "Define scope and success criteria",
            ),
            _task(
                "Prepare agenda and content",
                "Draft the programme, speakers and supporting material.",
                "medium",
                0.35,
                "Define scope and success criteria",
            ),
            _task(
                "Publish announcement and open registration",
                "Send the approved Telegram announcement and start collecting sign-ups.",
                "high",
                0.45,
                "Secure venue, budget and resources",
            ),
            _task(
                "Confirm participants and logistics",
                "Follow up with registrants and finalise operational details.",
                "medium",
                0.75,
                "Publish announcement and open registration",
            ),
            _task(
                "Execute and collect feedback",
                "Run the event and capture outcomes for follow-up.",
                "high",
                1.0,
                "Confirm participants and logistics",
            ),
        ],
        "communication": {
            "intro": "📢 {objective}",
            "lead": "We're moving fast: the full plan lands within {horizon} days.",
            "cta": "Stay tuned for updates. Reply if you want to take part.",
            "summary": "Event announcement summarising the plan and next steps.",
        },
    },
    "marketing_campaign": {
        "label": "marketing campaign",
        "requirements": [
            "Define the target audience and campaign goal",
            "Confirm channels, messaging and creative assets",
            "Prepare landing page, tracking and attribution",
            "Establish a content calendar and approval flow",
            "Define success metrics and reporting cadence",
        ],
        "constraints": [
            "Campaign performance depends on channel access and tracking",
        ],
        "missing_information": [
            "Budget and paid-channel allocation",
            "Primary conversion metric and target",
            "Brand guidelines and required approvals",
            "Tracking/analytics access",
        ],
        "risks": [
            "Messaging may not resonate with the target audience",
            "Tracking gaps make performance hard to measure",
            "Compressed timeline limits creative iteration",
        ],
        "assumptions": [
            "The audience and channels are reachable within the timeframe",
            "An owner is available to approve campaign assets",
        ],
        "tasks": [
            _task(
                "Define campaign goal, audience and success metrics",
                "Confirm the target segment, conversion goal and reporting cadence.",
                "high",
                0.10,
            ),
            _task(
                "Finalize messaging and creative assets",
                "Lock the core message, copy and visual assets for each channel.",
                "high",
                0.30,
                "Define campaign goal, audience and success metrics",
            ),
            _task(
                "Prepare landing page and tracking",
                "Publish the destination page and verify analytics and attribution.",
                "high",
                0.45,
                "Finalize messaging and creative assets",
            ),
            _task(
                "Build content and channel calendar",
                "Schedule posts, emails and paid placements across the campaign window.",
                "medium",
                0.60,
                "Prepare landing page and tracking",
            ),
            _task(
                "Launch campaign and monitor performance",
                "Activate channels and watch reach, conversion and spend.",
                "high",
                0.80,
                "Build content and channel calendar",
            ),
            _task(
                "Optimize and report results",
                "Adjust underperforming channels and publish the final performance report.",
                "medium",
                1.0,
                "Launch campaign and monitor performance",
            ),
        ],
        "communication": {
            "intro": "📣 Campaign plan: {objective}",
            "lead": "Here's how we'll launch and measure the campaign:",
            "cta": "Reply if you'd like to contribute creative or channel support.",
            "summary": "Campaign announcement outlining the launch plan and next steps.",
        },
    },
    "hiring": {
        "label": "hiring",
        "requirements": [
            "Define role profiles, levels and scorecards",
            "Confirm headcount, budget and compensation bands",
            "Select sourcing channels and employer branding",
            "Define the interview loop and decision process",
            "Prepare offer and onboarding steps",
        ],
        "constraints": [
            "Hiring timeline depends on candidate availability and approvals",
        ],
        "missing_information": [
            "Approved headcount and budget",
            "Compensation bands and location policy",
            "Interview panel availability",
            "Target start date",
        ],
        "risks": [
            "Competitive market may slow candidate pipelines",
            "Interview panel availability can bottleneck scheduling",
            "Unclear scorecards lead to inconsistent decisions",
        ],
        "assumptions": [
            "Headcount and budget can be approved quickly",
            "Hiring managers are available for interviews",
        ],
        "tasks": [
            _task(
                "Define role profiles and scorecards",
                "Document responsibilities, required skills and interview scorecards.",
                "high",
                0.10,
            ),
            _task(
                "Confirm headcount and budget approval",
                "Lock the approved positions, compensation bands and start dates.",
                "high",
                0.20,
                "Define role profiles and scorecards",
            ),
            _task(
                "Publish job posts and activate sourcing",
                "Post roles and start proactive candidate sourcing.",
                "high",
                0.35,
                "Confirm headcount and budget approval",
            ),
            _task(
                "Screen candidates and schedule interviews",
                "Review applications and coordinate interview loops.",
                "medium",
                0.55,
                "Publish job posts and activate sourcing",
            ),
            _task(
                "Run interview loops and collect feedback",
                "Execute interviews and consolidate structured feedback.",
                "high",
                0.75,
                "Screen candidates and schedule interviews",
            ),
            _task(
                "Extend offers and start onboarding",
                "Close selected candidates and begin onboarding.",
                "high",
                1.0,
                "Run interview loops and collect feedback",
            ),
        ],
        "communication": {
            "intro": "🧑‍💻 We're hiring: {objective}",
            "lead": "Here's the hiring plan and what happens next:",
            "cta": "Know someone great? Share this with them.",
            "summary": "Hiring announcement outlining the recruitment plan.",
        },
    },
    "product_launch": {
        "label": "product launch",
        "requirements": [
            "Define launch scope, target users and success metrics",
            "Finalize positioning, pricing and messaging",
            "Confirm product, documentation and support readiness",
            "Prepare launch assets and distribution channels",
            "Define go/no-go criteria and rollback plan",
        ],
        "constraints": [
            "Launch depends on product readiness and go/no-go approval",
        ],
        "missing_information": [
            "Launch date and release scope",
            "Pricing and packaging decisions",
            "Support and incident readiness owner",
            "Target adoption metrics",
        ],
        "risks": [
            "Product readiness may slip past the launch date",
            "Support may be unprepared for increased volume",
            "Unclear positioning weakens launch impact",
        ],
        "assumptions": [
            "The product is feature-complete enough to launch",
            "Marketing and support owners are available",
        ],
        "tasks": [
            _task(
                "Define launch scope, audience and success metrics",
                "Confirm what ships, who it is for and how success is measured.",
                "high",
                0.10,
            ),
            _task(
                "Finalize positioning and messaging",
                "Lock the value proposition, pricing and launch narrative.",
                "high",
                0.30,
                "Define launch scope, audience and success metrics",
            ),
            _task(
                "Prepare product, docs and support readiness",
                "Verify documentation, support coverage and operational readiness.",
                "high",
                0.50,
                "Finalize positioning and messaging",
            ),
            _task(
                "Build launch assets and landing page",
                "Produce the announcement, landing page and channel assets.",
                "medium",
                0.65,
                "Prepare product, docs and support readiness",
            ),
            _task(
                "Run launch checklist and go/no-go review",
                "Complete the readiness checklist and obtain go/no-go sign-off.",
                "high",
                0.85,
                "Build launch assets and landing page",
            ),
            _task(
                "Execute launch and monitor adoption",
                "Ship the launch, monitor adoption and address launch blockers.",
                "high",
                1.0,
                "Run launch checklist and go/no-go review",
            ),
        ],
        "communication": {
            "intro": "🚀 Launch plan: {objective}",
            "lead": "Here's the launch plan and what happens next:",
            "cta": "Reply with launch-blocking issues or customer commitments.",
            "summary": "Product launch announcement outlining readiness and next steps.",
        },
    },
    "data_migration": {
        "label": "data migration",
        "requirements": [
            "Document source and target systems, schemas and data volume",
            "Define migration strategy, downtime and cutover window",
            "Prepare migration scripts and validation queries",
            "Establish rollback and reconciliation procedures",
            "Define post-migration monitoring",
        ],
        "constraints": [
            "Cutover must fit the approved maintenance window",
        ],
        "missing_information": [
            "Data volume and growth rate",
            "Acceptable downtime and maintenance window",
            "Data ownership and validation sign-off",
            "Rollback time objective",
        ],
        "risks": [
            "Data loss or corruption during cutover",
            "Schema mismatches between source and target",
            "Downtime exceeding the approved window",
        ],
        "assumptions": [
            "Source and target systems are accessible for testing",
            "A rollback path can be maintained during cutover",
        ],
        "tasks": [
            _task(
                "Document source and target schemas and data volume",
                "Map fields, types and volume; flag transformations and gaps.",
                "high",
                0.10,
            ),
            _task(
                "Define migration strategy and cutover window",
                "Choose the migration approach and agree the maintenance window.",
                "high",
                0.25,
                "Document source and target schemas and data volume",
            ),
            _task(
                "Prepare migration scripts and validation queries",
                "Build repeatable scripts and checks for completeness and integrity.",
                "high",
                0.40,
                "Define migration strategy and cutover window",
            ),
            _task(
                "Rehearse migration in staging",
                "Run the full migration against a production-like copy and measure duration.",
                "high",
                0.60,
                "Prepare migration scripts and validation queries",
            ),
            _task(
                "Execute cutover and validate data integrity",
                "Perform the cutover, run validation queries and confirm sign-off.",
                "high",
                0.85,
                "Rehearse migration in staging",
            ),
            _task(
                "Monitor, reconcile and decommission the old path",
                "Watch production, reconcile discrepancies and retire the legacy source.",
                "medium",
                1.0,
                "Execute cutover and validate data integrity",
            ),
        ],
        "communication": {
            "intro": "🗄️ Migration plan: {objective}",
            "lead": "Here's the migration plan and what happens next:",
            "cta": "Reply with maintenance-window constraints or data concerns.",
            "summary": "Migration announcement outlining cutover, validation and rollback readiness.",
        },
    },
    "general": {
        "label": "project",
        "requirements": [
            "Clarify the concrete deliverable and success criteria",
            "Identify stakeholders and decision owners",
            "Confirm resources, budget and timeline",
            "Define the communication and approval flow",
            "Define how outcomes will be measured",
        ],
        "constraints": [
            "Scope depends on available resources and approval speed",
        ],
        "missing_information": [
            "Budget range and funding source",
            "Target date and key milestones",
            "Stakeholders and decision owners",
            "Success metrics",
        ],
        "risks": [
            "Timeline may be too tight for the scope",
            "Unclear ownership can slow decisions",
            "Resource availability is unconfirmed",
        ],
        "assumptions": [
            "The objective is feasible within the stated timeframe",
            "An owner is available to approve external communication",
        ],
        "tasks": [
            _task(
                "Define scope, stakeholders and success criteria",
                "Confirm the deliverable, decision owners and measurable outcomes.",
                "high",
                0.10,
            ),
            _task(
                "Confirm resources, budget and timeline",
                "Lock the people, funding and milestones required to deliver.",
                "high",
                0.25,
                "Define scope, stakeholders and success criteria",
            ),
            _task(
                "Prepare the execution plan and milestones",
                "Break the work into milestones with clear owners.",
                "medium",
                0.40,
                "Confirm resources, budget and timeline",
            ),
            _task(
                "Execute the first milestone",
                "Deliver the first milestone and validate the approach.",
                "high",
                0.60,
                "Prepare the execution plan and milestones",
            ),
            _task(
                "Review progress and resolve blockers",
                "Check progress against the plan and clear dependencies.",
                "medium",
                0.80,
                "Execute the first milestone",
            ),
            _task(
                "Deliver, verify and collect feedback",
                "Complete the objective, verify outcomes and capture feedback.",
                "high",
                1.0,
                "Review progress and resolve blockers",
            ),
        ],
        "communication": {
            "intro": "📋 Mission update: {objective}",
            "lead": "Here's the plan and what happens next:",
            "cta": "Reply with any constraints or questions.",
            "summary": "Mission announcement summarising the plan and next steps.",
        },
    },
}


def detect_domain(objective: str) -> str:
    text = f" {objective.lower()} "
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 2 if " " in keyword else 1
        if score:
            scores[domain] = score

    # Deployment language should win over a generic "launch" objective.
    if any(
        token in text
        for token in (
            "deploy",
            "deployment",
            "ci/cd",
            "cicd",
            "staging",
            "production",
            "rollout",
        )
    ):
        scores["software_deployment"] = scores.get("software_deployment", 0) + 2

    if not scores:
        return "general"

    return max(scores, key=lambda domain: (scores[domain], -PRIORITY.index(domain)))


def get_profile(objective: str) -> dict:
    domain = detect_domain(objective)
    profile = dict(PROFILES[domain])
    profile["domain"] = domain
    return profile
