import { useState } from "react";

import AuthenticationWrapper from "./components/generated/AuthenticationWrapper";
import MainView from "./components/generated/MainView";
import OnboardingView from "./components/generated/OnboardingView";
import { demoFounderData } from "./data/demo-founder";
import type { DemoFounderContext, DemoTask, DemoTaskStatus } from "./types/demo";

type DemoStage = "landing" | "context" | "workspace";

const demoDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "long",
  day: "numeric",
  weekday: "long",
});

function App() {
  const [stage, setStage] = useState<DemoStage>("landing");
  const [context, setContext] = useState<DemoFounderContext>(demoFounderData.context);
  const [tasks, setTasks] = useState<DemoTask[]>(demoFounderData.tasks);
  const [briefApproved, setBriefApproved] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(demoFounderData.tasks[0]?.id ?? null);
  const [latestLearning, setLatestLearning] = useState<string | null>(null);
  const brief = {
    ...demoFounderData.brief,
    dateLabel: demoDateFormatter.format(new Date()),
  };

  const resetDemo = () => {
    setStage("landing");
    setContext(demoFounderData.context);
    setTasks(demoFounderData.tasks);
    setBriefApproved(false);
    setSelectedTaskId(demoFounderData.tasks[0]?.id ?? null);
    setLatestLearning(null);
  };

  const openSeededWorkspace = () => {
    setContext(demoFounderData.context);
    setTasks(demoFounderData.tasks);
    setBriefApproved(false);
    setSelectedTaskId(demoFounderData.tasks[0]?.id ?? null);
    setLatestLearning(null);
    setStage("workspace");
  };

  const saveContext = (nextContext: DemoFounderContext) => {
    setContext(nextContext);
    setTasks(
      demoFounderData.tasks.map((task) =>
        task.id === "task-brief"
          ? {
              ...task,
              summary: `Check that ${nextContext.companyName}'s plan still matches the company reality before the day gets noisy.`,
              whyItMatters: `A quick review keeps ${nextContext.companyName} anchored to what matters most instead of reacting to the loudest open loop.`,
            }
          : task
      )
    );
    setSelectedTaskId(demoFounderData.tasks[0]?.id ?? null);
    setBriefApproved(false);
    setLatestLearning(null);
    setStage("workspace");
  };

  const moveTask = (taskId: string, nextStatus: DemoTaskStatus) => {
    const currentTask = tasks.find((task) => task.id === taskId);

    if (!currentTask) {
      return;
    }

    const updatedTask: DemoTask = { ...currentTask, status: nextStatus };

    setTasks((currentTasks) => currentTasks.map((task) => (task.id === taskId ? updatedTask : task)));
    setSelectedTaskId(taskId);

    if (nextStatus === "done") {
      setLatestLearning(
        `${updatedTask.title} is complete. The strongest pattern today: tasks move faster when the next decision and outcome are both explicit.`
      );
      return;
    }

    if (nextStatus === "parking-lot") {
      setLatestLearning(
        `${updatedTask.title} was parked. That is useful signal: timing was the blocker, not importance.`
      );
      return;
    }

    setLatestLearning(null);
  };

  if (stage === "landing") {
    return <AuthenticationWrapper onEditContext={() => setStage("context")} onOpenSeededDemo={openSeededWorkspace} />;
  }

  if (stage === "context") {
    return <OnboardingView initialContext={context} onSave={saveContext} onUseSeededContext={openSeededWorkspace} />;
  }

  return (
    <MainView
      brief={brief}
      briefApproved={briefApproved}
      columns={demoFounderData.columns}
      context={context}
      latestLearning={latestLearning}
      onApproveBrief={() => setBriefApproved(true)}
      onMoveTask={moveTask}
      onResetDemo={resetDemo}
      onSelectTask={setSelectedTaskId}
      selectedTaskId={selectedTaskId}
      tasks={tasks}
    />
  );
}

export default App;
