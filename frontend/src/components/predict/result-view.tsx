"use client";

import React, { useRef } from "react";
import { PredictionResponse, PredictionFactor } from "@/types/api";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { CheckCircle2, XCircle, Activity, BarChart3, Hash } from "lucide-react";

interface ResultViewProps {
  prediction: PredictionResponse | null;
  requestId: string | null;
}

export function ResultView({ prediction, requestId }: ResultViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const probNumberRef = useRef<HTMLSpanElement>(null);
  const probBarRef = useRef<HTMLDivElement>(null);
  const barsContainerRef = useRef<HTMLDivElement>(null);

  const isApproved = prediction?.outcome === "Approved";
  const probability = prediction?.probability ?? (isApproved ? 0.85 : 0.25);
  const factors = prediction?.explanation?.factors || [];

  useGSAP(
    () => {
      if (!prediction) return;

      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      // 1. Rolling probability ticker
      const targetPercent = Math.round(probability * 1000) / 10;
      const counter = { val: 0 };

      tl.to(counter, {
        val: targetPercent,
        duration: 0.6,
        ease: "power2.out",
        onUpdate: () => {
          if (probNumberRef.current) {
            probNumberRef.current.innerText = `${counter.val.toFixed(1)}%`;
          }
        },
      });

      // 2. Animate probability fill bar
      if (probBarRef.current) {
        tl.fromTo(
          probBarRef.current,
          { width: "0%" },
          { width: `${targetPercent}%`, duration: 0.6 },
          "<"
        );
      }

      // 3. Staggered shoot-out of TreeSHAP diverging bars
      if (barsContainerRef.current) {
        const barElements = barsContainerRef.current.querySelectorAll(".shap-bar-fill");
        tl.fromTo(
          barElements,
          { scaleX: 0 },
          { scaleX: 1, duration: 0.45, stagger: 0.04, transformOrigin: "left center" },
          "-=0.3"
        );
      }
    },
    { dependencies: [prediction], scope: containerRef }
  );

  if (!prediction) {
    return (
      <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-8 flex flex-col items-center justify-center text-center min-h-[420px]">
        <div className="w-10 h-10 rounded-full border border-zinc-800 bg-zinc-900 flex items-center justify-center mb-3 text-zinc-500">
          <Activity className="h-5 w-5" />
        </div>
        <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
          Underwriting Evaluation Terminal
        </h3>
        <p className="text-xs text-zinc-500 max-w-sm mt-1">
          Awaiting applicant input data. Submit the application ledger to generate TreeSHAP
          attribution factors and calibrated probability assessment.
        </p>
      </div>
    );
  }

  // Find max absolute weight for proportional bar scaling
  const maxWeight = Math.max(...factors.map((f) => Math.abs(f.weight)), 0.1);

  return (
    <div
      ref={containerRef}
      className="card-terminal rounded border border-[#22242a] bg-[#111216] p-5 shadow-sm space-y-5"
    >
      {/* Top Banner: Outcome & Calibrated Probability */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#22242a] gap-4">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 block">
            EVALUATION OUTCOME
          </span>
          <div className="flex items-center space-x-2 mt-1">
            {isApproved ? (
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs font-mono font-semibold tracking-wide">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>RECOMMENDED: APPROVED</span>
              </span>
            ) : (
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs font-mono font-semibold tracking-wide">
                <XCircle className="h-4 w-4 text-rose-400" />
                <span>RECOMMENDED: REJECTED</span>
              </span>
            )}
          </div>
        </div>

        {/* Probability Metric Meter */}
        <div className="sm:text-right">
          <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 block">
            CALIBRATED PROBABILITY
          </span>
          <div className="flex items-baseline sm:justify-end space-x-1 mt-0.5">
            <span
              ref={probNumberRef}
              className="text-2xl font-bold font-mono tracking-tight text-zinc-100"
            >
              0.0%
            </span>
          </div>
          <div className="w-36 h-1.5 bg-zinc-900 border border-zinc-800 rounded-full overflow-hidden mt-1 sm:ml-auto">
            <div
              ref={probBarRef}
              className={`h-full ${isApproved ? "bg-emerald-500" : "bg-rose-500"}`}
              style={{ width: "0%" }}
            />
          </div>
        </div>
      </div>

      {/* TreeSHAP Feature Attribution Ledger */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-1.5">
            <BarChart3 className="h-3.5 w-3.5 text-zinc-400" />
            <h4 className="text-xs font-mono uppercase tracking-wider text-zinc-300 font-semibold">
              Feature Contribution Analysis (TreeSHAP Δ)
            </h4>
          </div>
          <span className="text-[10px] font-mono text-zinc-500">
            BASE LOG-ODDS: +0.48
          </span>
        </div>

        <p className="text-[11px] text-zinc-400 mb-3">
          Local attribution values represent the marginal contribution of each applicant factor
          pushing the prediction towards approval (Emerald) or rejection (Rose).
        </p>

        {/* Factors List */}
        <div ref={barsContainerRef} className="space-y-2.5">
          {factors.map((factor: PredictionFactor, idx: number) => {
            const isPos = factor.impact === "positive";
            const percentWidth = Math.min((Math.abs(factor.weight) / maxWeight) * 100, 100);

            return (
              <div
                key={idx}
                className="group p-2.5 rounded border border-zinc-900 bg-zinc-950/70 hover:border-zinc-800 transition-colors"
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-mono text-zinc-200 font-medium">
                    {factor.factor}
                  </span>
                  <span
                    className={`font-mono text-xs font-semibold ${
                      isPos ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {isPos ? "+" : ""}
                    {factor.weight.toFixed(3)}
                  </span>
                </div>

                {/* Attribution Bar Graphic */}
                <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                  <div
                    className={`shap-bar-fill h-full rounded-full ${
                      isPos ? "bg-emerald-500" : "bg-rose-500"
                    }`}
                    style={{ width: `${percentWidth}%` }}
                  />
                </div>

                {/* Plain-text Context Narrative */}
                <p className="text-[11px] text-zinc-500 mt-1.5 group-hover:text-zinc-400 transition-colors">
                  {factor.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Audit Metadata Footer */}
      <div className="pt-3 border-t border-[#22242a] flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-zinc-500">
        <div className="flex items-center space-x-3">
          <span>MODEL: {prediction.model_version}</span>
          <span>RECORD ID: {prediction.prediction_id.slice(0, 8)}...</span>
        </div>
        {requestId && (
          <div className="flex items-center space-x-1">
            <Hash className="h-2.5 w-2.5" />
            <span>REQ_ID: {requestId.slice(0, 8)}...</span>
          </div>
        )}
      </div>
    </div>
  );
}

