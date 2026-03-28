import type { DemoFounderDemo } from "../types/demo";

export const demoFounderData: DemoFounderDemo = {
  context: {
    companyName: "AstraPilot",
    founderName: "Rhea",
    stage: "Seed, growing fast",
    targetCustomer: "COOs and revenue leaders at mid-market SaaS companies",
    oneLineStrategy:
      "Help revenue teams turn scattered customer, pipeline, and product signals into one confident weekly operating plan.",
    currentFocus:
      "Convert a strategic design partner, sharpen launch positioning, and fix onboarding friction before the next batch of pilots arrives.",
    constraints: [
      "Eight-person team with one open hiring decision",
      "Need a paid pilot this month to keep momentum strong",
      "Launch story still feels inconsistent across product and sales",
    ],
    tone: "Clear, ambitious, steady",
  },
  brief: {
    dateLabel: "Today",
    headline: "Daily brief",
    topPriorities: [
      "Prep the NexaCloud call so it ends with a concrete paid pilot proposal",
      "Lock the launch narrative so the website, product demo, and sales pitch tell the same story",
      "Resolve the onboarding drop-off in week one before new pilots amplify it",
    ],
    risks: [
      "Positioning drift could make the launch feel generic",
      "A vague pilot follow-up could stall a high-value account",
      "Hiring too early could add burn before demand is repeatable",
    ],
    changesSinceYesterday: [
      "NexaCloud asked for pricing and implementation timing before the next call",
      "Two onboarding users stalled at the workspace setup step",
      "The launch page draft is stronger, but the hero promise still feels broad",
    ],
    rationale:
      "Today is about tightening the chain between revenue, narrative, and product readiness. The best move is not to do more work, but to line up the work that compounds.",
    focusScore: "91% on the main thread",
  },
  tasks: [
    {
      id: "task-brief",
      title: "Review the daily brief",
      summary: "Make sure the plan still reflects the highest-leverage move for the company today.",
      priority: "high",
      estimate: "10 min",
      status: "todo",
      whyItMatters: "A short review prevents the day from drifting toward urgency instead of leverage.",
      okr: "Keep the team aligned on the most important company outcome",
    },
    {
      id: "task-pilot-call",
      title: "Prep the NexaCloud pilot call",
      summary: "Go in with a clear pilot proposal, pricing stance, and next-step ask.",
      priority: "high",
      estimate: "50 min",
      status: "in-progress",
      whyItMatters: "This is the closest path to new revenue and stronger social proof.",
      okr: "Convert a strategic design partner into a paid pilot",
      carryForward: true,
      evidence: "The account already asked for pricing and implementation timing, so the conversation needs to end with a concrete proposal.",
    },
    {
      id: "task-launch-story",
      title: "Tighten the launch narrative",
      summary: "Align the hero message, demo story, and sales framing around one clear promise.",
      priority: "high",
      estimate: "40 min",
      status: "todo",
      whyItMatters: "If the product story feels fuzzy, every downstream motion gets slower.",
      okr: "Launch with a message that sales and product can both defend",
    },
    {
      id: "task-onboarding-fix",
      title: "Choose the onboarding fix",
      summary: "Decide what to change in workspace setup before the next user cohort arrives.",
      priority: "medium",
      estimate: "35 min",
      status: "todo",
      whyItMatters: "Solving the first-week friction now is cheaper than scaling confusion.",
      okr: "Increase activation in the first week of a pilot",
    },
    {
      id: "task-signal-log",
      title: "Capture today’s strongest signal",
      summary: "Write down the single customer or product signal that should shape tomorrow’s plan.",
      priority: "low",
      estimate: "5 min",
      status: "parking-lot",
      whyItMatters: "A chief-of-staff gets sharper by learning what mattered, not by accumulating more tasks.",
      okr: "Improve the quality of tomorrow’s decisions",
    },
  ],
  columns: [
    {
      id: "parking-lot",
      title: "Parking Lot",
      description: "Worth keeping, not worth today",
    },
    {
      id: "todo",
      title: "To Do",
      description: "The short list that should define the day",
    },
    {
      id: "in-progress",
      title: "In Progress",
      description: "Work actively moving forward right now",
    },
    {
      id: "done",
      title: "Done",
      description: "Completed work the system can learn from",
    },
  ],
};
