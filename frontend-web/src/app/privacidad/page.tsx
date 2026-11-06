import type { Metadata } from "next";
import { Footer } from "@/components/landing/Footer";
import { LegalPage } from "@/components/legal/LegalPage";
import { privacidad } from "@/lib/legal/privacidad";

export const metadata: Metadata = {
  title: `${privacidad.title} — Koach`,
  description: privacidad.description,
  alternates: { canonical: "/privacidad" },
  // Borrador pendiente de revisión legal (P-04, P-05): no indexar todavía.
  robots: { index: false, follow: true },
};

export default function Page() {
  return (
    <>
      <LegalPage doc={privacidad} />
      <Footer />
    </>
  );
}
