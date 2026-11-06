import { ChatMockups } from "@/components/landing/ChatMockups";
import { Faq } from "@/components/landing/Faq";
import { Footer } from "@/components/landing/Footer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Leads } from "@/components/landing/Leads";
import { Pricing } from "@/components/landing/Pricing";
import { Problem } from "@/components/landing/Problem";

export default function Home() {
  return (
    <>
      <header className="px-4 py-4">
        <p className="mx-auto max-w-5xl text-xl font-bold text-primary">Koach</p>
      </header>
      <main className="flex-1">
        <Hero />
        <Problem />
        <HowItWorks />
        <ChatMockups />
        <Pricing />
        <Leads />
        <Faq />
      </main>
      <Footer />
    </>
  );
}
