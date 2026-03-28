import type { DemoBoardColumn, DemoTask } from "../../types/demo";

export interface FounderBoardProps {
  columns: DemoBoardColumn[];
  tasks: DemoTask[];
  selectedTaskId?: string | null;
  onSelectTask?: (task: DemoTask) => void;
  className?: string;
}

export function FounderBoard({ columns, tasks, selectedTaskId, onSelectTask, className }: FounderBoardProps) {
  return (
    <section className={["grid gap-4", className ?? ""].join(" ")}>
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Execution board</p>
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[#1f2421]">Today&apos;s execution</h2>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {columns.map((column) => {
          const items = tasks.filter((task) => task.status === column.id);

          return (
            <article key={column.id} className="rounded-[1.75rem] border border-[#ded6ca] bg-white/88 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{column.title}</h3>
                  <p className="text-sm leading-6 text-[#7a7268]">{column.description}</p>
                </div>
                <span className="rounded-full border border-[#ded6ca] bg-[#f6f1e8] px-3 py-1 text-xs font-semibold text-[#1f2421]">
                  {items.length}
                </span>
              </div>

              <div className="mt-4 space-y-3">
                {items.length === 0 ? (
                  <div className="rounded-[1.25rem] border border-dashed border-[#ded6ca] bg-[#f8f3eb] px-4 py-5 text-sm leading-6 text-[#7a7268]">
                    Nothing here right now.
                  </div>
                ) : null}

                {items.map((task) => (
                  <button
                    key={task.id}
                    type="button"
                    aria-pressed={selectedTaskId === task.id}
                    onClick={() => onSelectTask?.(task)}
                    className={[
                      "w-full rounded-[1.25rem] border p-4 text-left transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(27,30,35,0.08)]",
                      selectedTaskId === task.id
                        ? "border-[#1f2421] bg-white shadow-[0_12px_32px_rgba(27,30,35,0.1)]"
                        : "border-[#ded6ca] bg-[#f6f1e8]",
                    ].join(" ")}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <p className="text-base font-semibold text-[#1f2421]">{task.title}</p>
                        <p className="text-sm leading-6 text-[#7a7268]">{task.summary}</p>
                      </div>
                      <PriorityChip priority={task.priority} />
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      <MetaPill>{task.estimate}</MetaPill>
                      {task.carryForward ? <MetaPill tone="accent">Carry-forward</MetaPill> : null}
                    </div>
                  </button>
                ))}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function PriorityChip({ priority }: { priority: DemoTask["priority"] }) {
  const tone =
    priority === "high"
      ? "bg-[#1f2421] text-[#f6f1e8]"
      : priority === "medium"
        ? "bg-[#d39f5a] text-[#1f2421]"
        : "bg-[#b8c4ad] text-[#1f2421]";

  return (
    <span
      className={["shrink-0 rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em]", tone].join(" ")}
    >
      {priority}
    </span>
  );
}

function MetaPill({ children, tone = "default" }: { children: string; tone?: "default" | "accent" }) {
  const className =
    tone === "accent"
      ? "rounded-full bg-[#d39f5a]/20 px-3 py-1 text-xs font-semibold text-[#1f2421]"
      : "rounded-full border border-[#ded6ca] bg-white px-3 py-1 text-xs font-medium text-[#1f2421]";

  return <span className={className}>{children}</span>;
}
