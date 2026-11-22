import {
  AlertTriangle,
  Check,
  Loader2,
  Send,
  ShieldCheck,
  X,
} from "lucide-react";
import { Card, EmptyState, SectionHeader, StatusBadge, formatDateTime } from "./ui";

function ApprovalCard({ approval, onApprove, onReject, busy }) {
  const pending = approval.status === "pending";
  const border =
    approval.status === "sent" || approval.status === "completed"
      ? "border-emerald-500/25"
      : approval.status === "rejected"
      ? "border-rose-500/25"
      : approval.status === "failed"
      ? "border-red-500/25"
      : approval.status === "approved"
      ? "border-sky-500/25"
      : "border-white/[0.08]";

  return (
    <div className={`rounded-xl border ${border} bg-white/[0.02] p-4`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg border border-violet-500/25 bg-violet-500/10 text-violet-300">
            <Send className="h-4 w-4" />
          </span>
          <div>
            <p className="text-xs font-semibold text-white">
              Telegram announcement
            </p>
            <p className="font-mono text-[10px] text-slate-500">
              {approval.id.slice(0, 8)} · {approval.channel}
            </p>
          </div>
        </div>
        <StatusBadge status={approval.status} />
      </div>

      {approval.mission_objective ? (
        <p className="mt-3 text-[11px] text-slate-500">
          <span className="text-slate-600">Mission:</span>{" "}
          {approval.mission_objective}
        </p>
      ) : null}

      <pre className="mt-2 max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg border border-white/[0.06] bg-ink-950/70 p-3 text-[11px] leading-relaxed text-slate-300">
        {approval.content}
      </pre>

      <div className="mt-3 grid gap-1 text-[10px] text-slate-500 sm:grid-cols-2">
        <span>
          Target:{" "}
          <span className="text-slate-400">
            {approval.target_chat_id
              ? `chat ${approval.target_chat_id}`
              : "not configured"}
          </span>
        </span>
        {approval.telegram_message_id ? (
          <span>
            Message:{" "}
            <span className="font-mono text-emerald-300">
              #{approval.telegram_message_id}
            </span>
          </span>
        ) : (
          <span>
            Decided:{" "}
            <span className="text-slate-400">
              {approval.decided_at ? formatDateTime(approval.decided_at) : "—"}
            </span>
          </span>
        )}
      </div>

      {approval.execution_note ? (
        <div
          className={`mt-3 flex items-start gap-2 rounded-lg border px-3 py-2 text-[11px] leading-relaxed ${
            approval.status === "failed"
              ? "border-red-500/25 bg-red-500/[0.07] text-red-200"
              : approval.status === "sent"
              ? "border-emerald-500/25 bg-emerald-500/[0.07] text-emerald-200"
              : "border-amber-500/25 bg-amber-500/[0.07] text-amber-200"
          }`}
        >
          {approval.status === "failed" ? (
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          ) : (
            <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          )}
          <span>{approval.execution_note}</span>
        </div>
      ) : null}

      {pending ? (
        <div className="mt-3 flex items-center justify-end gap-2">
          <button
            onClick={() => onReject(approval.id)}
            disabled={busy}
            className="inline-flex items-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/[0.06] px-3 py-2 text-xs font-medium text-rose-300 transition hover:bg-rose-500/[0.12] disabled:opacity-40"
          >
            {busy ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <X className="h-3.5 w-3.5" />
            )}
            Reject
          </button>
          <button
            onClick={() => onApprove(approval.id)}
            disabled={busy}
            className="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:from-emerald-500 hover:to-teal-500 disabled:opacity-40"
          >
            {busy ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Check className="h-3.5 w-3.5" />
            )}
            Approve &amp; send
          </button>
        </div>
      ) : null}
    </div>
  );
}

export default function ApprovalPanel({
  approvals = [],
  onApprove,
  onReject,
  busyId,
  title = "Approvals",
  subtitle = "External actions require a human decision",
  emptyTitle = "No approvals pending",
  emptyDescription = "New Telegram announcements will appear here for review before anything is sent.",
  bare = false,
}) {
  const sorted = [...approvals].sort((a, b) => {
    const rank = (status) => (status === "pending" ? 0 : 1);
    const diff = rank(a.status) - rank(b.status);
    if (diff !== 0) return diff;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  const body = (
    <>
      <SectionHeader
        icon={ShieldCheck}
        title={title}
        subtitle={subtitle}
        accent="bg-amber-500/10 text-amber-300"
        action={
          <span className="rounded-full border border-amber-500/25 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-300">
            {approvals.filter((a) => a.status === "pending").length} pending
          </span>
        }
      />
      <div className="mt-4 space-y-3">
        {sorted.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            title={emptyTitle}
            description={emptyDescription}
          />
        ) : (
          sorted.map((approval) => (
            <ApprovalCard
              key={approval.id}
              approval={approval}
              onApprove={onApprove}
              onReject={onReject}
              busy={busyId === approval.id}
            />
          ))
        )}
      </div>
    </>
  );

  if (bare) return <div>{body}</div>;
  return <Card className="p-5">{body}</Card>;
}
