import { STEPS } from "@/lib/content";

export function HowItWorks() {
  return (
    <section
      id="como-funciona"
      aria-labelledby="como-funciona-title"
      className="mx-auto max-w-5xl px-4 py-16"
    >
      <h2 id="como-funciona-title" className="text-center text-3xl font-bold">
        Así funciona
      </h2>
      <ol className="mt-10 grid gap-6 md:grid-cols-3">
        {STEPS.map((s, i) => (
          <li key={s.title} className="flex flex-col gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary font-bold text-dark">
              {i + 1}
            </span>
            <h3 className="text-lg font-semibold">{s.title}</h3>
            <p className="text-dark/75">{s.body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
