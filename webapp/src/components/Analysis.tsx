import type { ReactNode } from "react";
import type { Analysis as AnalysisData } from "../api";

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="mb-2 text-lg font-semibold text-amber-400">{title}</h2>
      {children}
    </section>
  );
}

// Les repères de mémoire passent avant l'intrigue : on reconnaît un film à ses scènes.
// La fin reste repliée pour qui ne l'a pas vu.
export default function Analysis({ analysis }: { analysis: AnalysisData }) {
  return (
    <div className="space-y-8 leading-relaxed text-zinc-200">
      <Section title="Ça te dit quelque chose ?">
        <ul className="list-disc space-y-2 pl-5">
          {analysis.memory_cues.map((cue, i) => (
            <li key={i}>{cue}</li>
          ))}
        </ul>
      </Section>
      <Section title="Synopsis">
        <p className="whitespace-pre-line">{analysis.synopsis}</p>
      </Section>
      <Section title="Chronologie">
        <ol className="list-decimal space-y-2 pl-5">
          {analysis.timeline.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </Section>
      <details className="rounded-lg border border-zinc-800 p-4">
        <summary className="cursor-pointer font-semibold text-amber-400">
          La fin (attention, spoilers)
        </summary>
        <p className="mt-3 whitespace-pre-line">{analysis.ending}</p>
      </details>
      <Section title="Contexte">
        <p className="whitespace-pre-line">{analysis.context}</p>
      </Section>
    </div>
  );
}
