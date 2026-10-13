import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Hypeframe — Legendary Anime Moments', description: 'Discover, celebrate and save iconic anime moments.' };
export default function RootLayout({children}:{children:React.ReactNode}) {return <html lang="en"><body>{children}</body></html>}
