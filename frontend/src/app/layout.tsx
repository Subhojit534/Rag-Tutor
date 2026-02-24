import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'RAG Tutor - Academic ERP System',
    description: 'Comprehensive academic web application with AI-powered tutoring',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="bg-gray-50 min-h-screen">
                {children}
            </body>
        </html>
    )
}
