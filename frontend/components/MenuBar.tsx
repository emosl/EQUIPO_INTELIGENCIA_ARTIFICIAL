"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, BookOpen, Menu, X, ChevronDown, User, LogOut } from "lucide-react"
import { useState, useRef, useEffect } from "react"
import { useAuth } from "./AuthContext"

const navigation = [
  { name: "Results", href: "/results", icon: BarChart3 },
  { name: "User Manual", href: "/user-manual", icon: BookOpen },
]

export default function MenuBar() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [sessionDropdownOpen, setSessionDropdownOpen] = useState(false)
  const { user, logout } = useAuth()
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setSessionDropdownOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  // Don't render the menu bar on the login page
  if (pathname === "/login") {
    return null
  }

  // Don't render if not authenticated
  if (!user) {
    return null
  }

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">Dashboard</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? "bg-primary-100 text-primary-700 border-b-2 border-primary-600"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {item.name}
                </Link>
              )
            })}

            {/* Session Dropdown in Desktop Navigation */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setSessionDropdownOpen(!sessionDropdownOpen)}
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
              >
                {user.avatar ? (
                  <img src={user.avatar || "/placeholder.svg"} alt={user.name} className="h-6 w-6 rounded-full mr-2" />
                ) : (
                  <div className="h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center mr-2">
                    <User className="h-3 w-3 text-primary-600" />
                  </div>
                )}
                <span className="mr-1">{user.name}</span>
                <ChevronDown className="h-4 w-4" />
              </button>

              {sessionDropdownOpen && (
                <div className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50">
                  <div className="py-1" role="menu" aria-orientation="vertical">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user.name}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                      <p className="text-xs text-gray-500 mt-1">Role: {user.role}</p>
                    </div>
                    <button
                      onClick={() => {
                        logout()
                        setSessionDropdownOpen(false)
                      }}
                      className="flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                    >
                      <LogOut className="mr-3 h-4 w-4 text-gray-500" />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none focus:text-gray-900 p-2"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Link>
                )
              })}

              {/* Session info in Mobile Navigation */}
              <div className="border-t border-gray-200 pt-3 mt-3">
                <div className="px-3 py-2">
                  <div className="flex items-center">
                    {user.avatar ? (
                      <img
                        src={user.avatar || "/placeholder.svg"}
                        alt={user.name}
                        className="h-8 w-8 rounded-full mr-3"
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                        <User className="h-4 w-4 text-primary-600" />
                      </div>
                    )}
                    <div>
                      <p className="text-base font-medium text-gray-900">{user.name}</p>
                      <p className="text-sm text-gray-500">{user.role}</p>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => {
                    logout()
                    setMobileMenuOpen(false)
                  }}
                  className="flex w-full items-center px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                >
                  <LogOut className="mr-3 h-5 w-5 text-gray-500" />
                  Sign out
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
