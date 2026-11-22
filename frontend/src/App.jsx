import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Bot,
  Loader2,
  Rocket,
  ShieldCheck,
  Workflow,
} from "lucide-react";
import * as api from "./api";
import ActivityTimeline from "./components/ActivityTimeline";
import AgentCards from "./components/AgentCards";
import ApprovalPanel from "./components/ApprovalPanel";
import Header from "./components/Header";
import MissionDetail from "./components/MissionDetail";
import MissionList from "./components/MissionList";
import Overview from "./components/Overview";
import Sidebar from "./components/Sidebar";
import Toast from "./components/Toast";
import { Card, SectionHeader, timeAgo } from "./components/ui";

const TITLES = {
  overview: "Overview",
  missions: "Missions",
  agents: "Agent fleet",
  approvals: "Approvals",
  activity: "Activity",
};

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-32 text-slate-500">
      <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
      <p className="text-sm">Connecting to mission control…</p>
    </div>
  );
}

function MissionsView({
  missions,
  selectedId,
  selected,
  onSelect,
  onApprove,
  onReject,
  busyId,
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card className="p-5 lg:col-span-1">
        <SectionHeader
          icon={Rocket}
          title="Mission queue"
          subtitle={`${missions.length} total missions`}
        />
        <div className="mt-4 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
          <MissionList
            missions={missions}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        </div>
      </Card>
      <div className="lg:col-span-2">
        <MissionDetail
          mission={selected}
          onApprove={onApprove}
          onReject={onReject}
          busyId={busyId}
        />
      </div>
    </div>
  );
}

function AgentsView({ agentsData }) {
  const flow = [
    "Objective",
    "Research",
    "Planning",
    "Communication",
    "Approval",
    "Telegram",
  ];
  return (
    <div className="space-y-6">
      <AgentCards agents={agentsData.agents} mode={agentsData.mode} />

      <div className="grid gap-4 md:grid-cols-3">
        {agentsData.agents.map((agent) => (
          <Card key={agent.key} className="p-5">
            <SectionHeader
              icon={Bot}
              title={agent.name}
              subtitle={agent.description}
              accent="bg-violet-500/10 text-violet-300"
            />
            <div className="mt-3 flex flex-wrap gap-1.5">
              {(agent.capabilities || []).map((capability) => (
                <span
                  key={capability}
                  className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-1 text-[10px] text-slate-400"
                >
                  {capability}
                </span>
              ))}
            </div>
            <div className="mt-4 flex items-center justify-between border-t border-white/[0.05] pt-3 text-[10px] text-slate-500">
              <span>
                <span className="font-semibold text-slate-300">
                  {agent.runs ?? 0}
                </span>{" "}
                runs
              </span>
              <span>
                last {agent.last_run ? timeAgo(agent.last_run) : "never"}
              </span>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-5">
        <SectionHeader
          icon={Workflow}
          title="Orchestration flow"
          subtitle="Each agent receives the previous agent's structured output"
          accent="bg-indigo-500/10 text-indigo-300"
        />
        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {flow.map((step, index) => (
            <div
              key={step}
              className={`rounded-lg border px-3 py-2.5 text-center text-[11px] font-medium ${
                step === "Approval" || step === "Telegram"
                  ? "border-amber-500/25 bg-amber-500/[0.06] text-amber-200"
                  : "border-white/[0.07] bg-white/[0.02] text-slate-300"
              }`}
            >
              <span className="mb-1 block font-mono text-[9px] text-slate-600">
                0{index + 1}
              </span>
              {step}
            </div>
          ))}
        </div>
        <p className="mt-3 text-[10px] text-slate-600">
          External delivery is gated: the communication agent only drafts, and
          the orchestrator creates a pending approval.
        </p>
      </Card>
    </div>
  );
}

function ApprovalsView({ approvals, onApprove, onReject, busyId }) {
  const pending = approvals.filter((a) => a.status === "pending").length;
  return (
    <div className="space-y-6">
      <Card className="flex flex-wrap items-center justify-between gap-3 p-5">
        <SectionHeader
          icon={ShieldCheck}
          title="Human approval gate"
          subtitle="Only approved actions are sent to Telegram"
          accent="bg-amber-500/10 text-amber-300"
        />
        <div className="flex items-center gap-2 text-[11px]">
          <span className="rounded-full border border-amber-500/25 bg-amber-500/10 px-2.5 py-1 font-medium text-amber-300">
            {pending} pending
          </span>
          <span className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-slate-400">
            {approvals.length} total
          </span>
        </div>
      </Card>
      <ApprovalPanel
        approvals={approvals}
        onApprove={onApprove}
        onReject={onReject}
        busyId={busyId}
        title="Approval queue"
        subtitle="Review each draft before delivery"
        emptyTitle="Approval queue is empty"
        emptyDescription="Launch a mission and the communication agent will prepare a draft for review."
      />
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("overview");
  const [health, setHealth] = useState(null);
  const [missions, setMissions] = useState([]);
  const [agentsData, setAgentsData] = useState({ agents: [], mode: "demo" });
  const [approvals, setApprovals] = useState([]);
  const [activity, setActivity] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [creating, setCreating] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [toast, setToast] = useState(null);

  const notify = useCallback((type, message) => {
    setToast({ type, message, id: Date.now() });
  }, []);
  const closeToast = useCallback(() => setToast(null), []);

  const refreshLists = useCallback(
    async (silent = true) => {
      if (!silent) setRefreshing(true);
      try {
        const [
          healthRes,
          missionRes,
          agentRes,
          approvalRes,
          activityRes,
        ] = await Promise.allSettled([
          api.getHealth(),
          api.getMissions(),
          api.getAgents(),
          api.getApprovals(),
          api.getActivity(80),
        ]);

        if (healthRes.status === "fulfilled") {
          setHealth(healthRes.value);
        } else {
          setHealth(null);
        }

        if (missionRes.status === "fulfilled") {
          setMissions(missionRes.value);
        }
        if (agentRes.status === "fulfilled") {
          setAgentsData(agentRes.value);
        }
        if (approvalRes.status === "fulfilled") {
          setApprovals(approvalRes.value);
        }
        if (activityRes.status === "fulfilled") {
          setActivity(activityRes.value);
        }

        const firstRejected = [
          healthRes,
          missionRes,
          agentRes,
          approvalRes,
          activityRes,
        ].find((r) => r.status === "rejected");

        if (firstRejected && !silent) {
          notify("error", api.errText(firstRejected.reason));
        }
      } catch (error) {
        setHealth(null);
        if (!silent) notify("error", api.errText(error));
      } finally {
        setLoading(false);
        if (!silent) setRefreshing(false);
      }
    },
    [notify]
  );

  const loadSelected = useCallback(async (id) => {
    if (!id) {
      setSelected(null);
      return;
    }
    try {
      const mission = await api.getMission(id);
      setSelected(mission);
    } catch {
      // Keep the last known detail; polling will retry.
    }
  }, []);

  useEffect(() => {
    refreshLists(true);
  }, [refreshLists]);

  useEffect(() => {
    const timer = setInterval(() => refreshLists(true), 5000);
    return () => clearInterval(timer);
  }, [refreshLists]);

  useEffect(() => {
    if (selectedId) loadSelected(selectedId);
    else setSelected(null);
  }, [selectedId, loadSelected]);

  useEffect(() => {
    if (!selectedId && missions.length) {
      setSelectedId(missions[0].id);
    }
  }, [missions, selectedId]);

  useEffect(() => {
    if (!selectedId) return undefined;
    const timer = setInterval(() => loadSelected(selectedId), 5000);
    return () => clearInterval(timer);
  }, [selectedId, loadSelected]);

  const handleCreate = async (objective) => {
    setCreating(true);
    try {
      const mission = await api.createMission(objective);
      setSelectedId(mission.id);
      setSelected(mission);
      if (mission.status === "failed") {
        notify("error", mission.error || "Mission failed.");
      } else {
        notify(
          "success",
          "Mission processed. The Telegram announcement is awaiting approval."
        );
      }
      await refreshLists(true);
    } catch (error) {
      notify("error", api.errText(error));
    } finally {
      setCreating(false);
    }
  };

  const handleDecision = async (id, action) => {
    setBusyId(id);
    try {
      const result =
        action === "approve"
          ? await api.approveAction(id)
          : await api.rejectAction(id);

      if (action === "approve") {
        if (result.status === "sent") {
          notify(
            "success",
            `Approved and delivered to Telegram (message #${result.telegram_message_id}).`
          );
        } else if (result.status === "failed") {
          notify("error", result.execution_note || "Telegram delivery failed.");
        } else {
          notify(
            "info",
            result.execution_note || "Approved. Delivery was skipped."
          );
        }
      } else {
        notify("info", "Action rejected. Nothing was sent.");
      }

      await refreshLists(true);
      if (selectedId) await loadSelected(selectedId);
    } catch (error) {
      notify("error", api.errText(error));
    } finally {
      setBusyId(null);
    }
  };

  const pendingCount = approvals.filter((a) => a.status === "pending").length;

  return (
    <div className="min-h-screen">
      <Sidebar
        view={view}
        onNavigate={setView}
        health={health}
        pendingCount={pendingCount}
      />
      <div className="lg:pl-72">
        <Header
          title={TITLES[view]}
          health={health}
          onRefresh={() => refreshLists(false)}
          refreshing={refreshing}
          view={view}
          onNavigate={setView}
        />
        <main className="mx-auto max-w-[1600px] px-4 pb-16 pt-6 sm:px-6 lg:px-10">
          {loading ? (
            <LoadingState />
          ) : (
            <>
              {view === "overview" ? (
                <Overview
                  missions={missions}
                  selected={selected}
                  approvals={approvals}
                  activity={activity}
                  agentsData={agentsData}
                  creating={creating}
                  onCreate={handleCreate}
                  onApprove={(id) => handleDecision(id, "approve")}
                  onReject={(id) => handleDecision(id, "reject")}
                  busyId={busyId}
                />
              ) : null}

              {view === "missions" ? (
                <MissionsView
                  missions={missions}
                  selectedId={selectedId}
                  selected={selected}
                  onSelect={setSelectedId}
                  onApprove={(id) => handleDecision(id, "approve")}
                  onReject={(id) => handleDecision(id, "reject")}
                  busyId={busyId}
                />
              ) : null}

              {view === "agents" ? (
                <AgentsView agentsData={agentsData} />
              ) : null}

              {view === "approvals" ? (
                <ApprovalsView
                  approvals={approvals}
                  onApprove={(id) => handleDecision(id, "approve")}
                  onReject={(id) => handleDecision(id, "reject")}
                  busyId={busyId}
                />
              ) : null}

              {view === "activity" ? (
                <ActivityTimeline
                  items={activity}
                  showMission
                  maxHeight="max-h-none"
                  title="Activity stream"
                  subtitle="Every orchestration, agent and approval event"
                />
              ) : null}
            </>
          )}
        </main>
      </div>
      <Toast toast={toast} onClose={closeToast} />
    </div>
  );
}
