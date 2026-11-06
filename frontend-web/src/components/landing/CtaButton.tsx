import { buildWhatsappUrl } from "@/lib/whatsapp";

export function CtaButton({ label = "Empieza por WhatsApp" }: { label?: string }) {
  return (
    <a
      href={buildWhatsappUrl()}
      target="_blank"
      rel="noopener noreferrer"
      data-testid="cta-whatsapp"
      className="inline-flex min-h-12 items-center justify-center rounded-full bg-primary px-6 py-3 text-base font-semibold text-dark shadow-sm transition hover:brightness-95 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-dark"
    >
      {label}
    </a>
  );
}
