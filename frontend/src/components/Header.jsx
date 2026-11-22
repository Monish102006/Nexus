import { RefreshCw, Send, Sparkles, Wifi } from "lucide-react";
import { NAV } from "./Sidebar";

function Pill({ icon: Icon, label, value, tone }) {
  const tones = {
    good: "border-emerald-500/25 bg-emerald-500/10 text-emerald-300",
    warn: "border-amber-500/25 bg-amber-500/10 text-amber-300",
    info: "border-indigo-500/25 bg-indigo-500/10 text-indigo-300",
    off: "border-white/10 bg-white/[0.03] text-slate-400",
  };
  return (
    <div
      className={`hidden items-center gap-2 rounded-full border px-3 py-1.5 text-[11px] font-medium sm:flex ${
        tones[tone] || tones.off
      }`}
    >
      <Icon className="h-3.5 w-3.5" />
      <span className="text-slate-400">{label}</span>
      <span>{value}</span>
    </div>
  );
}

export default function Header({
  title,
  health,
  onRefresh,
  refreshing,
  view,
  onNavigate,
}) {
  const demo = health?.demo_mode;
  return (
    <header className="sticky top-0 z-20 border-b border-white/[0.06] bg-ink-950/75 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-[1600px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-10">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 shadow-glow-sm lg:hidden">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <div>
            <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
              Command Center
            </div>
            <h1 className="text-lg font-semibold tracking-tight text-white sm:text-xl">
              {title}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <Pill
            icon={Sparkles}
            label="AI"
            value={demo ? "Demo" : "Live"}
            tone={demo ? "warn" : "good"}
          />
          <Pill
            icon={Send}
            label="Telegram"
            value={health?.telegram_running ? "Connected" : "Offline"}
            tone={health?.telegram_running ? "good" : "off"}
          />
          <Pill
            icon={Wifi}
            label="API"
            value={health ? "Online" : "Offline"}
            tone={health ? "good" : "info"}
          />
          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-white/[0.03] text-slate-400 transition hover:border-violet-500/40 hover:text-violet-300 disabled:opacity-50"
            title="Refresh data"
          >
            <RefreshCw
              className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto border-t border-white/[0.04] px-3 py-2 lg:hidden">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = view === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                active
                  ? "bg-white/[0.07] text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
}
