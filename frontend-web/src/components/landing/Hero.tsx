import { CtaButton } from "./CtaButton";

export function Hero() {
  return (
    <section
      id="inicio"
      aria-labelledby="hero-title"
      className="mx-auto flex max-w-3xl flex-col items-center gap-6 px-4 pb-16 pt-12 text-center sm:pt-20"
    >
      <h1
        id="hero-title"
        className="text-4xl font-bold tracking-tight text-dark sm:text-5xl"
      >
        Tu coach de hábitos saludables, <span className="text-primary">en tu WhatsApp</span>
      </h1>
      <p className="max-w-xl text-lg text-dark/80">
        Koach te da orientación alimentaria con comida mexicana de verdad, parte
        de lo que ya tienes en casa y te escribe primero para acompañarte cada
        día. Sin apps nuevas.
      </p>
      <CtaButton />
      <p className="text-sm text-dark/60">
        Orientación alimentaria y acompañamiento. No es un servicio médico.
      </p>
    </section>
  );
}
