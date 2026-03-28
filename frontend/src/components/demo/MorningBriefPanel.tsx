import type { DemoFounderContext, DemoMorningBrief } from "../../types/demo";

export interface MorningBriefPanelProps {
  context: DemoFounderContext;
  brief: DemoMorningBrief;
  className?: string;
}

export function MorningBriefPanel({ context, brief, className }: MorningBriefPanelProps) {
  return (
    <section
      className={[
        "rounded-[2rem] border border-[#ded6ca] bg-white/82 p-6 shadow-[0_18px_60px_rgba(27,30,35,0.08)]",
        className ?? "",
      ].join(" ")}
    >
      <div className="space-y-5">
        <header className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-[#7a7268]">
            <span>{brief.dateLabel}</span>
            <span className="h-1 w-1 rounded-full bg-[#1f2421]/30" />
            <span>{context.companyName}</span>
            <span className="h-1 w-1 rounded-full bg-[#1f2421]/30" />
            <span>{brief.focusScore}</span>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{brief.headline}</p>
            <h2 className="font-display text-4xl tracking-[-0.05em] text-[#1f2421]">What deserves attention today.</h2>
            <p className="max-w-3xl text-sm leading-7 text-[#625a51] sm:text-base">{brief.rationale}</p>
          </div>
        </header>

        <div className="rounded-[1.5rem] border border-[#e5ddd1] bg-[#f8f3eb] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Top priorities</p>
          <ol className="mt-4 space-y-3">
            {brief.topPriorities.map((item, index) => (
              <li key={item} className="flex gap-3">
                <span className="mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1f2421] text-xs font-semibold text-[#f6f1e8]">
                  {index + 1}
                </span>
                <p className="text-sm leading-6 text-[#1f2421] sm:text-[15px]">{item}</p>
              </li>
            ))}
          </ol>
        </div>

        <div className="rounded-[1.5rem] border border-[#ded6ca] bg-[#f8f3eb] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Risks to watch</p>
          <ul className="mt-4 divide-y divide-[#e6ddd2]">
            {brief.risks.map((risk) => (
              <li key={risk} className="flex gap-3 py-4 first:pt-0 last:pb-0">
                <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-[#d39f5a]" />
                <span className="text-sm leading-6 text-[#1f2421]">{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
