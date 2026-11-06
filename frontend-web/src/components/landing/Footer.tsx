import { LEGAL_LINKS } from "@/lib/content";

export function Footer() {
  return (
    <footer className="mt-8 bg-dark px-4 py-10 text-sm text-white/80">
      <div className="mx-auto flex max-w-5xl flex-col gap-4">
        <p className="text-lg font-bold text-primary">Koach</p>
        <nav aria-label="Legal" className="flex flex-wrap gap-x-6 gap-y-2">
          {LEGAL_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="underline-offset-4 hover:underline">
              {l.label}
            </a>
          ))}
        </nav>
        <p className="max-w-2xl text-white/60">
          Koach ofrece orientación alimentaria y acompañamiento de hábitos. No es un
          servicio médico ni sustituye la consulta con un profesional de la salud.
        </p>
        <p className="text-white/60">© 2026 Koach</p>
      </div>
    </footer>
  );
}
