import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Koach — tu coach de hábitos saludables por WhatsApp",
  description:
    "Koach te acompaña por WhatsApp con orientación alimentaria y hábitos saludables.",
  metadataBase: new URL("https://koach.mx"),
  openGraph: { locale: "es_MX", type: "website", siteName: "Koach" },
};

export const viewport: Viewport = {
  themeColor: "#10b981",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es-MX"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
