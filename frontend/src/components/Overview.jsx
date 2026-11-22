import AgentCards from "./AgentCards";
import ActivityTimeline from "./ActivityTimeline";
import ApprovalPanel from "./ApprovalPanel";
import MissionComposer from "./MissionComposer";
import MissionDetail from "./MissionDetail";
import StatGrid from "./StatGrid";

export default function Overview({
  missions,
  selected,
  approvals,
  activity,
  agentsData,
  creating,
  onCreate,
  onApprove,
  onReject,
  busyId,
}) {
  const pending = approvals.filter((a) => a.status === "pending");

  return (
    <div className="space-y-6">
      <MissionComposer onCreate={onCreate} creating={creating} />
      <StatGrid
        missions={missions}
        approvals={approvals}
        agents={agentsData.agents}
      />
      <AgentCards agents={agentsData.agents} mode={agentsData.mode} />

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <MissionDetail
            mission={selected}
            onApprove={onApprove}
            onReject={onReject}
            busyId={busyId}
          />
        </div>
        <div className="space-y-6">
          <ApprovalPanel
            approvals={pending}
            onApprove={onApprove}
            onReject={onReject}
            busyId={busyId}
            title="Pending approvals"
            subtitle="Approve before anything is sent"
          />
          <ActivityTimeline
            items={activity.slice(0, 10)}
            title="Recent activity"
            subtitle="Latest orchestration events"
          />
        </div>
      </div>
    </div>
  );
}
