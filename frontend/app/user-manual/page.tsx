// src/pages/UserManualPage.tsx

"use client";

import {
  BookOpen,
  ChevronRight,
  Download,
  Search,
  HelpCircle,
} from "lucide-react";

export default function UserManualPage() {
  const sections = [
    {
      title: "Getting Started",
      items: [
        "What Is Kalman Filtering?",
        "Kalman Filter Variants Explained",
        "Understanding Your Results",
        "What You Can Do With Results",
      ],
    },
    {
      title: "Using the Platform",
      items: [
        "Getting Started - Account & Login",
        "Managing Your Patients",
        "Adding New Patients",
        "Uploading Your EEG Data",
        "Setting Up Your Analysis",
        "Understanding Channel Selection",
        "Running Your Analysis",
      ],
    },
    {
      title: "Viewing Results",
      items: ["Viewing Your Results", "Understanding Your Brain Wave Graphs"],
    },
    {
      title: "Advanced Features",
      items: [
        "Saving and Sharing Your Results",
        "Advanced Features and Customization",
        "Getting Help and Best Practices",
      ],
    },
  ];

  return (
    <div className="content-wrapper px-6 py-8">
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
        {/* Table of Contents Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-8 p-6 border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              Table of Contents
            </h3>
            <nav className="space-y-6">
              {sections.map((section, sectionIndex) => (
                <div key={sectionIndex}>
                  <h4 className="font-medium text-gray-900 mb-2">
                    {section.title}
                  </h4>
                  <ul className="space-y-1 ml-4">
                    {section.items.map((item, itemIndex) => (
                      <li key={itemIndex}>
                        <a
                          href={`#${item
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, "-")}`}
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

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-12">
          {/* Section: What Is Kalman Filtering? */}
          <section id="what-is-kalman-filtering">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              What Is Kalman Filtering?
            </h2>
            <p className="text-gray-600 mb-4">
              Kalman filtering is a powerful mathematical technique that helps
              clean up noisy data by making smart predictions about what the
              "true" signal should look like. Think of it as having a very
              sophisticated noise-canceling system for your brain wave data.
            </p>
            <p className="text-gray-600 mb-4">
              When recording EEG (brain wave) data, the signals often contain
              unwanted noise from muscle movements, electrical interference, or
              environmental factors. Kalman filters work by continuously
              comparing what they expect to see with what they actually observe,
              then making educated guesses about the real brain activity
              underneath all that noise.
            </p>
            <p className="text-gray-600">
              Our platform applies different types of Kalman filters to your EEG
              data, allowing you to compare which approach works best for your
              specific recordings and research needs. This user manual walks you
              through how our dashboard lets you run various Kalman filter
              variants, view results, and export data.
            </p>
          </section>

          {/* Section: Kalman Filter Variants Explained */}
          <section id="kalman-filter-variants-explained">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Kalman Filter Variants Explained
            </h2>
            <p className="text-gray-600 mb-6">
              Our platform offers nine different Kalman filter variants, each
              using a unique mathematical approach to process your EEG data.
              These variants are built on three main algorithmic foundations
              (Potter, Carlson, and Bierman) combined with three different
              mathematical techniques (Gram-Schmidt, Givens, and Householder).
              Here's what makes each combination special:
            </p>

            {/* Potter Method Variants */}
            <div className="border border-gray-300 rounded-lg p-6 mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">P</span>
                </div>
                Potter Method Variants
              </h3>
              <p className="text-gray-700 mb-4 text-sm">
                The Potter method is known for its classical approach and
                exceptional reliability. It's considered the gold standard for
                general-purpose EEG analysis and consistently produces stable,
                interpretable results across different types of brain wave data.
              </p>

              <div className="space-y-4">
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">1</span>
                    </div>
                    Potter - Gram-Schmidt
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Beginners, general-purpose
                    analysis, establishing baseline results
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Uses the classical Gram-Schmidt orthogonalization process,
                    which systematically removes correlations between different
                    signal components. This creates a very stable filtering
                    process that's forgiving of minor data quality issues.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Highly reliable, well-tested,
                      produces consistent results, good documentation in
                      literature
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Standard EEG recordings,
                      research requiring reproducible results, initial analysis
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">2</span>
                    </div>
                    Potter - Givens
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Noisy data, high-precision
                    requirements, challenging recordings
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Employs Givens rotations, which use precise mathematical
                    rotations to maintain numerical stability. This approach is
                    particularly effective when dealing with data that has
                    significant noise or when you need very accurate results.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Superior numerical stability,
                      handles noisy data well, maintains precision over long
                      recordings
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Clinical recordings with
                      artifacts, long-duration EEG sessions, research requiring
                      high accuracy
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">3</span>
                    </div>
                    Potter - Householder
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Maximum precision, research
                    applications, critical analysis
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Uses advanced Householder transformations for the highest
                    possible mathematical precision. This is the most accurate
                    Potter variant but requires more computational time.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Highest accuracy, excellent
                      for research, superior mathematical properties
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Research publications,
                      critical medical analysis, when accuracy is more important
                      than speed
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Carlson Method Variants */}
            <div className="border border-gray-300 rounded-lg p-6 mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">C</span>
                </div>
                Carlson Method Variants
              </h3>
              <p className="text-gray-700 mb-4 text-sm">
                The Carlson method prioritizes computational efficiency while
                maintaining good accuracy. These variants are designed for
                situations where you need to process large amounts of EEG data
                quickly without sacrificing too much precision.
              </p>

              <div className="space-y-4">
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">1</span>
                    </div>
                    Carlson - Gram-Schmidt
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Large datasets, routine analysis,
                    time-sensitive processing
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Combines Carlson's efficient algorithms with Gram-Schmidt
                    orthogonalization. This creates a fast, reliable filter
                    that's perfect for processing multiple EEG sessions quickly.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Fast processing, good
                      accuracy, handles large files well, resource-efficient
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Batch processing, large
                      studies, routine clinical analysis, time-constrained
                      projects
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">2</span>
                    </div>
                    Carlson - Givens
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Balanced speed and accuracy,
                    everyday research, moderate noise levels
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Balances computational speed with numerical stability using
                    Givens rotations. This variant provides the best compromise
                    between processing time and result quality.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Optimal speed-accuracy
                      balance, good stability, versatile performance
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Standard research
                      workflows, moderate-sized datasets, everyday EEG analysis
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">3</span>
                    </div>
                    Carlson - Householder
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> High-throughput research,
                    accurate batch processing, academic studies
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Combines Carlson's efficiency with Householder's precision.
                    Excellent choice when you need both speed and accuracy for
                    research applications.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Efficient yet precise, good
                      for research, maintains quality at speed
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Academic research,
                      large-scale studies, professional EEG analysis services
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bierman Method Variants */}
            <div className="border border-gray-300 rounded-lg p-6 mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">B</span>
                </div>
                Bierman Method Variants
              </h3>
              <p className="text-gray-700 mb-4 text-sm">
                The Bierman method uses square-root filtering for enhanced
                numerical stability and robustness. These variants are
                specifically designed to handle challenging datasets with
                significant noise, artifacts, or numerical precision
                requirements.
              </p>

              <div className="space-y-4">
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">1</span>
                    </div>
                    Bierman - Gram-Schmidt
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Long recordings, numerical
                    stability, accumulated error prevention
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Uses square-root filtering with Gram-Schmidt
                    orthogonalization to prevent numerical errors from
                    accumulating over time. Particularly valuable for long EEG
                    recordings where stability is crucial.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Excellent numerical stability,
                      prevents error accumulation, robust over time
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Long-duration
                      recordings, sleep studies, continuous monitoring
                      applications
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">2</span>
                    </div>
                    Bierman - Givens
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Challenging datasets, significant
                    artifacts, clinical recordings
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    Combines square-root stability with Givens rotation
                    precision. This creates the most robust variant for dealing
                    with difficult EEG data that contains significant noise or
                    artifacts.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Maximum robustness, handles
                      artifacts well, excellent for poor-quality data
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Clinical environments,
                      pediatric recordings, data with movement artifacts
                    </p>
                  </div>
                </div>

                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                      <span className="text-gray-700 font-bold text-xs">3</span>
                    </div>
                    Bierman - Householder
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    <strong>Best for:</strong> Most challenging analyses,
                    critical applications, maximum precision needed
                  </p>
                  <p className="text-gray-600 text-sm mb-2">
                    The most mathematically robust option available, combining
                    square-root filtering with advanced Householder
                    transformations. This is your best choice for the most
                    challenging or critical EEG analysis tasks.
                  </p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <p className="text-gray-700 text-xs">
                      <strong>Strengths:</strong> Ultimate mathematical
                      robustness, highest precision available, handles any data
                      quality
                    </p>
                    <p className="text-gray-700 text-xs mt-1">
                      <strong>Best suited for:</strong> Critical medical
                      decisions, challenging research problems, when only the
                      best results are acceptable
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Selection Guide */}
            <div className="border border-gray-300 rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Quick Selection Guide
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    If you're new to EEG analysis
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    Start with <strong>Potter - Gram-Schmidt</strong>
                  </p>
                  <p className="text-gray-600 text-xs">
                    Reliable, well-documented, and produces good results for
                    most data types
                  </p>
                </div>
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    If you have noisy or challenging data
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    Try <strong>Bierman - Givens</strong>
                  </p>
                  <p className="text-gray-600 text-xs">
                    Specifically designed to handle artifacts and poor signal
                    quality
                  </p>
                </div>
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    If you need to process large datasets quickly
                  </h4>
                  <p className="text-gray-700 text-sm mb-2">
                    Choose <strong>Carlson - Gram-Schmidt</strong>
                  </p>
                  <p className="text-gray-600 text-xs">
                    Optimized for speed while maintaining good accuracy
                  </p>
                </div>
              </div>
              <div className="mt-4 border border-gray-300 rounded-lg p-4">
                <p className="text-gray-700 text-sm">
                  <strong>Pro tip:</strong> You can run multiple algorithms on
                  the same data and compare the results. This helps you
                  understand which approach works best for your specific type of
                  EEG recordings and research questions.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Understanding Your Results */}
          <section id="understanding-your-results">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Understanding Your Results
            </h2>
            <p className="text-gray-600 mb-6">
              After your Kalman analysis finishes, the system creates several
              types of results that help you understand how the filtering
              improved your EEG data. Think of these as different ways to look
              at the same information - like viewing a photograph, reading its
              description, and seeing its color histogram.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="border border-gray-300 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-sm">📊</span>
                  </div>
                  <h3 className="font-semibold text-gray-900">Visual Graphs</h3>
                </div>
                <p className="text-gray-700 text-sm">
                  Easy-to-read charts that show how your brain waves changed
                  before and after filtering. Perfect for presentations and
                  quick insights.
                </p>
              </div>

              <div className="border border-gray-300 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-sm">🔢</span>
                  </div>
                  <h3 className="font-semibold text-gray-900">
                    Raw Data Files
                  </h3>
                </div>
                <p className="text-gray-700 text-sm">
                  Detailed numerical data you can download and analyze in Excel,
                  SPSS, or other statistical software for deeper research.
                </p>
              </div>

              <div className="border border-gray-300 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-sm">🔍</span>
                  </div>
                  <h3 className="font-semibold text-gray-900">
                    Frequency Analysis
                  </h3>
                </div>
                <p className="text-gray-700 text-sm">
                  Detailed breakdown of brain wave frequencies (alpha, beta,
                  theta, etc.) showing which patterns are strongest in your
                  data.
                </p>
              </div>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">
                What Each Result Type Shows You:
              </h4>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-gray-700 text-xs font-bold">O</span>
                  </div>
                  <div>
                    <p className="text-gray-700 text-sm">
                      <strong>Original:</strong> Your raw EEG data exactly as
                      recorded, including all noise and artifacts
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-gray-700 text-xs font-bold">A</span>
                  </div>
                  <div>
                    <p className="text-gray-700 text-sm">
                      <strong>All:</strong> The cleaned, filtered version
                      combining information from all your EEG channels
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-gray-700 text-xs font-bold">W</span>
                  </div>
                  <div>
                    <p className="text-gray-700 text-sm">
                      <strong>WC (Winning Combination):</strong> Results from
                      only the channels you selected as important
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-gray-700 text-xs font-bold">N</span>
                  </div>
                  <div>
                    <p className="text-gray-700 text-sm">
                      <strong>NWC (Non-Winning Combination):</strong> Results
                      from the channels you didn't select
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section: What You Can Do With Results */}
          <section id="what-you-can-do-with-results">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              What You Can Do With Results
            </h2>
            <p className="text-gray-600 mb-6">
              Once your analysis is complete, you have several ways to explore
              and use your results. Here's what's available and how each option
              can help your research:
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <span className="text-2xl mr-3">📈</span>
                  View Interactive Graphs
                </h3>
                <p className="text-gray-700 mb-3">
                  See your brain wave patterns in easy-to-understand charts
                  right on your screen. These graphs show you immediately how
                  well the filtering worked.
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded p-3">
                  <p className="text-gray-700 text-sm">
                    <strong>Perfect for:</strong> Quick assessment, sharing with
                    colleagues, presentations, getting immediate insights about
                    data quality
                  </p>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <span className="text-2xl mr-3">📥</span>
                  Download Data Files
                </h3>
                <p className="text-gray-700 mb-3">
                  Export your filtered data as spreadsheet files that you can
                  open in Excel, import into statistical software, or share with
                  other researchers.
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded p-3">
                  <p className="text-gray-700 text-sm">
                    <strong>Perfect for:</strong> Statistical analysis, creating
                    custom graphs, research publications, backup copies,
                    detailed data exploration
                  </p>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <span className="text-2xl mr-3">🔍</span>
                  Compare Different Algorithms
                </h3>
                <p className="text-gray-700 mb-3">
                  Run the same data through multiple filtering approaches and
                  see which one works best for your specific research needs.
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded p-3">
                  <p className="text-gray-700 text-sm">
                    <strong>Perfect for:</strong> Method validation, finding
                    optimal settings, research methodology, quality assessment
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Section: Getting Started - Account & Login */}
          <section id="getting-started-account-&-login">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Getting Started - Account & Login
            </h2>
            <p className="text-gray-600 mb-6">
              Before you can analyze your EEG data, you'll need to create an
              account and log in. This keeps your data secure and organized.
              Don't worry - the process is straightforward and only takes a few
              minutes.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                  Creating Your Account
                </h3>
                <div className="space-y-3">
                  <p className="text-gray-700">
                    Visit the registration page and fill in your basic
                    information. You'll need to provide:
                  </p>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <ul className="text-gray-700 text-sm space-y-2">
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-gray-400 rounded-full mr-3"></span>
                        <strong>Your name:</strong> So we know who you are
                      </li>
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-gray-400 rounded-full mr-3"></span>
                        <strong>Email address:</strong> This will be your
                        username for logging in
                      </li>
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-gray-400 rounded-full mr-3"></span>
                        <strong>Password:</strong> Choose something secure that
                        you'll remember
                      </li>
                    </ul>
                  </div>
                  <p className="text-gray-700 text-sm">
                    Click "Sign Up" when you're done, and your account will be
                    ready to use immediately.
                  </p>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                  Logging In
                </h3>
                <div className="space-y-3">
                  <p className="text-gray-700">
                    Once you have an account, simply enter your email and
                    password on the login page. The system will remember you're
                    logged in for convenience.
                  </p>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <p className="text-gray-700 text-sm">
                      <strong>Security note:</strong> Your login session stays
                      active so you don't have to sign in every time you visit.
                      If you're using a shared computer, remember to log out
                      when you're finished.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                  Ready to Analyze
                </h3>
                <p className="text-gray-700">
                  After logging in successfully, you'll be taken to your
                  personal dashboard where you can start organizing patients and
                  analyzing EEG data right away.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Managing Your Patients */}
          <section id="managing-your-patients">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Managing Your Patients
            </h2>
            <p className="text-gray-600 mb-6">
              The platform organizes all your EEG data by patient, making it
              easy to keep track of multiple subjects and see how their brain
              patterns change over time. Think of it like having a digital
              filing cabinet where each patient has their own folder.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="border border-gray-300 rounded-lg p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Selecting an Existing Patient
                </h3>
                <p className="text-gray-700 mb-3 text-sm">
                  Click "Select Patient" on your dashboard to see everyone
                  you've worked with before. You can search by name or browse
                  the list to find who you're looking for.
                </p>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-700 text-xs">
                    <strong>Tip:</strong> The list shows when you last worked
                    with each patient, making it easy to pick up where you left
                    off.
                  </p>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Why Patient Organization Matters
                </h3>
                <p className="text-gray-700 mb-3 text-sm">
                  Keeping data organized by patient helps you track progress
                  over time, compare different sessions, and maintain research
                  integrity.
                </p>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-700 text-xs">
                    <strong>Benefits:</strong> Easy data comparison, better
                    research organization, simplified reporting
                  </p>
                </div>
              </div>
            </div>

            <div className="border border-gray-300 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-gray-700 mb-2 flex items-center">
                <span className="text-lg mr-2">💡</span>
                How Patient Selection Works
              </h4>
              <p className="text-gray-700 text-sm">
                Once you choose a patient, everything you do - uploading new EEG
                sessions, running analyses, viewing results - will be connected
                to that person until you select someone else. This keeps your
                work organized and prevents accidentally mixing up data between
                different subjects.
              </p>
            </div>
          </section>

          {/* Section: Adding New Patients */}
          <section id="adding-new-patients">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Adding New Patients
            </h2>
            <p className="text-gray-600 mb-6">
              When you start working with a new research subject or patient,
              you'll need to create their profile in the system. This only takes
              a minute and helps keep all their EEG data properly organized and
              identifiable.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">👤</span>
                Required Patient Information
              </h3>
              <p className="text-gray-700 mb-4">
                To create a new patient profile, you'll need to provide some
                basic demographic information:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Personal Details
                    </h4>
                    <ul className="text-gray-700 text-sm space-y-1">
                      <li>• First Name</li>
                      <li>• Father's Surname (last name from father's side)</li>
                      <li>• Mother's Surname (last name from mother's side)</li>
                    </ul>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Demographics
                    </h4>
                    <ul className="text-gray-700 text-sm space-y-1">
                      <li>• Birth Date</li>
                      <li>• Sex/Gender</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">✅</span>
                  Quick Setup Process
                </h4>
                <ol className="text-gray-700 text-sm space-y-1 list-decimal list-inside">
                  <li>
                    Click "➕ Create New Patient" in the patient selection
                    window
                  </li>
                  <li>Fill in all the required fields in the form</li>
                  <li>Click "Create Patient" to save the information</li>
                  <li>
                    Your new patient will appear in the list and be
                    automatically selected
                  </li>
                </ol>
              </div>

              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">🔒</span>
                  Privacy & Security
                </h4>
                <p className="text-gray-700 text-sm">
                  Patient information is securely stored and only accessible
                  through your account. This demographic data helps with
                  research organization and can be important for analyzing
                  age-related or gender-related patterns in brain activity.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Uploading Your EEG Data */}
          <section id="uploading-your-eeg-data">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Uploading Your EEG Data
            </h2>
            <p className="text-gray-600 mb-6">
              Once you've selected a patient, it's time to upload their brain
              wave data. Think of this like adding photos to a photo album -
              you're organizing the EEG recordings so you can analyze them
              later. The process is designed to be simple and guides you through
              each step.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">📁</span>
                Step-by-Step Upload Process
              </h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Start the Upload
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Click the "Add Session" button on your dashboard. This
                      opens a window where you can organize your EEG data.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Choose or Create a Session
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      You can either add data to an existing session or create a
                      brand new one. If creating new, give it a descriptive name
                      like "Baseline Recording - June 5, 2025" so you can easily
                      find it later.
                    </p>
                    <div className="bg-gray-50 border border-gray-200 rounded p-3">
                      <p className="text-gray-700 text-xs">
                        <strong>Naming tip:</strong> Include the date and
                        purpose (e.g., "Pre-treatment", "Follow-up") in your
                        session names for better organization.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Select Your EEG File
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      Choose the CSV file containing your brain wave data. The
                      system expects data from all 14 standard EEG channels
                      (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8,
                      AF4).
                    </p>
                    <div className="bg-gray-50 border border-gray-200 rounded p-3">
                      <p className="text-gray-700 text-xs">
                        <strong>File requirements:</strong> CSV format with
                        column headers matching the 14 EEG channel names
                        exactly.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">4</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Upload and Verify
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Click "Upload" and the system will check your file format
                      and save the data. Once complete, you'll see the new
                      session appear in your patient's session list, ready for
                      analysis.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-gray-300 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                <span className="text-lg mr-2">✅</span>
                What Happens Next
              </h4>
              <p className="text-gray-600 text-sm">
                After successful upload, your EEG data is safely stored and
                organized under the patient's profile. You can now run Kalman
                filtering analysis on this data or upload additional sessions
                for the same patient.
              </p>
            </div>
          </section>

          {/* Section: Setting Up Your Analysis */}
          <section id="setting-up-your-analysis">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Setting Up Your Analysis
            </h2>
            <p className="text-gray-600 mb-6">
              Now that your EEG data is uploaded, it's time to set up the Kalman
              filtering analysis. This is where you choose how you want the
              system to clean and analyze your brain wave data. Don't worry -
              you can always run multiple analyses with different settings to
              compare results.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">⚙️</span>
                  Getting to the Analysis Setup
                </h3>
                <p className="text-gray-600 mb-3">
                  With your session uploaded, click the "Run Kalman" button.
                  This opens the analysis configuration window where you'll see
                  three important sections:
                </p>

                <div className="space-y-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Session Information
                    </h4>
                    <p className="text-gray-600 text-sm">
                      This shows which patient and session you're about to
                      analyze. Double-check this is the right data before
                      proceeding.
                    </p>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Algorithm Selection
                    </h4>
                    <p className="text-gray-600 text-sm">
                      A dropdown menu with all available Kalman filter variants.
                      If you're unsure, start with "Potter - Gram-Schmidt" as
                      it's reliable for most data types.
                    </p>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Channel Configuration
                    </h4>
                    <p className="text-gray-600 text-sm">
                      This is where you specify which EEG channels to emphasize
                      in your analysis using the "winning combination" settings.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section: Understanding Channel Selection */}
          <section id="understanding-channel-selection">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Understanding Channel Selection
            </h2>
            <p className="text-gray-600 mb-6">
              The "winning combination" is your way of telling the system which
              brain regions you want to focus on. Think of it like adjusting the
              equalizer on a stereo - you're emphasizing certain "frequencies"
              (in this case, brain regions) over others.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">🎯</span>
                How Channel Selection Works
              </h3>

              <p className="text-gray-600 mb-4">
                You'll enter a series of 14 numbers - one for each EEG channel.
                Use "1" to include a channel and "0" to exclude it. Here's a
                simple example:
              </p>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                <code className="block text-gray-900 text-sm mb-2">
                  [1,0,1,0,1,0,1,0,1,0,1,0,1,0]
                </code>
                <p className="text-gray-600 text-xs">
                  This example includes channels 1, 3, 5, 7, 9, 11, and 13 while
                  excluding the others.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">
                    Common Selection Patterns
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-medium text-gray-800">All channels:</p>
                      <code className="text-gray-600">
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                      </code>
                    </div>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-medium text-gray-800">
                        Frontal brain regions:
                      </p>
                      <code className="text-gray-600">
                        [1,1,1,0,0,0,0,0,0,0,0,1,1,1]
                      </code>
                    </div>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-medium text-gray-800">
                        Left hemisphere:
                      </p>
                      <code className="text-gray-600">
                        [1,1,1,1,1,1,1,0,0,0,0,0,0,0]
                      </code>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">
                    When to Customize
                  </h4>
                  <ul className="text-gray-600 text-sm space-y-1">
                    <li>
                      • <strong>Research focus:</strong> Studying specific brain
                      regions
                    </li>
                    <li>
                      • <strong>Data quality:</strong> Excluding noisy or
                      problematic channels
                    </li>
                    <li>
                      • <strong>Comparison studies:</strong> Testing different
                      regional hypotheses
                    </li>
                    <li>
                      • <strong>Clinical needs:</strong> Focusing on areas
                      relevant to specific conditions
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="border border-gray-300 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                <span className="text-lg mr-2">💡</span>
                Practical Tip
              </h4>
              <p className="text-gray-600 text-sm">
                If you're unsure about channel selection, start with all
                channels included (all 1s). You can always run additional
                analyses with different combinations to see how focusing on
                specific regions affects your results.
              </p>
            </div>
          </section>

          {/* Section: Running Your Analysis */}
          <section id="running-your-analysis">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Running Your Analysis
            </h2>
            <p className="text-gray-600 mb-6">
              Once you've chosen your algorithm and set your channel
              preferences, you're ready to start the analysis. The system will
              work behind the scenes to apply advanced mathematical filtering to
              your brain wave data, cleaning up noise and revealing clearer
              patterns.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">🚀</span>
                Starting the Analysis Process
              </h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Final Review
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Double-check your algorithm choice and channel
                      combination. Make sure you're analyzing the right session
                      for the right patient.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Click "Run Kalman Analysis"
                    </h4>
                    <p className="text-gray-600 text-sm">
                      This starts the filtering process. You'll see a progress
                      indicator showing that the system is working on your data.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Wait for Processing
                    </h4>
                    <p className="text-gray-600 text-sm">
                      The system applies the mathematical filters to clean your
                      data. Processing time varies depending on data size and
                      algorithm complexity - usually just a few minutes.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">4</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Analysis Complete
                    </h4>
                    <p className="text-gray-600 text-sm">
                      When finished, you'll receive confirmation that your
                      analysis is ready. The results are automatically saved and
                      ready to view.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">⏱️</span>
                  What Happens During Processing
                </h4>
                <p className="text-gray-600 text-sm">
                  The system validates your data, applies the selected Kalman
                  filter, calculates amplitude measurements, and generates
                  frequency analysis. All results are saved securely for you to
                  review.
                </p>
              </div>

              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">📋</span>
                  Keep Your Browser Open
                </h4>
                <p className="text-gray-600 text-sm">
                  While analysis runs, it's best to keep the browser tab open.
                  If you navigate away, you can always check the Results page
                  later to see if your analysis completed successfully.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Viewing Your Results */}
          <section id="viewing-your-results">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Viewing Your Results
            </h2>
            <p className="text-gray-600 mb-6">
              Once your analysis is complete, it's time to explore what the
              Kalman filtering revealed about your brain wave data. The Results
              page is designed to make it easy to find, compare, and understand
              your filtered EEG data.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">📊</span>
                Navigating to Your Results
              </h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Go to Results Page
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Click on "Results" in your navigation menu. This is your
                      central hub for viewing all completed analyses.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Select Your Patient
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      Choose the patient whose results you want to view. The
                      page will show their name and when you last worked with
                      their data.
                    </p>
                    <div className="bg-gray-50 border border-gray-200 rounded p-3">
                      <p className="text-gray-700 text-xs">
                        <strong>Helpful display:</strong> You'll see the
                        patient's last visit date and a summary of their
                        available sessions.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Browse Available Sessions
                    </h4>
                    <p className="text-gray-600 text-sm">
                      You'll see cards for each session that has completed
                      analysis. Each card shows useful information like the
                      session name, which algorithm was used, and how long the
                      analysis took.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">4</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      Expand Session Details
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Click on any session card to see the detailed results
                      including graphs and download options. You can expand
                      multiple sessions at once to compare different analyses.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-gray-300 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                <span className="text-lg mr-2">🔍</span>
                What You'll See
              </h4>
              <p className="text-gray-600 text-sm">
                Only sessions with successful analysis results appear on this
                page. If you don't see a session you expect, it may still be
                processing or encountered an error during analysis. The system
                automatically filters to show only sessions with complete,
                viewable results.
              </p>
            </div>
          </section>

          {/* Section: Understanding Your Brain Wave Graphs */}
          <section id="understanding-your-brain-wave-graphs">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Understanding Your Brain Wave Graphs
            </h2>
            <p className="text-gray-600 mb-6">
              Your analysis results include two main types of graphs that help
              you see how the Kalman filtering improved your EEG data. These
              visual representations make it easy to spot patterns, assess data
              quality, and understand the effects of filtering.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">📈</span>
                  Amplitude Over Time Graph
                </h3>
                <p className="text-gray-600 mb-4">
                  This graph shows the strength of brain wave signals over time,
                  comparing your original recording with the filtered version.
                  It's like before-and-after photos showing how noise reduction
                  improved your data.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Original Signal (Raw Data)
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Shows your EEG data exactly as recorded, including all the
                      natural noise from muscle movements, electrical
                      interference, and other sources. You'll often see rapid
                      fluctuations and spikes.
                    </p>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Filtered Signal (Cleaned Data)
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Displays the Kalman-filtered version, which should appear
                      much smoother and more stable while preserving the
                      important brain wave patterns you want to study.
                    </p>
                  </div>
                </div>

                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    What to Look For
                  </h4>
                  <ul className="text-gray-600 text-sm space-y-1">
                    <li>
                      • <strong>Smoother patterns:</strong> The filtered signal
                      should have fewer random spikes and fluctuations
                    </li>
                    <li>
                      • <strong>Preserved rhythms:</strong> Important brain wave
                      patterns should still be visible and clear
                    </li>
                    <li>
                      • <strong>Reduced noise:</strong> Background electrical
                      interference should be minimized
                    </li>
                    <li>
                      • <strong>Clearer trends:</strong> Overall patterns should
                      be easier to identify and interpret
                    </li>
                  </ul>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🌊</span>
                  Frequency Analysis Graph (Welch PSD)
                </h3>
                <p className="text-gray-600 mb-4">
                  This graph breaks down your brain waves by frequency, showing
                  which brain wave types (alpha, beta, theta, etc.) are
                  strongest in your data. Think of it like a musical spectrum
                  analyzer that shows which "notes" are loudest in your brain's
                  electrical symphony.
                </p>

                <div className="space-y-4 mb-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">
                      The Four Analysis Lines
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <p className="text-gray-700 text-sm mb-1">
                          <strong>Original:</strong> Frequency content of your
                          raw EEG data
                        </p>
                        <p className="text-gray-700 text-sm">
                          <strong>All:</strong> Frequency content after
                          filtering all channels combined
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-700 text-sm mb-1">
                          <strong>WC (Winning Combination):</strong> Frequencies
                          from only your selected channels
                        </p>
                        <p className="text-gray-700 text-sm">
                          <strong>NWC (Non-Winning Combination):</strong>{" "}
                          Frequencies from the channels you didn't select
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">
                      Key Brain Wave Frequencies
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <p className="text-gray-700 text-sm mb-1">
                          <strong>Delta (0.5-4 Hz):</strong> Deep sleep,
                          unconscious processes
                        </p>
                        <p className="text-gray-700 text-sm">
                          <strong>Theta (4-8 Hz):</strong> Creativity,
                          meditation, memory formation
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-700 text-sm mb-1">
                          <strong>Alpha (8-13 Hz):</strong> Relaxed awareness,
                          closed-eye resting
                        </p>
                        <p className="text-gray-700 text-sm">
                          <strong>Beta (13-30 Hz):</strong> Active thinking,
                          concentration, alertness
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Interpreting Your Results
                  </h4>
                  <p className="text-gray-600 text-sm">
                    Compare the different lines to see how your channel
                    selection and filtering affected specific brain wave
                    frequencies. A good filter should reduce noise frequencies
                    while preserving or enhancing the brain wave frequencies
                    that are relevant to your research or clinical goals.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Section: Saving and Sharing Your Results */}
          <section id="saving-and-sharing-your-results">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Saving and Sharing Your Results
            </h2>
            <p className="text-gray-600 mb-6">
              Once you're satisfied with your analysis results, you can download
              your filtered brain wave data for further analysis, backup, or
              sharing with colleagues. The platform provides your data in
              standard spreadsheet format that works with Excel, statistical
              software, and research tools.
            </p>

            <div className="border border-gray-300 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-3">💾</span>
                Three Types of Data Downloads
              </h3>
              <p className="text-gray-600 mb-4">
                When you view your session results, you'll see three download
                buttons, each providing different aspects of your analysis.
                Think of these as different views of the same data - like
                getting the raw photos, the edited versions, and the metadata
                all separately.
              </p>

              <div className="space-y-4">
                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold text-xs">1</span>
                    </div>
                    Core Filter Results (Y-Values)
                  </h4>
                  <p className="text-gray-600 text-sm mb-3">
                    This file contains the fundamental output from the Kalman
                    filter - the mathematical values that represent how the
                    algorithm processed your brain wave data over time.
                  </p>
                  <div className="bg-gray-50 border border-gray-200 rounded p-3">
                    <p className="text-gray-700 text-sm mb-2">
                      <strong>What's included:</strong> Time stamps, filter
                      output values, session information, and algorithm
                      identifiers
                    </p>
                    <p className="text-gray-700 text-sm">
                      <strong>Best for:</strong> Advanced statistical analysis,
                      comparing filter performance, building custom
                      visualizations, research methodology validation
                    </p>
                  </div>
                </div>

                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold text-xs">2</span>
                    </div>
                    Amplitude Data
                  </h4>
                  <p className="text-gray-600 text-sm mb-3">
                    This file shows the strength of brain wave signals over time
                    for all four analysis types: your original data, the
                    combined filtered result, your selected channels, and the
                    non-selected channels.
                  </p>
                  <div className="bg-gray-50 border border-gray-200 rounded p-3">
                    <p className="text-gray-700 text-sm mb-2">
                      <strong>What's included:</strong> Amplitude values for
                      Original, All, WC, and NWC signals with timestamps
                    </p>
                    <p className="text-gray-700 text-sm">
                      <strong>Best for:</strong> Creating custom amplitude
                      graphs, studying signal strength patterns, research
                      publications, detailed signal analysis
                    </p>
                  </div>
                </div>

                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white font-bold text-xs">3</span>
                    </div>
                    Frequency Analysis (Welch Data)
                  </h4>
                  <p className="text-gray-600 text-sm mb-3">
                    This file contains the detailed frequency breakdown of your
                    brain waves, showing the power of different brain wave types
                    (alpha, beta, theta, etc.) for each analysis condition.
                  </p>
                  <div className="bg-gray-50 border border-gray-200 rounded p-3">
                    <p className="text-gray-700 text-sm mb-2">
                      <strong>What's included:</strong> Frequency values and
                      corresponding power measurements for all four signal types
                    </p>
                    <p className="text-gray-700 text-sm">
                      <strong>Best for:</strong> Brain wave research,
                      frequency-specific analysis, studying different brain
                      states, clinical applications
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">📋</span>
                  Download Tips
                </h4>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• Download all three file types for complete analysis</li>
                  <li>
                    • Use descriptive filenames including patient ID and date
                  </li>
                  <li>• Keep original raw data files as backup</li>
                  <li>
                    • Consider downloading results from multiple algorithms for
                    comparison
                  </li>
                </ul>
              </div>

              <div className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-lg mr-2">🔗</span>
                  File Compatibility
                </h4>
                <p className="text-gray-600 text-sm">
                  All downloads are in standard CSV format that opens directly
                  in Excel, imports easily into SPSS, R, Python, or any
                  statistical software. Files include headers and are ready for
                  immediate analysis.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Advanced Features and Customization */}
          <section id="advanced-features-and-customization">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Advanced Features and Customization
            </h2>
            <p className="text-gray-600 mb-6">
              As you become more comfortable with the platform, you can explore
              advanced features that give you greater control over your EEG
              analysis. These tools help you fine-tune your approach and adapt
              the system to your specific research needs.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🎛️</span>
                  Experimenting with Channel Combinations
                </h3>
                <p className="text-gray-600 mb-4">
                  The "winning combination" feature is one of the most powerful
                  tools for customizing your analysis. By trying different
                  channel selections, you can explore how different brain
                  regions contribute to your results.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Research Applications
                    </h4>
                    <ul className="text-gray-600 text-sm space-y-1">
                      <li>• Compare left vs. right hemisphere activity</li>
                      <li>• Isolate frontal vs. posterior brain regions</li>
                      <li>• Focus on specific areas relevant to your study</li>
                      <li>• Test hypotheses about regional brain function</li>
                    </ul>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Quality Control
                    </h4>
                    <ul className="text-gray-600 text-sm space-y-1">
                      <li>• Exclude channels with poor electrode contact</li>
                      <li>• Remove consistently noisy channels</li>
                      <li>• Focus on channels with good signal quality</li>
                      <li>• Validate results across different channel sets</li>
                    </ul>
                  </div>
                </div>

                <div className="border border-gray-300 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Systematic Approach
                  </h4>
                  <p className="text-gray-600 text-sm">
                    Try running the same session with different channel
                    combinations to see how regional selection affects your
                    results. This comparative approach helps you understand
                    which brain areas are most relevant to your research
                    questions.
                  </p>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🔬</span>
                  Comparing Algorithm Performance
                </h3>
                <p className="text-gray-600 mb-4">
                  One of the platform's greatest strengths is the ability to run
                  multiple Kalman filter variants on the same data. This lets
                  you empirically determine which approach works best for your
                  specific type of EEG recordings.
                </p>

                <div className="space-y-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Methodology Validation
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Run 2-3 different algorithms on the same session and
                      compare their results. This helps you choose the most
                      appropriate method for your research and provides evidence
                      for your methodology in publications.
                    </p>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Performance Assessment
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Look at processing times, noise reduction quality, and
                      pattern preservation across different algorithms. Some may
                      work better for your specific data characteristics or
                      research requirements.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🚀</span>
                  Future Possibilities
                </h3>
                <p className="text-gray-600 mb-4">
                  The platform is designed to grow with advancing research
                  needs. As new filtering techniques become available or your
                  research develops new requirements, additional algorithm
                  variants can be integrated into the system.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Expanding Analysis Options
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Future updates may include new Kalman variants, custom
                      filter parameters, or specialized algorithms for specific
                      types of EEG analysis.
                    </p>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Enhanced Comparisons
                    </h4>
                    <p className="text-gray-600 text-sm">
                      As more algorithms become available, you'll be able to
                      perform even more comprehensive side-by-side comparisons
                      to optimize your analysis approach.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section: Getting Help and Best Practices */}
          <section id="getting-help-and-best-practices">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Getting Help and Best Practices
            </h2>
            <p className="text-gray-600 mb-6">
              Even with the most user-friendly platform, you might occasionally
              encounter questions or challenges. Here's guidance for common
              situations and tips for getting the most out of your EEG analysis
              experience.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🔧</span>
                  Common Challenges and Solutions
                </h3>

                <div className="space-y-4">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Can't See Your Analysis Results
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      If your completed analysis isn't showing up in the Results
                      page, check these common causes:
                    </p>
                    <ul className="text-gray-600 text-sm space-y-1 ml-4">
                      <li>• Make sure you've selected the correct patient</li>
                      <li>
                        • Verify that your analysis actually completed (check
                        for processing time)
                      </li>
                      <li>
                        • Try refreshing the page or logging out and back in
                      </li>
                      <li>
                        • Look for any error messages that might indicate what
                        went wrong
                      </li>
                    </ul>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Analysis Keeps Failing
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      When your Kalman analysis doesn't complete successfully,
                      the most common issues are:
                    </p>
                    <ul className="text-gray-600 text-sm space-y-1 ml-4">
                      <li>
                        • Check your winning combination has exactly 14 numbers
                        (only 0s and 1s)
                      </li>
                      <li>
                        • Verify your EEG file has all required channel columns
                        with correct names
                      </li>
                      <li>
                        • Make sure your data doesn't have extreme values or
                        missing data
                      </li>
                      <li>
                        • Try a different algorithm if one consistently fails
                      </li>
                    </ul>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Graphs Appear Blank or Missing
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      Empty graphs usually indicate that the analysis didn't
                      generate complete results:
                    </p>
                    <ul className="text-gray-600 text-sm space-y-1 ml-4">
                      <li>
                        • Check if the session shows a processing time greater
                        than 0 seconds
                      </li>
                      <li>
                        • Look for an algorithm name in the session information
                      </li>
                      <li>
                        • If both are missing, the analysis may have failed -
                        try re-running it
                      </li>
                      <li>
                        • Sometimes refreshing the page helps if it's just a
                        display issue
                      </li>
                    </ul>
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      File Upload Problems
                    </h4>
                    <p className="text-gray-600 text-sm mb-2">
                      If your EEG files won't upload, these steps usually
                      resolve the issue:
                    </p>
                    <ul className="text-gray-600 text-sm space-y-1 ml-4">
                      <li>
                        • Double-check that your file is in CSV format (.csv
                        extension)
                      </li>
                      <li>
                        • Verify all 14 EEG channel names are spelled exactly
                        right
                      </li>
                      <li>
                        • Remove any empty rows or text characters from your
                        data
                      </li>
                      <li>
                        • Try saving your file as CSV again from Excel or your
                        data software
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">⭐</span>
                  Tips for Success
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">
                        Data Organization
                      </h4>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>
                          • Use consistent, descriptive names for patients and
                          sessions
                        </li>
                        <li>
                          • Keep notes about which settings work best for
                          different data types
                        </li>
                        <li>
                          • Download results immediately after analysis
                          completes
                        </li>
                        <li>
                          • Maintain backup copies of your original data files
                        </li>
                      </ul>
                    </div>

                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">
                        Analysis Strategy
                      </h4>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>
                          • Start with Potter - Gram-Schmidt for reliable
                          baseline results
                        </li>
                        <li>
                          • Test different algorithms on the same data to
                          compare
                        </li>
                        <li>
                          • Document which combinations work best for your
                          research
                        </li>
                        <li>
                          • Process similar sessions in batches with the same
                          settings
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">
                        Quality Control
                      </h4>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>
                          • Always check your data quality before uploading
                        </li>
                        <li>
                          • Compare filtered vs. original signals to assess
                          improvement
                        </li>
                        <li>
                          • Look for reasonable processing times (very short may
                          indicate errors)
                        </li>
                        <li>
                          • Verify that important brain wave patterns are
                          preserved
                        </li>
                      </ul>
                    </div>

                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">
                        Performance
                      </h4>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>
                          • Keep browser tabs open during analysis processing
                        </li>
                        <li>
                          • Avoid running multiple analyses simultaneously
                        </li>
                        <li>
                          • Use Carlson algorithms for faster processing of
                          large files
                        </li>
                        <li>
                          • Consider Householder methods when accuracy is
                          critical
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-gray-300 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="text-2xl mr-3">📚</span>
                  Building Your Expertise
                </h3>
                <p className="text-gray-600 mb-4">
                  As you use the platform more, you'll develop intuition about
                  which settings work best for different types of data and
                  research questions. Here's how to build that expertise
                  systematically:
                </p>

                <div className="space-y-3">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Start Simple, Then Experiment
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Begin with standard settings (Potter - Gram-Schmidt, all
                      channels included) to establish baseline results. Then
                      systematically vary one parameter at a time to understand
                      how each choice affects your results.
                    </p>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Document Your Findings
                    </h4>
                    <p className="text-gray-600 text-sm">
                      Keep track of which algorithm and channel combinations
                      work best for different types of data or research
                      questions. This becomes valuable reference information for
                      future analyses.
                    </p>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Learn from Comparisons
                    </h4>
                    <p className="text-gray-600 text-sm">
                      The platform's ability to run multiple algorithms on the
                      same data is perfect for learning. Use this feature to
                      understand the practical differences between mathematical
                      approaches.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
