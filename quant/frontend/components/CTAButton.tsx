export function CTAButton({ 
  variant = 'primary',
  children,
  href,
}: {
  variant?: 'primary' | 'success'
  children: React.ReactNode
  href: string
}) {
  const styles = {
    primary: 'bg-purple-600 text-white hover:bg-purple-700',
    success: 'bg-green-600 text-white hover:bg-green-700',
  }

  return (
    <a href={href} className={`${styles[variant]} px-6 py-2.5 rounded font-bold transition inline-block`}>
      {children}
    </a>
  )
}
