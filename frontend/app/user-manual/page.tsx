import { BookOpen, ChevronRight, Download, Search, HelpCircle } from "lucide-react"

export default function UserManualPage() {
  const sections = [
    {
      title: "Getting Started",
      items: ["Account Setup", "Dashboard Overview", "Navigation Basics", "First Steps"],
    },
    {
      title: "Results & Analytics",
      items: ["Understanding Metrics", "Reading Charts", "Exporting Data", "Custom Reports"],
    },
    {
      title: "Historic Data",
      items: ["Accessing Historic Records", "Filtering Data", "Date Range Selection", "Data Export Options"],
    },
    {
      title: "Advanced Features",
      items: ["API Integration", "Custom Dashboards", "Automated Reports", "User Management"],
    },
  ]

  const faqs = [
    {
      question: "How do I export my data?",
      answer:
        "You can export data from any page by clicking the Export button in the top-right corner. Choose your preferred format (CSV, PDF, or Excel).",
    },
    {
      question: "Can I customize the dashboard?",
      answer:
        "Yes, you can customize your dashboard by rearranging widgets, adding new metrics, and creating custom views through the settings panel.",
    },
    {
      question: "How often is the data updated?",
      answer:
        "Data is updated in real-time for most metrics. Historic data is processed every hour to ensure accuracy and consistency.",
    },
  ]

  return (
    <div className="content-wrapper">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <h1 className="page-title mb-4 sm:mb-0">User Manual</h1>
        <div className="flex space-x-3">
          <button className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
            <Search className="h-4 w-4 mr-2" />
            Search
          </button>
          <button className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-primary-700">
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <div className="card sticky top-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              Table of Contents
            </h3>
            <nav className="space-y-4">
              {sections.map((section, sectionIndex) => (
                <div key={sectionIndex}>
                  <h4 className="font-medium text-gray-900 mb-2">{section.title}</h4>
                  <ul className="space-y-1 ml-4">
                    {section.items.map((item, itemIndex) => (
                      <li key={itemIndex}>
                        <a
                          href={`#${item.toLowerCase().replace(/\s+/g, "-")}`}
                          className="text-sm text-gray-600 hover:text-primary-600 flex items-center group"
                        >
                          <ChevronRight className="h-3 w-3 mr-1 group-hover:translate-x-1 transition-transform" />
                          {item}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </nav>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-8">
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to the User Manual</h2>
            <p className="text-gray-600 mb-6">
              This comprehensive guide will help you navigate and make the most of your dashboard application. Whether
              you're a new user or looking to explore advanced features, you'll find everything you need here.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start">
                <HelpCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-blue-900 mb-1">Need Help?</h4>
                  <p className="text-sm text-blue-700">
                    If you can't find what you're looking for, contact our support team at support@dashboard.com
                  </p>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Start Guide</h3>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-sm font-medium text-primary-600">1</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Explore the Dashboard</h4>
                  <p className="text-sm text-gray-600">
                    Start by familiarizing yourself with the main dashboard and navigation menu.
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-sm font-medium text-primary-600">2</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Check Your Results</h4>
                  <p className="text-sm text-gray-600">
                    Visit the Results page to view your current metrics and performance data.
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-sm font-medium text-primary-600">3</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Review Historic Data</h4>
                  <p className="text-sm text-gray-600">
                    Use the Historic page to analyze trends and patterns over time.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Frequently Asked Questions</h3>
            <div className="space-y-6">
              {faqs.map((faq, index) => (
                <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <h4 className="font-medium text-gray-900 mb-2">{faq.question}</h4>
                  <p className="text-sm text-gray-600">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Additional Resources</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <a
                href="#"
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <BookOpen className="h-8 w-8 text-primary-600 mr-4" />
                <div>
                  <h4 className="font-medium text-gray-900">Video Tutorials</h4>
                  <p className="text-sm text-gray-600">Step-by-step video guides</p>
                </div>
              </a>
              <a
                href="#"
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <HelpCircle className="h-8 w-8 text-primary-600 mr-4" />
                <div>
                  <h4 className="font-medium text-gray-900">Support Center</h4>
                  <p className="text-sm text-gray-600">Get help from our team</p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
