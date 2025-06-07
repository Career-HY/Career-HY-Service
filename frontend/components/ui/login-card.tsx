import Image from 'next/image'
import { ReactNode } from 'react'

interface LoginCardProps {
  title: string
  subtitle1: string
  subtitle2: string
  description: string
  children: ReactNode
  bottomLink: ReactNode
}

export default function LoginCard({
  title,
  subtitle1,
  subtitle2,
  description,
  children,
  bottomLink,
}: LoginCardProps) {
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Image
              src="/images/logos/careerhy.png"
              alt="Career-HY"
              width={64}
              height={64}
              className="object-contain"
            />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600 mb-1">{subtitle1}</p>
          <p className="text-gray-600 font-medium">{subtitle2}</p>
          <p className="text-sm text-gray-500 mt-2">{description}</p>
        </div>

        {children}

        <div className="mt-6 text-center">{bottomLink}</div>
      </div>
    </div>
  )
}
