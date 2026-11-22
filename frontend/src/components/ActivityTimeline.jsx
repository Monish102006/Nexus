import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Flag,
  Info,
  Play,
  Rocket,
  Send,
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  XCircle,
} from "lucide-react";
import { Card, EmptyState, SectionHeader, timeAgo } from "./ui";

const ICONS = {
  mission_created: Rocket,
  mission_completed: Flag,
  mission_failed: XCircle,
  agent_started: Play,
  agent_completed: CheckCircle2,
  approval_requested: ShieldAlert,
  approval_approved: ShieldCheck,
  approval_rejected: ShieldX,
  telegram_sent: Send,
  telegram_failed: AlertTriangle,
  telegram_not_configured: Info,
};

const LEVEL_COLOR = {
  info: { bg: "bg-indigo-400", text: "text-indigo-300" },
  success: { bg: "bg-emerald-400", text: "text-emerald-300" },
  warning: { bg: "bg-amber-400", text: "text-amber-300" },
  error: { bg: "bg-rose-400", text: "text-rose-300" },
};

export default function ActivityTimeline({
  items = [],
  title = "Activity",
  subtitle = "Live execution timeline",
  showMission = false,
  maxHeight = "max-h-[420px]",
  bare = false,
}) {
  const body = (
    <>
      <SectionHeader
        icon={Activity}
        title={title}
        subtitle={subtitle}
        accent="bg-indigo-500/10 text-indigo-300"
        action={
          <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] text-slate-400">
            {items.length}
          </span>
        }
      />
      <div className={`mt-4 ${bare ? "" : maxHeight} overflow-y-auto pr-1`}>
        {items.length === 0 ? (
          <EmptyState
            icon={Activity}
            title="No activity yet"
            description="Agent runs and approval events will stream here in real time."
          />
        ) : (
          <div>
            {items.map((item, index) => {
              const Icon = ICONS[item.type] || Info;
              const color = LEVEL_COLOR[item.level] || LEVEL_COLOR.info;
              return (
                <div key={item.id} className="relative flex gap-3 pb-4 last:pb-0">
                  <div className="flex flex-col items-center">
                    <span
                      className={`mt-1 grid h-6 w-6 shrink-0 place-items-center rounded-full border border-white/10 bg-ink-900 ${color.text}`}
                    >
                      <Icon className="h-3 w-3" />
                    </span>
                    {index < items.length - 1 ? (
                      <span className="mt-1 w-px flex-1 bg-white/[0.06]" />
                    ) : null}
                  </div>
                  <div className="min-w-0 flex-1 pb-1">
                    <p className="text-xs leading-relaxed text-slate-300">
                      {item.message}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-[10px] text-slate-500">
                      <span className="font-mono uppercase tracking-wide">
                        {String(item.type || "").replaceAll("_", " ")}
                      </span>
                      <span>·</span>
                      <span>{timeAgo(item.created_at)}</span>
                    </div>
                    {showMission && item.mission_objective ? (
                      <p className="mt-1 truncate text-[10px] text-slate-600">
                        {item.mission_objective}
                      </p>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );

  if (bare) return <div>{body}</div>;
  return <Card className="p-5">{body}</Card>;
}
