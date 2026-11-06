import { PROBLEMS } from "@/lib/content";

export function Problem() {
  return (
    <section
      id="problema"
      aria-labelledby="problema-title"
      className="mx-auto max-w-5xl px-4 py-16"
    >
      <h2 id="problema-title" className="text-center text-3xl font-bold">
        Cuidarte no debería ser tan complicado
      </h2>
      <ul className="mt-10 grid gap-6 md:grid-cols-3">
        {PROBLEMS.map((p) => (
          <li key={p.title} className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-dark/10">
            <h3 className="text-lg font-semibold">{p.title}</h3>
            <p className="mt-2 text-dark/75">{p.body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
