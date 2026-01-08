import './globals.css'
import Providers from '@/components/Providers'

export const metadata = {
  title: 'Invoice Generator - Topmate',
  description: 'GST-compliant invoice generator',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
