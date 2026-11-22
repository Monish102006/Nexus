import { ChevronRight, Inbox, Rocket } from "lucide-react";
import { EmptyState, StatusBadge, timeAgo } from "./ui";

export default function MissionList({ missions = [], selectedId, onSelect }) {
  if (!missions.length) {
    return (
      <EmptyState
        icon={Inbox}
        title="No missions yet"
        description="Launch your first mission from the Overview tab. It will appear here with its full execution history."
      />
    );
  }

  return (
    <div className="space-y-2">
      {missions.map((mission) => {
        const active = mission.id === selectedId;
        return (
          <button
            key={mission.id}
            onClick={() => onSelect(mission.id)}
            className={`w-full rounded-xl border p-3.5 text-left transition ${
              active
                ? "border-violet-500/40 bg-violet-500/[0.07]"
                : "border-white/[0.06] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.035]"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="grid h-7 w-7 place-items-center rounded-lg border border-white/10 bg-white/[0.03] text-slate-400">
                  <Rocket className="h-3.5 w-3.5" />
                </span>
                <span className="font-mono text-[10px] text-slate-500">
                  {mission.id.slice(0, 8)}
                </span>
              </div>
              <StatusBadge status={mission.status} />
            </div>
            <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-slate-300">
              {mission.objective}
            </p>
            <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-500">
              <span>
                {mission.task_count} tasks · {mission.agent_count} agents
              </span>
              <span className="flex items-center gap-1">
                {timeAgo(mission.created_at)}
                <ChevronRight className="h-3 w-3" />
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
