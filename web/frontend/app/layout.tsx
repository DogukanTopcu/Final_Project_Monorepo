import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { SideNav } from "@/components/SideNav";
import { HostStatusBar } from "@/components/HostStatusBar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Thesis Experiment Platform",
  description: "SLM/LLM experiment runner and results dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-zinc-50 text-zinc-900`}>
        <Providers>
          <div className="flex min-h-screen">
            <SideNav />
            <div className="flex flex-1 flex-col overflow-hidden">
              <HostStatusBar />
              <main className="flex-1 overflow-auto p-8">{children}</main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
