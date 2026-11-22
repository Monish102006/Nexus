import { ChevronRight } from "lucide-react";

export const STATUS = {
  pending: {
    label: "Pending",
    cls: "bg-slate-500/10 text-slate-300 border-slate-500/30",
    dot: "bg-slate-400",
  },
  running: {
    label: "Running",
    cls: "bg-violet-500/10 text-violet-300 border-violet-500/30",
    dot: "bg-violet-400 animate-pulse",
  },
  awaiting_approval: {
    label: "Awaiting approval",
    cls: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    dot: "bg-amber-400 animate-pulse",
  },
  approved: {
    label: "Approved",
    cls: "bg-sky-500/10 text-sky-300 border-sky-500/30",
    dot: "bg-sky-400",
  },
  sent: {
    label: "Sent",
    cls: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    dot: "bg-emerald-400",
  },
  completed: {
    label: "Completed",
    cls: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    dot: "bg-emerald-400",
  },
  rejected: {
    label: "Rejected",
    cls: "bg-rose-500/10 text-rose-300 border-rose-500/30",
    dot: "bg-rose-400",
  },
  failed: {
    label: "Failed",
    cls: "bg-red-500/10 text-red-300 border-red-500/30",
    dot: "bg-red-400",
  },
};

const PRIORITY = {
  high: "bg-rose-500/10 text-rose-300 border-rose-500/25",
  medium: "bg-amber-500/10 text-amber-300 border-amber-500/25",
  low: "bg-slate-500/10 text-slate-300 border-slate-500/25",
};

export function StatusBadge({ status }) {
  const meta = STATUS[status] || STATUS.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium ${meta.cls}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
      {meta.label}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const cls = PRIORITY[priority] || PRIORITY.medium;
  return (
    <span
      className={`inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${cls}`}
    >
      {priority || "medium"}
    </span>
  );
}

export function Card({ className = "", children, ...props }) {
  return (
    <div className={`panel ${className}`} {...props}>
      {children}
    </div>
  );
}

export function SectionHeader({ icon: Icon, title, subtitle, action, accent }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-center gap-3">
        {Icon ? (
          <span
            className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-white/10 ${
              accent || "bg-violet-500/10 text-violet-300"
            }`}
          >
            <Icon className="h-4 w-4" />
          </span>
        ) : null}
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-white">
            {title}
          </h2>
          {subtitle ? (
            <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>
          ) : null}
        </div>
      </div>
      {action}
    </div>
  );
}

export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-white/10 bg-white/[0.015] px-6 py-10 text-center">
      {Icon ? (
        <span className="grid h-10 w-10 place-items-center rounded-full bg-white/[0.04] text-slate-500">
          <Icon className="h-5 w-5" />
        </span>
      ) : null}
      <p className="text-sm font-medium text-slate-300">{title}</p>
      {description ? (
        <p className="max-w-xs text-xs leading-relaxed text-slate-500">
          {description}
        </p>
      ) : null}
    </div>
  );
}

export function ArrowHint({ children }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-slate-500">
      {children}
      <ChevronRight className="h-3 w-3" />
    </span>
  );
}

export function timeAgo(value) {
  if (!value) return "—";
  const then = new Date(value).getTime();
  if (Number.isNaN(then)) return "—";
  const seconds = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(value).toLocaleDateString();
}

export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
