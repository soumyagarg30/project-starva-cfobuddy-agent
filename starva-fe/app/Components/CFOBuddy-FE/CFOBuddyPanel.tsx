"use client";

import { FormEvent, useMemo, useState } from "react";

type RagResponse = {
  query: string;
  context_snippets: string[];
  metrics: Record<string, number | string>;
  insight: string;
  recommendation: string;
  answer: string;
};

type FinancialResponse = {
  unit_economics: Record<string, number>;
  cash_runway: Record<string, number>;
  break_even: Record<string, number>;
  discount_impact: Record<string, number>;
  scenario: Record<string, number>;
  insight: string;
  recommendation: string;
};

type FormulaName =
  | "calculate_unit_economics"
  | "calculate_cash_runway"
  | "calculate_break_even"
  | "calculate_discount_impact";

type FormulaResponse = {
  formula_name: string;
  formula_expression: string;
  result: Record<string, number>;
};

type FormulaConfig = {
  label: string;
  expression: string;
  accent: string;
  icon: string;
  fields: Array<{ key: string; label: string; defaultValue: number }>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const metricTitle = (key: string): string =>
  key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

const formulaConfigs: Record<FormulaName, FormulaConfig> = {
  calculate_unit_economics: {
    label: "calculate_unit_economics",
    accent: "from-orange-500 via-amber-500 to-yellow-400",
    icon: "UE",
    expression:
      "contribution_margin = price - variable_cost; cm_percent = (contribution_margin / price) * 100",
    fields: [
      { key: "price", label: "Price", defaultValue: 400 },
      { key: "variable_cost", label: "Variable Cost", defaultValue: 280 },
    ],
  },
  calculate_cash_runway: {
    label: "calculate_cash_runway",
    accent: "from-cyan-600 via-sky-500 to-blue-400",
    icon: "CR",
    expression:
      "burn_rate = fixed_cost + variable_cost - revenue; runway_months = cash_balance / burn_rate",
    fields: [
      { key: "cash_balance", label: "Cash Balance", defaultValue: 5000000 },
      { key: "revenue", label: "Revenue", defaultValue: 3000000 },
      { key: "fixed_cost", label: "Fixed Cost", defaultValue: 1500000 },
      { key: "variable_cost", label: "Variable Cost", defaultValue: 1000000 },
    ],
  },
  calculate_break_even: {
    label: "calculate_break_even",
    accent: "from-emerald-600 via-teal-500 to-lime-400",
    icon: "BE",
    expression: "break_even_orders = fixed_cost / contribution_margin",
    fields: [
      { key: "fixed_cost", label: "Fixed Cost", defaultValue: 1500000 },
      { key: "contribution_margin", label: "Contribution Margin", defaultValue: 120 },
    ],
  },
  calculate_discount_impact: {
    label: "calculate_discount_impact",
    accent: "from-fuchsia-600 via-pink-500 to-rose-400",
    icon: "DI",
    expression: "new_price = price * (1 - discount_pct); new_cm = new_price - cost",
    fields: [
      { key: "price", label: "Price", defaultValue: 400 },
      { key: "discount_pct", label: "Discount Pct (0.05 = 5%)", defaultValue: 0.05 },
      { key: "cost", label: "Cost", defaultValue: 280 },
    ],
  },
};

export default function CFOBuddyPanel() {
  const [activeTab, setActiveTab] = useState<"rag" | "strategist" | "formula" | "ceo">("ceo");
  const [query, setQuery] = useState("What is our runway and where is margin risk?");
  const [ragData, setRagData] = useState<RagResponse | null>(null);
  const [ragLoading, setRagLoading] = useState(false);

  const [modelInput, setModelInput] = useState({
    price: 400,
    variable_cost: 280,
    cash_balance: 5000000,
    revenue: 3000000,
    fixed_cost: 1500000,
    monthly_variable_cost: 1000000,
    discount_pct: 0.05,
    orders: 120000,
    growth_rate: 0.15,
  });
  const [financialData, setFinancialData] = useState<FinancialResponse | null>(null);
  const [financialLoading, setFinancialLoading] = useState(false);

  const [formulaName, setFormulaName] = useState<FormulaName>("calculate_unit_economics");
  const [formulaInputs, setFormulaInputs] = useState<Record<string, number>>({
    price: 400,
    variable_cost: 280,
  });
  const [formulaData, setFormulaData] = useState<FormulaResponse | null>(null);
  const [formulaLoading, setFormulaLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ceoMetrics = [
    { label: "MRR", value: "INR 18.4M", tone: "from-amber-200 to-orange-100", indicator: "bg-emerald-500" },
    { label: "Gross Margin", value: "31.2%", tone: "from-amber-100 to-yellow-50", indicator: "bg-amber-500", highlight: false },
    { label: "Runway", value: "8.4 months", tone: "from-sky-200 to-cyan-100", indicator: "bg-amber-500" },
    { label: "Repeat Rate", value: "46%", tone: "from-violet-200 to-fuchsia-100", indicator: "bg-emerald-500" },
    { label: "Risk Flag", value: "Medium", tone: "from-amber-100 to-yellow-50", indicator: "bg-amber-500", highlight: false },
    { label: "Action", value: "Reduce discount leakage", tone: "from-slate-200 to-stone-100", indicator: "bg-emerald-500" },
  ];

  const financialGroups = useMemo(() => {
    if (!financialData) return [];
    return [
      { title: "Unit Economics", data: financialData.unit_economics },
      { title: "Cash Burn & Runway", data: financialData.cash_runway },
      { title: "Break-even", data: financialData.break_even },
      { title: "Discount Impact", data: financialData.discount_impact },
      { title: "Scenario Modeling", data: financialData.scenario },
    ];
  }, [financialData]);

  const askRag = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setRagLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/cfobuddy/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch RAG response");
      }

      const data = (await response.json()) as RagResponse;
      setRagData(data);
    } catch {
      setError("Unable to connect to CFOBuddy backend for RAG query.");
    } finally {
      setRagLoading(false);
    }
  };

  const runFinancialModel = async () => {
    setError(null);
    setFinancialLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/cfobuddy/financial-strategist/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(modelInput),
      });

      if (!response.ok) {
        throw new Error("Failed to evaluate financial strategist model");
      }

      const data = (await response.json()) as FinancialResponse;
      setFinancialData(data);
    } catch {
      setError("Unable to run Financial Strategist. Verify backend is running.");
    } finally {
      setFinancialLoading(false);
    }
  };

  const onFormulaChange = (nextFormula: FormulaName) => {
    setFormulaName(nextFormula);
    const defaults = formulaConfigs[nextFormula].fields.reduce<Record<string, number>>(
      (acc, field) => {
        acc[field.key] = field.defaultValue;
        return acc;
      },
      {},
    );
    setFormulaInputs(defaults);
    setFormulaData(null);
  };

  const formulaCards = Object.entries(formulaConfigs).map(([key, config]) => {
    const formulaKey = key as FormulaName;
    const isSelected = formulaName === formulaKey;

    return (
      <button
        key={key}
        type="button"
        onClick={() => onFormulaChange(formulaKey)}
        className={`group relative overflow-hidden rounded-3xl border p-4 text-left transition duration-200 hover:-translate-y-1 hover:shadow-xl ${
          isSelected
            ? "border-transparent bg-slate-950 text-white shadow-[0_18px_45px_rgba(15,23,42,0.25)]"
            : "border-slate-200 bg-white text-slate-800"
        }`}
      >
        <div className={`absolute inset-x-0 top-0 h-1 bg-linear-to-r ${config.accent}`} />
        <div className="relative flex items-start justify-between gap-3">
          <div className={`flex h-11 w-11 items-center justify-center rounded-2xl bg-linear-to-br ${config.accent} text-sm font-black text-white shadow-lg`}>
            {config.icon}
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold tracking-[0.18em] ${
              isSelected ? "bg-white/10 text-white" : "bg-slate-100 text-slate-500"
            }`}
          >
            Formula
          </span>
        </div>
        <h3 className={`mt-4 text-lg font-bold ${isSelected ? "text-white" : "text-slate-900"}`}>
          {config.label}
        </h3>
        <p className={`mt-2 text-sm leading-6 ${isSelected ? "text-slate-200" : "text-slate-600"}`}>
          {config.expression}
        </p>
      </button>
    );
  });

  const runFormulaCalculation = async () => {
    setError(null);
    setFormulaLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/cfobuddy/formula/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          formula_name: formulaName,
          inputs: formulaInputs,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to calculate formula");
      }

      const data = (await response.json()) as FormulaResponse;
      setFormulaData(data);
    } catch {
      setError("Unable to run formula calculation on backend.");
    } finally {
      setFormulaLoading(false);
    }
  };

  const downloadRagReport = () => {
    const report = ragData
      ? [
          "# CFOBuddy RAG Report",
          "",
          `Query: ${ragData.query}`,
          "",
          "## Context",
          ...ragData.context_snippets.map((snippet) => `- ${snippet}`),
          "",
          "## Metrics",
          ...Object.entries(ragData.metrics).map(([key, value]) => `- ${metricTitle(key)}: ${value}`),
          "",
          "## Insight",
          ragData.insight,
          "",
          "## Recommendation",
          ragData.recommendation,
          "",
          "## Executive Answer",
          ragData.answer,
        ].join("\n")
      : [
          "# CFOBuddy RAG Report",
          "",
          `Query: ${query}`,
          "",
          "No report has been generated yet.",
        ].join("\n");

    const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const fileStamp = new Date().toISOString().replaceAll(":", "-").slice(0, 19);

    anchor.href = url;
    anchor.download = `cfobuddy-rag-report-${fileStamp}.md`;
    anchor.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_10%_20%,#fef3c7_0%,#fde68a_15%,#fff7ed_45%,#ecfeff_100%)] px-4 py-8 text-slate-900 md:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="rounded-3xl border border-slate-900/10 bg-white/80 p-6 shadow-xl backdrop-blur md:p-10">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-orange-700">Project Starva</p>
          <h1 className="mt-3 text-3xl font-black leading-tight md:text-5xl">
            CFOBuddy Agentic Financial Decision System
          </h1>
          <p className="mt-4 max-w-3xl text-slate-700">
            CFO-to-CEO reporting and agentic decision-support system for RAG and
            Financial Strategist workflows. Use it to simulate CFO-grade reporting,
            executive summaries, and decision-ready metrics with deterministic outputs.
          </p>
        </header>

        <div className="mt-8 rounded-3xl border border-slate-900/10 bg-white/70 p-3 shadow-lg">
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
            <button
              type="button"
              onClick={() => setActiveTab("ceo")}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                activeTab === "ceo" ? "bg-fuchsia-700 text-white" : "bg-white text-slate-700"
              }`}
            >
              CEO Dashboard
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("rag")}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                activeTab === "rag" ? "bg-orange-600 text-white" : "bg-white text-slate-700"
              }`}
            >
              RAG Module
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("strategist")}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                activeTab === "strategist" ? "bg-cyan-700 text-white" : "bg-white text-slate-700"
              }`}
            >
              Financial Strategist
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("formula")}
              className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                activeTab === "formula" ? "bg-slate-900 text-white" : "bg-white text-slate-700"
              }`}
            >
              Formula Calculation
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-6">
          {activeTab === "rag" && (
            <section className="rounded-3xl border border-slate-900/10 bg-white/85 p-6 shadow-lg">
              <h2 className="text-2xl font-bold">RAG Module</h2>
              <p className="mt-2 text-sm text-slate-600">
                Retrieves demo finance context and returns CFO-style insights.
              </p>
              <form className="mt-4 space-y-3" onSubmit={askRag}>
                <textarea
                  className="h-32 w-full rounded-xl border border-slate-300 bg-white p-3 outline-none ring-orange-300 transition focus:ring"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                <button
                  type="submit"
                  className="rounded-xl bg-orange-600 px-4 py-2 font-semibold text-white transition hover:bg-orange-700"
                  disabled={ragLoading}
                >
                  {ragLoading ? "Thinking..." : "Ask CFOBuddy"}
                </button>
              </form>

              {ragData && (
                <div className="mt-5 space-y-4">
                  <div className="rounded-xl bg-orange-50 p-3">
                    <h3 className="font-semibold">Context</h3>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
                      {ragData.context_snippets.map((snippet, index) => (
                        <li key={`${snippet}-${index}`}>{snippet}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(ragData.metrics).map(([key, value]) => (
                      <div key={key} className="rounded-xl bg-slate-100 p-3">
                        <p className="text-xs uppercase tracking-wide text-slate-500">{metricTitle(key)}</p>
                        <p className="text-sm font-bold text-slate-800">{String(value)}</p>
                      </div>
                    ))}
                  </div>

                  <pre className="whitespace-pre-wrap rounded-xl bg-slate-900 p-3 text-sm text-slate-100">
                    {ragData.answer}
                  </pre>

                  <div className="flex justify-end pt-1">
                    <button
                      type="button"
                      onClick={downloadRagReport}
                      className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
                    >
                      Download Report
                    </button>
                  </div>
                </div>
              )}
            </section>
          )}

          {activeTab === "strategist" && (
            <section className="rounded-3xl border border-slate-900/10 bg-white/85 p-6 shadow-lg">
              <h2 className="text-2xl font-bold">Financial Strategist</h2>
              <p className="mt-2 text-sm text-slate-600">
                Runs all 5 core financial functions with configurable inputs.
              </p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm md:grid-cols-3">
                {Object.entries(modelInput).map(([key, value]) => (
                  <label key={key} className="flex flex-col gap-1">
                    <span className="font-medium text-slate-600">{metricTitle(key)}</span>
                    <input
                      type="number"
                      value={value}
                      className="rounded-lg border border-slate-300 p-2"
                      onChange={(event) =>
                        setModelInput((previous) => ({
                          ...previous,
                          [key]: Number(event.target.value),
                        }))
                      }
                    />
                  </label>
                ))}
              </div>

              <button
                type="button"
                className="mt-4 rounded-xl bg-cyan-700 px-4 py-2 font-semibold text-white transition hover:bg-cyan-800"
                disabled={financialLoading}
                onClick={runFinancialModel}
              >
                {financialLoading ? "Running model..." : "Run Financial Strategist"}
              </button>

              {financialData && (
                <div className="mt-5 space-y-3">
                  {financialGroups.map((group) => (
                    <div key={group.title} className="rounded-xl bg-cyan-50 p-3">
                      <h3 className="font-semibold text-cyan-900">{group.title}</h3>
                      <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                        {Object.entries(group.data).map(([key, value]) => (
                          <div key={key} className="rounded-lg bg-white p-2">
                            <p className="text-xs uppercase tracking-wide text-slate-500">{metricTitle(key)}</p>
                            <p className="font-semibold text-slate-800">{String(value)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  <div className="rounded-xl bg-slate-900 p-3 text-sm text-white">
                    <p className="font-semibold">Insight</p>
                    <p className="mt-1 text-slate-200">{financialData.insight}</p>
                    <p className="mt-3 font-semibold">Recommendation</p>
                    <p className="mt-1 text-slate-200">{financialData.recommendation}</p>
                  </div>
                </div>
              )}
            </section>
          )}

          {activeTab === "ceo" && (
            <section className="overflow-hidden rounded-4xl border border-slate-900/10 bg-white/90 shadow-[0_20px_60px_rgba(15,23,42,0.12)] backdrop-blur">
              <div className="border-b border-slate-200 bg-linear-to-r from-slate-950 via-slate-900 to-fuchsia-950 px-6 py-6 text-white md:px-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-300">
                      CEO Dashboard
                    </p>
                    <h2 className="mt-2 text-2xl font-black md:text-3xl">
                      Executive health overview
                    </h2>
                    <p className="mt-2 max-w-2xl text-sm text-slate-300">
                      A concise demo view for margin, runway, and decision risk.
                    </p>
                  </div>

                  <div className="rounded-full border border-amber-300/40 bg-amber-400/15 px-4 py-2 text-sm font-semibold text-amber-200">
                    Overall Risk: Medium
                  </div>
                </div>
              </div>

              <div className="p-6 md:p-8">
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {ceoMetrics.map((metric) => (
                    <div
                      key={metric.label}
                      className={`rounded-3xl bg-linear-to-br ${metric.tone} p-4 shadow-sm ring-1 ring-white/60 transition-transform hover:-translate-y-0.5`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`h-2.5 w-2.5 rounded-full ${metric.indicator}`} />
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-700">
                          {metric.label}
                        </p>
                      </div>
                      <p
                        className={`mt-3 text-2xl font-black ${
                          metric.label === "Gross Margin" || metric.label === "Risk Flag"
                            ? "text-amber-700"
                            : "text-slate-900"
                        }`}
                      >
                        {metric.value}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
                  <div className="rounded-3xl bg-slate-950 p-6 text-white shadow-lg">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                          CEO view
                        </p>
                        <h3 className="mt-2 text-xl font-bold md:text-2xl">
                          What needs attention this week
                        </h3>
                      </div>
                      <div className="rounded-full border border-amber-300/30 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">
                        Action needed
                      </div>
                    </div>

                    <div className="mt-5 space-y-3">
                      {[
                        "Reduce discount leakage on low-retention cohorts.",
                        "Push fulfillment efficiency to protect margin expansion.",
                        "Prioritize high-repeat micro-markets for capital deployment.",
                      ].map((item) => (
                        <div key={item} className="flex gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                          <span className="mt-1 h-2 w-2 rounded-full bg-amber-400" />
                          <p>{item}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                      Decision summary
                    </p>
                    <div className="mt-4 space-y-3 text-sm text-slate-700">
                      <div className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-100">
                        Status: runway acceptable but not comfortable.
                      </div>
                      <div className="rounded-2xl bg-amber-50 p-4 ring-1 ring-amber-100">
                        Primary risk: discounting and variable cost drift.
                      </div>
                      <div className="rounded-2xl bg-emerald-50 p-4 ring-1 ring-emerald-100">
                        Recommended move: tighten cohort-level spend rules.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {activeTab === "formula" && (
            <section className="overflow-hidden rounded-4xl border border-slate-900/10 bg-white/90 shadow-[0_20px_60px_rgba(15,23,42,0.12)] backdrop-blur">
              <div className="border-b border-slate-200 bg-linear-to-r from-slate-950 via-slate-900 to-cyan-950 px-6 py-6 text-white md:px-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-300">
                      Formula Library
                    </p>
                    <h2 className="mt-2 text-2xl font-black md:text-3xl">
                      Calculation workspace
                    </h2>
                    <p className="mt-2 max-w-2xl text-sm text-slate-300">
                      Choose a formula card, enter values, and run the backend calculation instantly.
                    </p>
                  </div>

                  <div className="rounded-full border border-cyan-300/40 bg-cyan-400/15 px-4 py-2 text-sm font-semibold text-cyan-200">
                    4 formulas ready
                  </div>
                </div>
              </div>

              <div className="p-6 md:p-8">
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                  {formulaCards}
                </div>

                <div className="mt-6 grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
                  <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-5 shadow-sm">
                    <div className={`rounded-2xl bg-linear-to-r ${formulaConfigs[formulaName].accent} p-4 text-white shadow-lg`}>
                      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-white/80">
                        Selected Formula
                      </p>
                      <h3 className="mt-2 text-xl font-black">{formulaConfigs[formulaName].label}</h3>
                      <p className="mt-2 text-sm text-white/85">{formulaConfigs[formulaName].expression}</p>
                    </div>

                    <div className="mt-5 rounded-2xl bg-white p-4 ring-1 ring-slate-100">
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
                        Inputs
                      </p>
                      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                        {formulaConfigs[formulaName].fields.map((field) => (
                          <label key={field.key} className="flex flex-col gap-2 rounded-2xl bg-slate-50 p-3 ring-1 ring-slate-100">
                            <span className="text-sm font-semibold text-slate-700">{field.label}</span>
                            <input
                              type="number"
                              value={formulaInputs[field.key] ?? field.defaultValue}
                              className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200"
                              onChange={(event) =>
                                setFormulaInputs((prev) => ({
                                  ...prev,
                                  [field.key]: Number(event.target.value),
                                }))
                              }
                            />
                          </label>
                        ))}
                      </div>

                      <button
                        type="button"
                        className="mt-4 inline-flex items-center justify-center rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-slate-800"
                        disabled={formulaLoading}
                        onClick={runFormulaCalculation}
                      >
                        {formulaLoading ? "Calculating..." : "Run Formula"}
                      </button>
                    </div>
                  </div>

                  <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                          Output
                        </p>
                        <h3 className="mt-2 text-xl font-bold text-slate-900">Calculation result</h3>
                      </div>
                      <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                        Backend computed
                      </div>
                    </div>

                    {formulaData ? (
                      <div className="mt-5 space-y-4">
                        <div className="rounded-2xl bg-slate-950 p-4 text-white shadow-lg">
                          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                            Formula expression
                          </p>
                          <p className="mt-2 text-sm text-slate-200">{formulaData.formula_expression}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          {Object.entries(formulaData.result).map(([key, value], index) => (
                            <div
                              key={key}
                              className={`rounded-2xl p-4 ring-1 ${
                                index === 0
                                  ? "bg-orange-50 ring-orange-100"
                                  : index === 1
                                    ? "bg-cyan-50 ring-cyan-100"
                                    : index === 2
                                      ? "bg-emerald-50 ring-emerald-100"
                                      : "bg-fuchsia-50 ring-fuchsia-100"
                              }`}
                            >
                              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
                                {metricTitle(key)}
                              </p>
                              <p className="mt-2 text-2xl font-black text-slate-900">{String(value)}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center">
                        <p className="text-sm font-semibold text-slate-700">Select a formula and run it to see results here.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>

        {error && <p className="mt-4 rounded-xl bg-red-100 p-3 text-red-700">{error}</p>}
      </div>
    </div>
  );
}
