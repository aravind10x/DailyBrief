import { useEffect, useState } from "react";
import type { DemoFounderContext } from "../../types/demo";

export interface FounderContextFormProps {
  initialContext: DemoFounderContext;
  onSave?: (context: DemoFounderContext) => void;
  className?: string;
}

export function FounderContextForm({ initialContext, onSave, className }: FounderContextFormProps) {
  const [formState, setFormState] = useState<DemoFounderContext>(initialContext);
  const [constraintsDraft, setConstraintsDraft] = useState(initialContext.constraints.join("\n"));
  const parsedConstraints = parseConstraints(constraintsDraft);

  useEffect(() => {
    setFormState(initialContext);
    setConstraintsDraft(initialContext.constraints.join("\n"));
  }, [initialContext]);

  return (
    <section
      className={[
        "rounded-[2rem] border border-[#ded6ca] bg-white/85 p-6 shadow-[0_12px_40px_rgba(27,30,35,0.06)]",
        className ?? "",
      ].join(" ")}
    >
      <div className="max-w-2xl space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Founder context</p>
        <h2 className="text-2xl font-semibold tracking-tight text-[#1f2421]">Start with the real business context.</h2>
        <p className="text-sm leading-6 text-[#7a7268]">
          This demo shows how a founder can give the system just enough signal for it to act like a thoughtful
          chief-of-staff.
        </p>
      </div>

      <form
        className="mt-6 grid gap-4"
        onSubmit={(event) => {
          event.preventDefault();
          onSave?.({
            ...formState,
            constraints: parsedConstraints,
          });
        }}
      >
        <div className="grid gap-4 md:grid-cols-2">
          <Field
            label="Company"
            value={formState.companyName}
            onChange={(value) => setFormState((current) => ({ ...current, companyName: value }))}
          />
          <Field
            label="Founder"
            value={formState.founderName}
            onChange={(value) => setFormState((current) => ({ ...current, founderName: value }))}
          />
        </div>
        <Field
          label="Stage"
          value={formState.stage}
          onChange={(value) => setFormState((current) => ({ ...current, stage: value }))}
        />
        <Field
          label="Target customer"
          value={formState.targetCustomer}
          onChange={(value) => setFormState((current) => ({ ...current, targetCustomer: value }))}
        />
        <Field
          label="Operating tone"
          value={formState.tone}
          onChange={(value) => setFormState((current) => ({ ...current, tone: value }))}
        />
        <TextareaField
          label="One-line strategy"
          value={formState.oneLineStrategy}
          onChange={(value) => setFormState((current) => ({ ...current, oneLineStrategy: value }))}
        />
        <TextareaField
          label="Current focus"
          value={formState.currentFocus}
          onChange={(value) => setFormState((current) => ({ ...current, currentFocus: value }))}
        />

        <div className="grid gap-4 rounded-[1.25rem] border border-dashed border-[#ded6ca] bg-[#f6f1e8] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Constraints</p>
          <TextareaField
            label="Constraints (one per line)"
            value={constraintsDraft}
            onChange={setConstraintsDraft}
          />
          <div className="flex flex-wrap gap-2">
            {parsedConstraints.map((item) => (
              <span
                key={item}
                className="rounded-full border border-[#ded6ca] bg-white px-3 py-1 text-xs font-medium text-[#1f2421]"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="inline-flex h-11 items-center justify-center rounded-full bg-[#1f2421] px-5 text-sm font-semibold text-[#f6f1e8] transition-transform duration-200 hover:-translate-y-0.5"
        >
          Use this context
        </button>
      </form>
    </section>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function Field({ label, value, onChange }: FieldProps) {
  return (
    <label className="grid gap-2">
      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-11 rounded-2xl border border-[#ded6ca] bg-white px-4 text-sm text-[#1f2421] outline-none transition-shadow focus:shadow-[0_0_0_4px_rgba(27,30,35,0.08)]"
      />
    </label>
  );
}

interface TextareaFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function TextareaField({ label, value, onChange }: TextareaFieldProps) {
  return (
    <label className="grid gap-2">
      <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={4}
        className="rounded-[1.25rem] border border-[#ded6ca] bg-white px-4 py-3 text-sm leading-6 text-[#1f2421] outline-none transition-shadow focus:shadow-[0_0_0_4px_rgba(27,30,35,0.08)]"
      />
    </label>
  );
}

function parseConstraints(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}
