import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "ClearFinance",
  description: "Your Personal Financial Board of Directors",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">{children}</div>
      </body>
    </html>
  );
}
