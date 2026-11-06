import type { Metadata } from "next";
import { Footer } from "@/components/landing/Footer";
import { LegalPage } from "@/components/legal/LegalPage";
import { terminos } from "@/lib/legal/terminos";

export const metadata: Metadata = {
  title: `${terminos.title} — Koach`,
  description: terminos.description,
  alternates: { canonical: "/terminos" },
  // Borrador pendiente de revisión legal (P-04): no indexar todavía.
  robots: { index: false, follow: true },
};

export default function Page() {
  return (
    <>
      <LegalPage doc={terminos} />
      <Footer />
    </>
  );
}
