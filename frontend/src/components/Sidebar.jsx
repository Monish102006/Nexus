import {
  Activity,
  Bot,
  LayoutDashboard,
  Orbit,
  Rocket,
  ShieldCheck,
  Signal,
} from "lucide-react";

export const NAV = [
  { key: "overview", label: "Overview", icon: LayoutDashboard },
  { key: "missions", label: "Missions", icon: Rocket },
  { key: "agents", label: "Agents", icon: Bot },
  { key: "approvals", label: "Approvals", icon: ShieldCheck },
  { key: "activity", label: "Activity", icon: Activity },
];

function StatusRow({ label, value, tone }) {
  const toneMap = {
    good: "bg-emerald-400",
    warn: "bg-amber-400",
    off: "bg-slate-500",
    bad: "bg-rose-400",
  };
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-slate-500">{label}</span>
      <span className="flex items-center gap-1.5 text-slate-300">
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            toneMap[tone] || toneMap.off
          }`}
        />
        {value}
      </span>
    </div>
  );
}

export default function Sidebar({ view, onNavigate, health, pendingCount }) {
  const aiMode = !health
    ? { value: "Offline", tone: "off" }
    : health.demo_mode || health.mode === "demo"
    ? { value: "Demo", tone: "warn" }
    : { value: "Live", tone: "good" };

  const tgStatus = !health
    ? { value: "Offline", tone: "off" }
    : health.telegram_running
    ? { value: "Connected", tone: "good" }
    : { value: "Offline", tone: "off" };

  const apiStatus = health
    ? { value: "Online", tone: "good" }
    : { value: "Offline", tone: "bad" };
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 flex-col border-r border-white/[0.06] bg-ink-900/80 backdrop-blur-xl lg:flex">
      <div className="flex h-20 items-center gap-3 border-b border-white/[0.06] px-6">
        <div className="relative grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-violet-500 via-indigo-500 to-blue-600 shadow-glow">
          <Orbit className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="text-lg font-bold tracking-tight text-white">
            NEXUS
          </div>
          <div className="text-[10px] uppercase tracking-[0.28em] text-slate-500">
            Mission Control
          </div>
        </div>
      </div>

      <div className="px-4 pt-6">
        <div className="px-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-600">
          Workspace
        </div>
      </div>
      <nav className="mt-2 flex-1 space-y-1 px-3">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = view === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={`group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-white/[0.06] text-white"
                  : "text-slate-400 hover:bg-white/[0.03] hover:text-slate-200"
              }`}
            >
              {active ? (
                <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-gradient-to-b from-violet-400 to-indigo-500" />
              ) : null}
              <Icon
                className={`h-4 w-4 ${
                  active
                    ? "text-violet-300"
                    : "text-slate-500 group-hover:text-slate-300"
                }`}
              />
              <span className="font-medium">{item.label}</span>
              {item.key === "approvals" && pendingCount > 0 ? (
                <span className="ml-auto rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-300">
                  {pendingCount}
                </span>
              ) : null}
            </button>
          );
        })}
      </nav>

      <div className="space-y-3 border-t border-white/[0.06] p-4">
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
          <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
            <Signal className="h-3 w-3" /> System
          </div>
          <div className="space-y-1.5">
            <StatusRow
              label="AI mode"
              value={aiMode.value}
              tone={aiMode.tone}
            />
            <StatusRow
              label="Telegram"
              value={tgStatus.value}
              tone={tgStatus.tone}
            />
            <StatusRow
              label="API"
              value={apiStatus.value}
              tone={apiStatus.tone}
            />
          </div>
        </div>
        <p className="px-1 text-[10px] text-slate-600">
          NEXUS v1.0 · Autonomous workflows
        </p>
      </div>
    </aside>
  );
}
