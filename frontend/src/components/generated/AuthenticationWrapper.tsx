"use client";

import { ArrowRight, NotebookPen, Sparkles, Waypoints } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export interface AuthenticationWrapperProps {
  onEditContext?: () => void;
  onOpenSeededDemo?: () => void;
}

const productPillars = [
  {
    title: "Start from context",
    body: "The founder's stage, pressure, and constraints shape the day before any task gets recommended.",
    icon: NotebookPen,
  },
  {
    title: "Make judgment visible",
    body: "The brief explains why a priority matters now instead of dumping another list into the day.",
    icon: Sparkles,
  },
  {
    title: "Stay close to execution",
    body: "The plan moves into action, and the system learns from what actually got done or deferred.",
    icon: Waypoints,
  },
];

export default function AuthenticationWrapper({
  onEditContext,
  onOpenSeededDemo,
}: AuthenticationWrapperProps) {
  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(211,159,90,0.24),_transparent_32%),radial-gradient(circle_at_85%_8%,_rgba(94,109,90,0.18),_transparent_22%),linear-gradient(180deg,_rgba(246,241,232,1),_rgba(237,231,219,1))] px-4 py-8 text-[#1f2421] sm:px-6 lg:px-10">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative overflow-hidden rounded-[2rem] border border-white/70 bg-[#1f2421] px-6 py-8 text-[#f6f1e8] shadow-[0_24px_80px_rgba(27,30,35,0.22)] sm:px-8 lg:px-10">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent" />

          <div className="relative z-10 flex h-full flex-col justify-between gap-8">
            <div className="space-y-6">
              <div className="flex flex-wrap items-center gap-3">
                <Badge className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#f6f1e8]">
                  Daily Brief
                </Badge>
                <Badge className="rounded-full border border-white/15 bg-transparent px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-white/70">
                  Founder workspace
                </Badge>
              </div>

              <div className="max-w-3xl space-y-4">
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-white/60">AI chief-of-staff</p>
                <h1 className="font-display text-4xl leading-tight tracking-[-0.04em] text-[#f6f1e8] sm:text-5xl lg:text-6xl">
                  Start the day with a sharper operating plan.
                </h1>
                <p className="max-w-2xl text-base leading-7 text-white/72 sm:text-lg">
                  Daily Brief turns founder context into a focused plan, keeps the next move visible, and makes it
                  easier to protect the work that compounds.
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-4 sm:flex-row">
              <Button
                className="h-12 rounded-full bg-[#d39f5a] px-6 text-sm font-semibold text-[#1f2421] hover:bg-[#c48e49]"
                onClick={onOpenSeededDemo}
              >
                Open a sample workspace
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button
                className="h-12 rounded-full border border-white/20 bg-transparent px-6 text-sm font-semibold text-[#f6f1e8] hover:bg-white/10"
                onClick={onEditContext}
                variant="outline"
              >
                Start with founder context
              </Button>
            </div>
          </div>
        </section>

        <section className="grid gap-4">
          {productPillars.map((pillar) => {
            const Icon = pillar.icon;

            return (
              <Card
                key={pillar.title}
                className="border-[#ded6ca] bg-white/82 py-0 shadow-[0_12px_32px_rgba(27,30,35,0.06)]"
              >
                <CardHeader className="gap-4 px-6 py-6">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#f1eadf] text-[#1f2421]">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="font-display text-2xl tracking-[-0.03em] text-[#1f2421]">
                      {pillar.title}
                    </CardTitle>
                    <CardDescription className="text-sm leading-6 text-[#6d665d]">
                      {pillar.body}
                    </CardDescription>
                  </div>
                </CardHeader>
              </Card>
            );
          })}

          <Card className="border-dashed border-[#d7cabc] bg-[#f6f1e8] py-0">
            <CardContent className="px-6 py-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#7a7268]">What founders get</p>
              <p className="mt-3 text-sm leading-7 text-[#1f2421]">
                A clearer morning plan, visible tradeoffs, and an execution surface that stays close to the real work.
              </p>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}
