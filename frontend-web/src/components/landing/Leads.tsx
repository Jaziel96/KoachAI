import { LeadForm } from "./LeadForm";

export function Leads() {
  return (
    <section
      id="lista-espera"
      aria-labelledby="lista-espera-title"
      className="mx-auto max-w-3xl px-4 py-16"
    >
      <h2 id="lista-espera-title" className="text-center text-3xl font-bold">
        ¿Aún no estás listo? Te avisamos
      </h2>
      <p className="mx-auto mt-3 max-w-md text-center text-dark/75">
        Déjanos tus datos y te escribimos cuando Koach esté disponible.
      </p>
      <div className="mt-8">
        <LeadForm />
      </div>
    </section>
  );
}
