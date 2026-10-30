"use client";

import React, { useState } from "react";
import { AuthGuard } from "@/components/auth/auth-guard";
import { Navbar } from "@/components/navigation/navbar";
import { LoanForm } from "@/components/predict/loan-form";
import { ResultView } from "@/components/predict/result-view";
import { PredictionInput, PredictionResponse } from "@/types/api";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/context/auth-context";

export default function PredictPage() {
  const { token } = useAuth();
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async (formData: PredictionInput) => {
    if (!token) return;
    setIsLoading(true);
    setError(null);

    try {
      const { prediction: result, requestId: resReqId } = await api.createPrediction(
        formData,
        token
      );
      setPrediction(result);
      setRequestId(resReqId);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(`${err.code}: ${err.message}`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to complete loan outcome evaluation.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#090a0c] text-zinc-100 flex flex-col">
        <Navbar />

        <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 py-6 sm:py-8">
          {/* Page Subtitle Banner */}
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#22242a] gap-2">
            <div>
              <h1 className="text-base font-semibold font-mono tracking-wider uppercase text-zinc-100">
                Underwriting Risk Workbench
              </h1>
              <p className="text-xs text-zinc-400 mt-0.5">
                Submit applicant parameters to execute Random Forest tree inference and generate
                local TreeSHAP feature attributions.
              </p>
            </div>
            <div className="text-[11px] font-mono text-zinc-500">
              CHAMPION MODEL: <span className="text-zinc-300">RandomForest (150 trees)</span>
            </div>
          </div>

          {/* Workbench Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Form */}
            <div className="lg:col-span-7">
              <LoanForm
                onSubmit={handleEvaluate}
                isLoading={isLoading}
                error={error}
              />
            </div>

            {/* Right Column: Output */}
            <div className="lg:col-span-5 sticky top-20">
              <ResultView prediction={prediction} requestId={requestId} />
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}

