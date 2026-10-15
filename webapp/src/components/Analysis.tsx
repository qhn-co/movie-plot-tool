import type { Analysis as AnalysisData } from "../api";

export default function Analysis({ analysis }: { analysis: AnalysisData }) {
  return (
    <div className="space-y-8 leading-relaxed text-zinc-200">
      <section>
        <h2 className="mb-2 text-lg font-semibold text-amber-400">Synopsis</h2>
        <p className="whitespace-pre-line">{analysis.synopsis}</p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold text-amber-400">Chronologie</h2>
        <ol className="list-decimal space-y-2 pl-5">
          {analysis.timeline.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </section>
      <details className="rounded-lg border border-zinc-800 p-4">
        <summary className="cursor-pointer font-semibold text-amber-400">
          La fin (attention, spoilers)
        </summary>
        <p className="mt-3 whitespace-pre-line">{analysis.ending}</p>
      </details>
      <section>
        <h2 className="mb-2 text-lg font-semibold text-amber-400">Analyse</h2>
        <p className="whitespace-pre-line">{analysis.meta_analysis}</p>
      </section>
    </div>
  );
}
