export type DemoPriority = "high" | "medium" | "low";
export type DemoTaskStatus = "parking-lot" | "todo" | "in-progress" | "done";

export interface DemoFounderContext {
  companyName: string;
  founderName: string;
  stage: string;
  targetCustomer: string;
  oneLineStrategy: string;
  currentFocus: string;
  constraints: string[];
  tone: string;
}

export interface DemoTask {
  id: string;
  title: string;
  summary: string;
  priority: DemoPriority;
  estimate: string;
  status: DemoTaskStatus;
  whyItMatters: string;
  okr: string;
  carryForward?: boolean;
  evidence?: string;
}

export interface DemoMorningBrief {
  dateLabel: string;
  headline: string;
  topPriorities: string[];
  risks: string[];
  changesSinceYesterday: string[];
  rationale: string;
  focusScore: string;
}

export interface DemoBoardColumn {
  id: DemoTaskStatus;
  title: string;
  description: string;
}

export interface DemoFounderDemo {
  context: DemoFounderContext;
  brief: DemoMorningBrief;
  tasks: DemoTask[];
  columns: DemoBoardColumn[];
}
