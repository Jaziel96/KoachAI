import Link from "next/link";
import { formatLegalDate, type LegalDocument } from "@/lib/legal/types";

export function LegalPage({ doc }: { doc: LegalDocument }) {
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
      <Link href="/" className="text-sm font-semibold text-primary underline-offset-4 hover:underline">
        ← Volver a Koach
      </Link>

      <article className="mt-6">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{doc.title}</h1>
        <p className="mt-2 text-sm text-dark/70">
          Versión {doc.version} · Última actualización:{" "}
          <time dateTime={doc.updatedAt}>{formatLegalDate(doc.updatedAt)}</time>
        </p>

        <p
          role="note"
          data-testid="legal-draft-notice"
          className="mt-6 rounded-xl bg-accent/20 px-4 py-3 text-sm ring-1 ring-accent"
        >
          Documento en revisión legal. Esta es una versión preliminar y puede cambiar.
        </p>

        <nav aria-label="Contenido" className="mt-8 rounded-xl bg-white p-4 ring-1 ring-dark/10">
          <p className="font-semibold">Contenido</p>
          <ol className="mt-2 flex list-decimal flex-col gap-1 pl-5 text-sm">
            {doc.sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`} className="underline-offset-4 hover:underline">
                  {s.title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        {doc.sections.map((s) => (
          <section key={s.id} id={s.id} aria-labelledby={`${s.id}-title`} className="mt-10 scroll-mt-6">
            <h2 id={`${s.id}-title`} className="text-xl font-bold">
              {s.title}
            </h2>
            {s.paragraphs?.map((p) => (
              <p key={p} className="mt-3 text-dark/85">
                {p}
              </p>
            ))}
            {s.items && (
              <ul className="mt-3 flex list-disc flex-col gap-1 pl-5 text-dark/85">
                {s.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </article>
    </main>
  );
}
