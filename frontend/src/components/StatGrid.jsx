import { Bot, CheckCheck, Rocket, ShieldAlert } from "lucide-react";

function Stat({ icon: Icon, label, value, hint, accent }) {
  return (
    <div className="panel relative overflow-hidden p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>
          <p className="mt-1.5 text-2xl font-semibold tracking-tight text-white">
            {value}
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">{hint}</p>
        </div>
        <span
          className={`grid h-9 w-9 place-items-center rounded-lg border ${accent}`}
        >
          <Icon className="h-4 w-4" />
        </span>
      </div>
    </div>
  );
}

export default function StatGrid({ missions = [], approvals = [], agents = [] }) {
  const pending = approvals.filter((a) => a.status === "pending").length;
  const delivered = approvals.filter((a) => a.status === "sent").length;
  const active = missions.filter(
    (m) => m.status === "running" || m.status === "awaiting_approval"
  ).length;

  return (
    <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
      <Stat
        icon={Rocket}
        label="Missions"
        value={missions.length}
        hint={`${active} active now`}
        accent="border-violet-500/25 bg-violet-500/10 text-violet-300"
      />
      <Stat
        icon={ShieldAlert}
        label="Pending approvals"
        value={pending}
        hint={pending ? "Awaiting human decision" : "Queue is clear"}
        accent="border-amber-500/25 bg-amber-500/10 text-amber-300"
      />
      <Stat
        icon={Bot}
        label="Agents online"
        value={agents.length}
        hint="Research · Plan · Comms"
        accent="border-indigo-500/25 bg-indigo-500/10 text-indigo-300"
      />
      <Stat
        icon={CheckCheck}
        label="Delivered"
        value={delivered}
        hint="Telegram messages sent"
        accent="border-emerald-500/25 bg-emerald-500/10 text-emerald-300"
      />
    </div>
  );
}
