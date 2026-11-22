import {
  Bot,
  ListChecks,
  Search,
  Send,
  Sparkles,
  Workflow,
} from "lucide-react";

const META = {
  research: {
    icon: Search,
    accent: "from-indigo-500/20 to-blue-500/5",
    iconCls: "border-indigo-500/25 bg-indigo-500/10 text-indigo-300",
    bar: "from-indigo-400 to-blue-500",
  },
  planning: {
    icon: ListChecks,
    accent: "from-violet-500/20 to-purple-500/5",
    iconCls: "border-violet-500/25 bg-violet-500/10 text-violet-300",
    bar: "from-violet-400 to-purple-500",
  },
  communication: {
    icon: Send,
    accent: "from-emerald-500/20 to-teal-500/5",
    iconCls: "border-emerald-500/25 bg-emerald-500/10 text-emerald-300",
    bar: "from-emerald-400 to-teal-500",
  },
};

function AgentCard({ agent, index }) {
  const meta = META[agent.key] || META.research;
  const Icon = meta.icon;
  return (
    <div className="panel panel-hover group relative overflow-hidden p-5">
      <div
        className={`pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b ${meta.accent} opacity-70`}
      />
      <div className="relative flex items-start justify-between">
        <span
          className={`grid h-10 w-10 place-items-center rounded-xl border ${meta.iconCls}`}
        >
          <Icon className="h-5 w-5" />
        </span>
        <div className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-2 py-1 text-[10px] font-medium text-slate-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
          ready
        </div>
      </div>

      <div className="relative mt-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-white">{agent.name}</h3>
          <span className="rounded border border-white/10 px-1.5 py-0.5 font-mono text-[9px] text-slate-500">
            0{index + 1}
          </span>
        </div>
        <p className="mt-1 text-xs leading-relaxed text-slate-500">
          {agent.description}
        </p>
      </div>

      <div className="relative mt-4 flex items-center justify-between border-t border-white/[0.06] pt-3 text-[11px]">
        <span className="text-slate-500">
          <span className="font-semibold text-slate-300">{agent.runs ?? 0}</span>{" "}
          runs
        </span>
        <span
          className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium ${
            agent.mode === "demo"
              ? "border-amber-500/25 bg-amber-500/10 text-amber-300"
              : "border-emerald-500/25 bg-emerald-500/10 text-emerald-300"
          }`}
        >
          <Sparkles className="h-2.5 w-2.5" />
          {agent.mode === "demo" ? "demo" : "live"}
        </span>
      </div>
      <div className="relative mt-2 h-0.5 w-full overflow-hidden rounded-full bg-white/[0.04]">
        <div
          className={`h-full w-1/3 rounded-full bg-gradient-to-r ${meta.bar} opacity-70 transition-all duration-500 group-hover:w-2/3`}
        />
      </div>
    </div>
  );
}

export default function AgentCards({ agents = [], mode = "demo" }) {
  if (!agents.length) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        {[0, 1, 2].map((index) => (
          <div
            key={index}
            className="panel h-44 animate-pulse bg-white/[0.02]"
          />
        ))}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          <Workflow className="h-3.5 w-3.5" />
          Agent fleet
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
          <Bot className="h-3.5 w-3.5" />
          {agents.length} specialised agents ·{" "}
          <span
            className={
              mode === "demo" ? "text-amber-300" : "text-emerald-300"
            }
          >
            {mode} mode
          </span>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {agents.map((agent, index) => (
          <AgentCard key={agent.key} agent={agent} index={index} />
        ))}
      </div>
    </div>
  );
}
