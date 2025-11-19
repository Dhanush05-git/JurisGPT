import "./globals.css";
import { Inter } from "next/font/google";
import clsx from "clsx";
import Navbar from "@/components/Navbar";



const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "JurisGPT",
  description: "AI-powered legal information system for Indian laws",
  icons: {
    icon: "/icon.png",
  },
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark:bg-[#0d0d0d]">
      <body
        className={clsx(
          inter.className,
          "min-h-screen text-gray-900 dark:text-gray-100"
        )}
      >
        <div className="flex flex-col items-center w-full">
          <div className="w-full max-w-3xl px-4 py-6">
            <Navbar />
            {children}

          </div>
        </div>
      </body>
    </html>
  );
}
