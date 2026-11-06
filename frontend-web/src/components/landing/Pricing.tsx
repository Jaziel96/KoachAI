import { FOUNDER_BENEFITS } from "@/lib/content";
import { CtaButton } from "./CtaButton";

export function Pricing() {
  return (
    <section
      id="precios"
      aria-labelledby="precios-title"
      className="mx-auto max-w-5xl px-4 py-16"
    >
      <h2 id="precios-title" className="text-center text-3xl font-bold">
        Precio Founder
      </h2>
      <div className="mx-auto mt-10 max-w-md rounded-3xl bg-white p-8 shadow-md ring-2 ring-primary">
        <span className="inline-block rounded-full bg-accent px-3 py-1 text-sm font-semibold text-dark">
          Primeros 50 usuarios
        </span>
        <p className="mt-4 flex items-baseline gap-1">
          <span className="text-5xl font-bold">$149</span>
          <span className="text-dark/70">MXN / mes</span>
        </p>
        <p className="mt-1 text-sm text-dark/70">Precio congelado de por vida.</p>
        <ul className="mt-6 flex flex-col gap-2">
          {FOUNDER_BENEFITS.map((b) => (
            <li key={b} className="flex gap-2">
              <span aria-hidden className="text-primary">✓</span>
              {b}
            </li>
          ))}
        </ul>
        <div className="mt-8 flex justify-center">
          <CtaButton label="Quiero ser Founder" />
        </div>
      </div>
    </section>
  );
}
