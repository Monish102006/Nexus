import { ArrowUpRight, Loader2, Sparkles } from "lucide-react";
import { useState } from "react";

const EXAMPLES = [
  "Organize a technical workshop for 100 students within 10 days.",
  "Launch a developer newsletter for 5,000 subscribers within 21 days.",
  "Run a 48-hour hackathon for 200 participants within 30 days.",
];

const STAGES = ["Research", "Plan", "Communicate", "Approval"];

export default function MissionComposer({ onCreate, creating }) {
  const [objective, setObjective] = useState("");
  const disabled = creating || objective.trim().length < 3;

  const submit = () => {
    if (disabled) return;
    onCreate(objective.trim());
    setObjective("");
  };

  return (
    <div className="panel relative overflow-hidden p-5 sm:p-6">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-500/70 to-transparent" />
      <div className="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-violet-600/10 blur-3xl" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl border border-violet-500/25 bg-violet-500/10 text-violet-300">
            <Sparkles className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-base font-semibold tracking-tight text-white">
              Launch a mission
            </h2>
            <p className="text-xs text-slate-500">
              Describe the outcome. NEXUS researches, plans and drafts the
              announcement.
            </p>
          </div>
        </div>
        <span className="hidden rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-slate-400 sm:block">
          Human-in-the-loop
        </span>
      </div>

      <div className="relative mt-4">
        <textarea
          value={objective}
          onChange={(event) => setObjective(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
              submit();
            }
          }}
          rows={4}
          maxLength={4000}
          placeholder="e.g. Organize a technical workshop for 100 students within 10 days."
          className="w-full resize-none rounded-xl border border-white/10 bg-ink-950/70 px-4 py-3.5 text-sm leading-relaxed text-slate-100 placeholder:text-slate-600 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
        />
        <div className="pointer-events-none absolute bottom-3 right-3 text-[10px] text-slate-600">
          {objective.length}/4000
        </div>
      </div>

      {creating ? (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {STAGES.map((stage, index) => (
            <div key={stage} className="flex items-center gap-2">
              <span
                className="flex items-center gap-1.5 rounded-full border border-violet-500/25 bg-violet-500/10 px-2.5 py-1 text-[11px] font-medium text-violet-200"
                style={{ animationDelay: `${index * 120}ms` }}
              >
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400" />
                {stage}
              </span>
              {index < STAGES.length - 1 ? (
                <span className="h-px w-4 bg-white/10" />
              ) : null}
            </div>
          ))}
        </div>
      ) : (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              onClick={() => setObjective(example)}
              className="rounded-full border border-white/[0.07] bg-white/[0.02] px-2.5 py-1 text-[11px] text-slate-400 transition hover:border-violet-500/30 hover:text-violet-200"
            >
              {example.length > 52 ? `${example.slice(0, 52)}…` : example}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between gap-3">
        <p className="hidden text-[11px] text-slate-600 sm:block">
          Agents run in sequence. External actions require approval.
        </p>
        <button
          onClick={submit}
          disabled={disabled}
          className="group ml-auto inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-glow-sm transition hover:from-violet-500 hover:to-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {creating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          {creating ? "Orchestrating…" : "Deploy mission"}
          {!creating ? (
            <ArrowUpRight className="h-4 w-4 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          ) : null}
        </button>
      </div>
    </div>
  );
}
