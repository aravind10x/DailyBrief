"use client";

import { ArrowRight, WandSparkles } from "lucide-react";

import { FounderContextForm } from "@/components/demo/FounderContextForm";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { DemoFounderContext } from "@/types/demo";

export interface OnboardingViewProps {
  onSave?: (context: DemoFounderContext) => Promise<void> | void;
  initialContext?: DemoFounderContext;
  onUseSeededContext?: () => void;
}

export default function OnboardingView({
  onSave,
  initialContext,
  onUseSeededContext,
}: OnboardingViewProps) {
  if (!initialContext) {
    return null;
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(211,159,90,0.2),_transparent_30%),linear-gradient(180deg,_rgba(246,241,232,1),_rgba(237,231,219,1))] px-4 py-8 text-[#1f2421] sm:px-6 lg:px-10">
      <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <FounderContextForm className="bg-white/90" initialContext={initialContext} onSave={onSave} />

        <section className="grid gap-4">
          <Card className="border-[#ded6ca] bg-[#1f2421] py-0 text-[#f6f1e8] shadow-[0_18px_60px_rgba(27,30,35,0.18)]">
            <CardContent className="space-y-5 px-6 py-6">
              <Badge className="w-fit rounded-full border border-white/15 bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#f6f1e8]">
                Founder setup
              </Badge>
              <div className="space-y-3">
                <h1 className="font-display text-3xl tracking-[-0.04em] text-[#f6f1e8]">
                  Give the system enough context to make better calls.
                </h1>
                <p className="text-sm leading-7 text-white/72">
                  Keep it lightweight. The point is not to document the whole company. It is to make sure the brief
                  reflects the real business pressure of the week.
                </p>
              </div>
              <div className="grid gap-3 text-sm text-white/80">
                <div className="rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-4">
                  Stage, customer, and strategy shape the planning frame.
                </div>
                <div className="rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-4">
                  Constraints keep the day realistic instead of aspirational.
                </div>
                <div className="rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-4">
                  The next screen turns that context into a brief and an execution workspace.
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-dashed border-[#d7cabc] bg-[#f6f1e8] py-0">
            <CardContent className="space-y-4 px-6 py-6">
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7a7268]">Prefer a quick start?</p>
                <p className="text-sm leading-6 text-[#1f2421]">
                  Open the sample workspace if you want to inspect the founder flow first and come back to edit context later.
                </p>
              </div>

              <Button
                className="h-11 w-full rounded-full bg-[#d39f5a] text-sm font-semibold text-[#1f2421] hover:bg-[#c48e49]"
                onClick={onUseSeededContext}
              >
                <WandSparkles className="h-4 w-4" />
                Open the sample workspace
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}
