"use client";

import { useState, type ReactNode } from "react";
import { ArrowRight, PauseCircle, PlayCircle, RotateCcw, Sparkles, Trophy } from "lucide-react";

import { FounderBoard } from "@/components/demo/FounderBoard";
import { MorningBriefPanel } from "@/components/demo/MorningBriefPanel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { DemoBoardColumn, DemoFounderContext, DemoMorningBrief, DemoTask, DemoTaskStatus } from "@/types/demo";

export interface MainViewProps {
  context: DemoFounderContext;
  brief: DemoMorningBrief;
  columns: DemoBoardColumn[];
  tasks: DemoTask[];
  selectedTaskId: string | null;
  briefApproved: boolean;
  latestLearning?: string | null;
  onApproveBrief?: () => void;
  onSelectTask?: (taskId: string) => void;
  onMoveTask?: (taskId: string, status: DemoTaskStatus) => void;
  onResetDemo?: () => void;
}

export default function MainView({
  context,
  brief,
  columns,
  tasks,
  selectedTaskId,
  briefApproved,
  latestLearning,
  onApproveBrief,
  onSelectTask,
  onMoveTask,
  onResetDemo,
}: MainViewProps) {
  const [activeTab, setActiveTab] = useState<"overview" | "execution">("overview");
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const selectedTask = tasks.find((task) => task.id === selectedTaskId) ?? tasks[0];

  const handleApproveBrief = () => {
    onApproveBrief?.();
    setActiveTab("execution");
  };

  const handleTaskSelect = (task: DemoTask) => {
    onSelectTask?.(task.id);
    setActiveTab("execution");
    setInspectorOpen(true);
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(211,159,90,0.18),_transparent_30%),radial-gradient(circle_at_85%_0%,_rgba(94,109,90,0.14),_transparent_22%),linear-gradient(180deg,_rgba(246,241,232,1),_rgba(237,231,219,1))] px-4 py-8 text-[#1f2421] sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="grid gap-4 rounded-[2rem] border border-white/70 bg-white/78 px-6 py-6 shadow-[0_12px_40px_rgba(27,30,35,0.06)] lg:grid-cols-[1fr_auto] lg:items-center">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <Badge className="rounded-full border border-[#ded6ca] bg-[#f6f1e8] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#1f2421]">
                Daily Brief
              </Badge>
              <Badge className="rounded-full border border-[#ded6ca] bg-transparent px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7a7268]">
                {context.companyName}
              </Badge>
            </div>
            <div className="space-y-2">
              <h1 className="font-display text-4xl tracking-[-0.05em] text-[#1f2421]">Good morning, {context.founderName}.</h1>
              <p className="max-w-3xl text-sm leading-7 text-[#665f56] sm:text-base">
                One clear operating plan for {context.companyName}: protect the main thread, keep the day realistic,
                and move the most important work forward.
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            {!briefApproved ? (
              <Button
                className="h-11 rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] hover:bg-[#111512]"
                onClick={handleApproveBrief}
              >
                Approve today&apos;s plan
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Badge className="h-11 rounded-full border border-[#b8c4ad] bg-[#b8c4ad] px-5 text-sm font-semibold text-[#1f2421]">
                Plan is in motion
              </Badge>
            )}
            <Button
              className="h-11 rounded-full border border-[#ded6ca] bg-transparent px-5 text-sm font-semibold text-[#1f2421] hover:bg-white"
              onClick={onResetDemo}
              variant="outline"
            >
              <RotateCcw className="h-4 w-4" />
              Reset workspace
            </Button>
          </div>
        </header>

        <Tabs className="gap-5" value={activeTab} onValueChange={(value) => setActiveTab(value as "overview" | "execution")}>
          <TabsList className="h-auto rounded-full border border-[#ded6ca] bg-white/70 p-1">
            <TabsTrigger
              className="rounded-full px-5 py-2.5 text-sm font-semibold data-[state=active]:bg-[#1f2421] data-[state=active]:text-[#f6f1e8]"
              value="overview"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger
              className="rounded-full px-5 py-2.5 text-sm font-semibold data-[state=active]:bg-[#1f2421] data-[state=active]:text-[#f6f1e8]"
              value="execution"
            >
              Execution
            </TabsTrigger>
          </TabsList>

          <TabsContent className="space-y-6" value="overview">
            <MorningBriefPanel brief={brief} context={context} />

            {!briefApproved ? (
              <Card className="border-dashed border-[#d7cabc] bg-[#f7f0e5] py-0">
                <CardContent className="flex flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Next move</p>
                    <p className="text-sm leading-6 text-[#1f2421]">
                      Approve the plan when it feels right, then move into execution. You can still explore the board
                      before committing.
                    </p>
                  </div>
                  <Button
                    className="h-11 rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] hover:bg-[#111512]"
                    onClick={handleApproveBrief}
                  >
                    Approve and open execution
                  </Button>
                </CardContent>
              </Card>
            ) : null}

            <FounderSnapshot context={context} />

            {latestLearning ? (
              <Alert className="border-[#b8c4ad] bg-[#eef2e8] text-[#1f2421]">
                <Sparkles className="h-4 w-4" />
                <AlertTitle>Latest learning</AlertTitle>
                <AlertDescription>{latestLearning}</AlertDescription>
              </Alert>
            ) : null}
          </TabsContent>

          <TabsContent className="space-y-5" value="execution">
            {!briefApproved ? (
              <Card className="border-dashed border-[#d7cabc] bg-[#f7f0e5] py-0">
                <CardContent className="flex flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
                  <p className="text-sm leading-6 text-[#1f2421]">
                    The board is ready to inspect. Task actions unlock once you approve today&apos;s plan.
                  </p>
                  <Button
                    className="h-11 rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] hover:bg-[#111512]"
                    onClick={handleApproveBrief}
                  >
                    Approve today&apos;s plan
                  </Button>
                </CardContent>
              </Card>
            ) : null}

            <FounderBoard
              columns={columns}
              onSelectTask={handleTaskSelect}
              selectedTaskId={selectedTaskId}
              tasks={tasks}
            />

            {latestLearning ? (
              <Alert className="border-[#b8c4ad] bg-[#eef2e8] text-[#1f2421]">
                <Sparkles className="h-4 w-4" />
                <AlertTitle>Latest learning</AlertTitle>
                <AlertDescription>{latestLearning}</AlertDescription>
              </Alert>
            ) : null}
          </TabsContent>
        </Tabs>
      </div>

      <Sheet open={inspectorOpen} onOpenChange={setInspectorOpen}>
        <SheetContent
          className="w-full border-l border-[#ded6ca] bg-[#f8f4ee] sm:max-w-xl"
          side="right"
        >
          {selectedTask ? (
            <>
              <SheetHeader className="space-y-3 border-b border-[#e1d9cd] px-6 py-6">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Task detail</p>
                <SheetTitle className="font-display text-3xl tracking-[-0.04em] text-[#1f2421]">
                  {selectedTask.title}
                </SheetTitle>
                <SheetDescription className="text-sm leading-7 text-[#615a51]">
                  {selectedTask.summary}
                </SheetDescription>
                <div className="flex flex-wrap gap-2">
                  <TaskPriorityBadge priority={selectedTask.priority} />
                  <MetaBadge>{selectedTask.estimate}</MetaBadge>
                  <MetaBadge>{selectedTask.status.replace("-", " ")}</MetaBadge>
                </div>
              </SheetHeader>

              <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
                <InspectorBlock label="Why this exists" value={selectedTask.whyItMatters} />
                <InspectorBlock label="Linked outcome" value={selectedTask.okr} />
                {selectedTask.evidence ? <InspectorBlock label="Evidence" value={selectedTask.evidence} /> : null}

                {!briefApproved ? (
                  <Alert className="border-[#d7cabc] bg-[#f2eadf] text-[#1f2421]">
                    <Sparkles className="h-4 w-4" />
                    <AlertTitle>Waiting for approval</AlertTitle>
                    <AlertDescription>
                      You can inspect the task now. Status changes unlock after you approve today&apos;s plan.
                    </AlertDescription>
                  </Alert>
                ) : null}
              </div>

              <SheetFooter className="border-t border-[#e1d9cd] px-6 py-6">
                {!briefApproved ? (
                  <Button
                    className="h-11 rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] hover:bg-[#111512]"
                    onClick={handleApproveBrief}
                  >
                    Approve today&apos;s plan
                  </Button>
                ) : (
                  <TaskActions selectedTask={selectedTask} onMoveTask={onMoveTask} />
                )}
              </SheetFooter>
            </>
          ) : null}
        </SheetContent>
      </Sheet>
    </main>
  );
}

function FounderSnapshot({ context }: { context: DemoFounderContext }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <section className="rounded-[1.75rem] border border-[#ded6ca] bg-white/78 px-6 py-5 shadow-[0_10px_32px_rgba(27,30,35,0.05)]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Context and constraints</p>
          <p className="max-w-3xl text-sm leading-6 text-[#625a51]">
            {context.stage} for {context.targetCustomer}. {context.constraints.length} active constraints shaping the week.
          </p>
        </div>
        <Button
          className="h-10 rounded-full border border-[#ded6ca] bg-transparent px-4 text-sm font-semibold text-[#1f2421] hover:bg-white"
          onClick={() => setIsExpanded((current) => !current)}
          variant="outline"
        >
          {isExpanded ? "Hide details" : "Show details"}
        </Button>
      </div>

      {isExpanded ? (
        <div className="mt-6 space-y-4">
          <ContextRow label="Stage and customer">
            <div className="space-y-1">
              <p className="text-sm leading-6 text-[#1f2421]">{context.stage}</p>
              <p className="text-sm leading-6 text-[#625a51]">{context.targetCustomer}</p>
            </div>
          </ContextRow>

          <ContextRow label="Operating strategy">
            <p className="text-sm leading-6 text-[#1f2421]">{context.oneLineStrategy}</p>
          </ContextRow>

          <ContextRow label="Constraints">
            <div className="flex flex-wrap gap-2">
              {context.constraints.slice(0, 3).map((constraint) => (
                <MetaBadge key={constraint}>{constraint}</MetaBadge>
              ))}
            </div>
          </ContextRow>
        </div>
      ) : null}
    </section>
  );
}

function ContextRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-3 border-t border-[#ebe2d7] pt-4 sm:flex-row sm:items-start sm:justify-between">
      <p className="w-full max-w-52 text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{label}</p>
      <div className="w-full max-w-3xl">{children}</div>
    </div>
  );
}

function InspectorBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-2 rounded-[1.35rem] border border-[#ded6ca] bg-white/85 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{label}</p>
      <p className="text-sm leading-6 text-[#1f2421]">{value}</p>
    </div>
  );
}

function TaskPriorityBadge({ priority }: { priority: DemoTask["priority"] }) {
  const tone =
    priority === "high"
      ? "border-[#1f2421] bg-[#1f2421] text-[#f6f1e8]"
      : priority === "medium"
        ? "border-[#d39f5a] bg-[#d39f5a] text-[#1f2421]"
        : "border-[#b8c4ad] bg-[#b8c4ad] text-[#1f2421]";

  return (
    <Badge className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${tone}`}>
      {priority}
    </Badge>
  );
}

function MetaBadge({ children }: { children: string }) {
  return (
    <Badge className="rounded-full border border-[#ded6ca] bg-white px-3 py-1 text-xs font-medium text-[#1f2421]">
      {children}
    </Badge>
  );
}

function TaskActions({
  selectedTask,
  onMoveTask,
}: {
  selectedTask: DemoTask;
  onMoveTask?: (taskId: string, status: DemoTaskStatus) => void;
}) {
  if (selectedTask.status === "todo") {
    return (
      <div className="grid w-full gap-3">
        <ActionButton
          icon={<PlayCircle className="h-4 w-4" />}
          label="Start task"
          onClick={() => onMoveTask?.(selectedTask.id, "in-progress")}
        />
        <ActionButton
          icon={<PauseCircle className="h-4 w-4" />}
          label="Send to parking lot"
          onClick={() => onMoveTask?.(selectedTask.id, "parking-lot")}
          variant="outline"
        />
      </div>
    );
  }

  if (selectedTask.status === "in-progress") {
    return (
      <div className="grid w-full gap-3">
        <ActionButton
          icon={<Trophy className="h-4 w-4" />}
          label="Mark done"
          onClick={() => onMoveTask?.(selectedTask.id, "done")}
        />
        <ActionButton
          icon={<RotateCcw className="h-4 w-4" />}
          label="Move back to to-do"
          onClick={() => onMoveTask?.(selectedTask.id, "todo")}
          variant="outline"
        />
      </div>
    );
  }

  if (selectedTask.status === "parking-lot") {
    return (
      <ActionButton
        icon={<ArrowRight className="h-4 w-4" />}
        label="Restore to today"
        onClick={() => onMoveTask?.(selectedTask.id, "todo")}
      />
    );
  }

  return (
    <ActionButton
      icon={<RotateCcw className="h-4 w-4" />}
      label="Re-open task"
      onClick={() => onMoveTask?.(selectedTask.id, "todo")}
      variant="outline"
    />
  );
}

function ActionButton({
  icon,
  label,
  onClick,
  variant = "default",
}: {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  variant?: "default" | "outline";
}) {
  const className =
    variant === "default"
      ? "h-11 rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] hover:bg-[#111512]"
      : "h-11 rounded-full border border-[#ded6ca] bg-transparent px-5 text-sm font-semibold text-[#1f2421] hover:bg-white";

  return (
    <Button className={className} onClick={onClick} variant={variant === "default" ? "default" : "outline"}>
      {icon}
      {label}
    </Button>
  );
}
