import type { Metadata } from "next";
import { Footer } from "@/components/landing/Footer";
import { LegalPage } from "@/components/legal/LegalPage";
import { disclaimer } from "@/lib/legal/disclaimer";

export const metadata: Metadata = {
  title: `${disclaimer.title} — Koach`,
  description: disclaimer.description,
  alternates: { canonical: "/disclaimer-medico" },
  // Borrador pendiente de revisión legal: no indexar todavía.
  robots: { index: false, follow: true },
};

export default function Page() {
  return (
    <>
      <LegalPage doc={disclaimer} />
      <Footer />
    </>
  );
}
