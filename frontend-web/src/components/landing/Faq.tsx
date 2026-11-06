import { FAQ } from "@/lib/content";

export function Faq() {
  return (
    <section
      id="faq"
      aria-labelledby="faq-title"
      className="mx-auto max-w-3xl px-4 py-16"
    >
      <h2 id="faq-title" className="text-center text-3xl font-bold">
        Preguntas frecuentes
      </h2>
      <div className="mt-10 flex flex-col gap-3">
        {FAQ.map((item) => (
          <details
            key={item.question}
            data-testid="faq-item"
            className="group rounded-xl bg-white px-5 py-4 ring-1 ring-dark/10"
          >
            <summary className="flex min-h-6 cursor-pointer list-none items-center justify-between gap-4 font-semibold [&::-webkit-details-marker]:hidden">
              {item.question}
              <span aria-hidden className="text-primary transition group-open:rotate-45">
                +
              </span>
            </summary>
            <p className="mt-3 text-dark/80">{item.answer}</p>
            {item.link && (
              <a
                href={item.link.href}
                className="mt-2 inline-block font-semibold text-primary underline underline-offset-4"
              >
                {item.link.label}
              </a>
            )}
          </details>
        ))}
      </div>
    </section>
  );
}
