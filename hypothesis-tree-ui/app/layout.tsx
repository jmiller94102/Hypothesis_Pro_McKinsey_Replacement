import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HypothesisTree Pro",
  description: "Strategic Decision Support with MECE Hypothesis Trees",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
