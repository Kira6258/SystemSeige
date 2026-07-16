import type { ReactNode } from "react";
import { Outfit } from "next/font/google";
import { ThemeProvider } from "@/components/ThemeProvider";
import Nav from "@/components/Nav";
import "./globals.css";

const outfit = Outfit({ subsets: ["latin"] });

export const metadata = {
  title: "ClearFinance | AI Financial Intelligence",
  description: "Your AI-powered Personal Financial Board of Directors",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <body className={outfit.className}>
        <ThemeProvider>
          <div className="background-glow"></div>
          <Nav>{children}</Nav>
        </ThemeProvider>
      </body>
    </html>
  );
}
