import {
  AlertTriangle,
  CalendarDays,
  Check,
  ChevronDown,
  GitBranch,
  Layers,
  ListChecks,
  Rocket,
  Search,
  Send,
  Sparkles,
  Target,
} from "lucide-react";
import {
  Card,
  EmptyState,
  PriorityBadge,
  SectionHeader,
  StatusBadge,
  formatDateTime,
  timeAgo,
} from "./ui";
import ApprovalPanel from "./ApprovalPanel";

const STAGES = [
  { key: "research", label: "Research" },
  { key: "planning", label: "Planning" },
  { key: "communication", label: "Drafting" },
  { key: "approval", label: "Approval" },
  { key: "delivery", label: "Delivery" },
];

const OUTPUT_META = {
  research: {
    icon: Search,
    cls: "border-indigo-500/25 bg-indigo-500/10 text-indigo-300",
  },
  planning: {
    icon: ListChecks,
    cls: "border-violet-500/25 bg-violet-500/10 text-violet-300",
  },
  communication: {
    icon: Send,
    cls: "border-emerald-500/25 bg-emerald-500/10 text-emerald-300",
  },
};

function Bullets({ items }) {
  if (!items || items.length === 0) {
    return <p className="text-[11px] text-slate-600">None identified.</p>;
  }
  return (
    <ul className="space-y-1">
      {items.map((item, index) => (
        <li
          key={index}
          className="flex gap-2 text-[11px] leading-relaxed text-slate-400"
        >
          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-violet-400/70" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function ListBlock({ title, items }) {
  return (
    <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-3">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
        {title}
      </p>
      <Bullets items={items} />
    </div>
  );
}

function ResearchOutput({ output }) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2.5 sm:grid-cols-2">
        <ListBlock title="Requirements" items={output.requirements} />
        <ListBlock title="Constraints" items={output.constraints} />
        <ListBlock
          title="Missing information"
          items={output.missing_information}
        />
        <ListBlock title="Risks" items={output.risks} />
      </div>
      {output.assumptions?.length ? (
        <ListBlock title="Assumptions" items={output.assumptions} />
      ) : null}
      {output.research_notes ? (
        <p className="text-[10px] italic leading-relaxed text-slate-600">
          {output.research_notes}
        </p>
      ) : null}
    </div>
  );
}

function PlanningOutput({ output }) {
  return (
    <div className="space-y-2">
      {output.summary ? (
        <p className="text-[11px] leading-relaxed text-slate-300">
          {output.summary}
        </p>
      ) : null}
      <div className="flex flex-wrap gap-2 text-[10px] text-slate-500">
        <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5">
          Horizon: {output.horizon_days ?? "—"} days
        </span>
        <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5">
          Tasks: {output.tasks?.length ?? 0}
        </span>
      </div>
      {output.note ? (
        <p className="text-[10px] italic text-slate-600">{output.note}</p>
      ) : null}
    </div>
  );
}

function CommunicationOutput({ output }) {
  return (
    <div className="space-y-2">
      <pre className="max-h-56 overflow-y-auto whitespace-pre-wrap rounded-lg border border-white/[0.06] bg-ink-950/70 p-3 text-[11px] leading-relaxed text-slate-300">
        {output.announcement}
      </pre>
      {output.summary ? (
        <p className="text-[10px] text-slate-500">{output.summary}</p>
      ) : null}
    </div>
  );
}

function AgentOutput({ result }) {
  const meta = OUTPUT_META[result.agent_name] || OUTPUT_META.research;
  const Icon = meta.icon;
  const output = result.output || {};
  return (
    <details className="group rounded-xl border border-white/[0.06] bg-white/[0.02]">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-3.5 py-3">
        <span className="flex items-center gap-2 text-xs font-medium text-slate-200">
          <span
            className={`grid h-7 w-7 place-items-center rounded-lg border ${meta.cls}`}
          >
            <Icon className="h-3.5 w-3.5" />
          </span>
          {result.role || result.agent_name}
        </span>
        <span className="flex items-center gap-2">
          <span
            className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${
              result.source === "demo"
                ? "border-amber-500/25 bg-amber-500/10 text-amber-300"
                : "border-emerald-500/25 bg-emerald-500/10 text-emerald-300"
            }`}
          >
            {result.source}
          </span>
          <ChevronDown className="h-3.5 w-3.5 text-slate-500 transition group-open:rotate-180" />
        </span>
      </summary>
      <div className="border-t border-white/[0.05] px-3.5 py-3">
        {result.agent_name === "research" ? (
          <ResearchOutput output={output} />
        ) : result.agent_name === "planning" ? (
          <PlanningOutput output={output} />
        ) : (
          <CommunicationOutput output={output} />
        )}
      </div>
    </details>
  );
}

function computeStage(mission) {
  const names = (mission.agent_results || []).map((r) => r.agent_name);
  const approvals = mission.approvals || [];
  let stage = 0;
  if (names.includes("research")) stage = 1;
  if (names.includes("planning")) stage = 2;
  if (names.includes("communication")) stage = 3;
  if (
    mission.status === "awaiting_approval" ||
    approvals.some((a) => a.status !== "pending")
  ) {
    stage = 4;
  }
  if (mission.status === "completed") stage = 5;
  return stage;
}

export default function MissionDetail({
  mission,
  onApprove,
  onReject,
  busyId,
}) {
  if (!mission) {
    return (
      <Card className="p-5">
        <SectionHeader
          icon={Target}
          title="Active mission"
          subtitle="Select or launch a mission to inspect it"
        />
        <div className="mt-4">
          <EmptyState
            icon={Rocket}
            title="No mission selected"
            description="Enter an objective above. NEXUS will run the research, planning and communication agents and surface the draft for approval."
          />
        </div>
      </Card>
    );
  }

  const tasks = mission.tasks || [];
  const results = mission.agent_results || [];
  const approvals = mission.approvals || [];
  const stage = computeStage(mission);
  const pct = Math.round((stage / STAGES.length) * 100);
  const pendingApproval = approvals.find((a) => a.status === "pending");

  return (
    <div className="space-y-5">
      <Card className="relative overflow-hidden p-5">
        <div className="pointer-events-none absolute -right-20 -top-20 h-48 w-48 rounded-full bg-indigo-600/10 blur-3xl" />
        <div className="relative flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 font-mono text-[10px] text-slate-400">
              {mission.id.slice(0, 8)}
            </span>
            <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] text-slate-400">
              via {mission.source}
            </span>
          </div>
          <StatusBadge status={mission.status} />
        </div>

        <h2 className="relative mt-3 text-base font-semibold leading-snug text-white">
          {mission.objective}
        </h2>
        {mission.summary ? (
          <p className="relative mt-1.5 text-xs leading-relaxed text-slate-400">
            {mission.summary}
          </p>
        ) : null}

        <div className="relative mt-4">
          <div className="mb-2 flex items-center justify-between text-[10px] text-slate-500">
            <span className="uppercase tracking-[0.16em]">Mission progress</span>
            <span>{pct}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.05]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 via-indigo-500 to-blue-500 transition-all duration-700"
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="mt-3 grid grid-cols-5 gap-1">
            {STAGES.map((item, index) => {
              const done = index < stage;
              const current = index === stage;
              return (
                <div key={item.key} className="flex flex-col items-center gap-1">
                  <span
                    className={`grid h-5 w-5 place-items-center rounded-full border text-[9px] ${
                      done
                        ? "border-violet-500/40 bg-violet-500/20 text-violet-200"
                        : current
                        ? "border-indigo-400/50 bg-indigo-500/10 text-indigo-300 ring-2 ring-indigo-500/20"
                        : "border-white/10 bg-white/[0.02] text-slate-600"
                    }`}
                  >
                    {done ? <Check className="h-3 w-3" /> : index + 1}
                  </span>
                  <span
                    className={`text-[9px] ${
                      done || current ? "text-slate-300" : "text-slate-600"
                    }`}
                  >
                    {item.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {mission.error ? (
          <div className="relative mt-4 flex items-start gap-2 rounded-lg border border-rose-500/25 bg-rose-500/[0.07] px-3 py-2 text-[11px] text-rose-200">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            <span>{mission.error}</span>
          </div>
        ) : null}

        <div className="relative mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-white/[0.05] pt-3 text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <CalendarDays className="h-3 w-3" />
            Created {formatDateTime(mission.created_at)}
          </span>
          <span>Updated {timeAgo(mission.updated_at)}</span>
          {pendingApproval ? (
            <span className="flex items-center gap-1 text-amber-300">
              <Sparkles className="h-3 w-3" />
              Draft awaiting approval
            </span>
          ) : null}
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader
          icon={ListChecks}
          title="Task plan"
          subtitle={`${tasks.length} tasks · dependencies mapped`}
          accent="bg-violet-500/10 text-violet-300"
          action={
            <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] text-slate-400">
              {tasks.filter((t) => t.status === "completed").length}/
              {tasks.length} done
            </span>
          }
        />
        <div className="mt-4 space-y-2">
          {tasks.length === 0 ? (
            <EmptyState
              icon={ListChecks}
              title="Plan not generated yet"
              description="The planning agent will populate tasks once research completes."
            />
          ) : (
            tasks.map((task, index) => (
              <div
                key={task.id}
                className="flex gap-3 rounded-lg border border-white/[0.05] bg-white/[0.015] p-3"
              >
                <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-md border border-white/10 bg-white/[0.03] font-mono text-[10px] text-slate-400">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-xs font-medium text-slate-200">
                      {task.title}
                    </p>
                    <PriorityBadge priority={task.priority} />
                  </div>
                  {task.description ? (
                    <p className="mt-0.5 text-[11px] leading-relaxed text-slate-500">
                      {task.description}
                    </p>
                  ) : null}
                  <div className="mt-1.5 flex flex-wrap gap-3 text-[10px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <CalendarDays className="h-3 w-3" />
                      {task.deadline || "no deadline"}
                    </span>
                    {task.dependency ? (
                      <span className="flex items-center gap-1">
                        <GitBranch className="h-3 w-3" />
                        depends on “{task.dependency}”
                      </span>
                    ) : null}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader
          icon={Layers}
          title="Agent outputs"
          subtitle="Structured results passed between agents"
          accent="bg-indigo-500/10 text-indigo-300"
        />
        <div className="mt-4 space-y-2">
          {results.length === 0 ? (
            <EmptyState
              icon={Layers}
              title="Agents warming up"
              description="Structured research, planning and communication outputs will appear here."
            />
          ) : (
            results.map((result) => (
              <AgentOutput key={result.id} result={result} />
            ))
          )}
        </div>
      </Card>

      <Card className="p-5">
        <ApprovalPanel
          approvals={approvals}
          onApprove={onApprove}
          onReject={onReject}
          busyId={busyId}
          bare
          title="Approval & delivery"
          subtitle="Only approved actions may be sent to Telegram"
          emptyTitle="No approval requests"
          emptyDescription="The communication agent will create a draft announcement for this mission."
        />
      </Card>
    </div>
  );
}
