import React from 'react'
import { 
  InformationCircleIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  BookOpenIcon,
  PhoneIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'

const About: React.FC = () => {
  const safetyResources = [
    {
      title: 'OSHA Official Website',
      description: 'Access official workplace safety regulations, training materials, and reporting guidelines.',
      url: 'https://www.osha.gov',
      icon: GlobeAltIcon,
    },
    {
      title: 'Safety Training Resources',
      description: 'Comprehensive safety training materials for various industries and workplace hazards.',
      url: 'https://www.osha.gov/training',
      icon: BookOpenIcon,
    },
    {
      title: 'Report Workplace Hazards',
      description: 'Report unsafe working conditions or workplace hazards to OSHA for investigation.',
      url: 'https://www.osha.gov/workers/file_complaint.html',
      icon: ExclamationTriangleIcon,
    },
    {
      title: 'Emergency Contacts',
      description: '24/7 emergency contact information for workplace safety emergencies.',
      url: 'tel:1-800-321-OSHA',
      icon: PhoneIcon,
    },
  ]

  const safetyTips = [
    'Always wear appropriate personal protective equipment (PPE) for your job tasks',
    'Report unsafe conditions or near-miss incidents immediately to supervisors',
    'Participate in safety training and refresher courses regularly',
    'Follow established safety procedures and never take shortcuts',
    'Maintain good housekeeping practices to prevent slips, trips, and falls',
    'Use proper lifting techniques and ask for help with heavy loads',
    'Keep emergency exits clear and know your evacuation routes',
    'Report injuries, no matter how minor, to ensure proper medical attention',
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="mx-auto h-16 w-16 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mb-4">
          <InformationCircleIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">About WorkerBooBoo</h1>
        <p className="mt-2 text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          A comprehensive workplace safety data visualization platform designed to raise awareness 
          and improve workplace safety through data-driven insights.
        </p>
      </div>

      {/* Mission Statement */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
        <h2 className="text-xl font-semibold text-blue-900 dark:text-blue-100 mb-3">Our Mission</h2>
        <p className="text-blue-800 dark:text-blue-200 leading-relaxed">
          WorkerBooBoo aims to make workplace safety data accessible, understandable, and actionable. 
          By visualizing OSHA incident data on interactive maps and providing comprehensive analytics, 
          we help safety professionals, employers, and workers identify patterns, understand risks, 
          and implement effective safety measures to prevent workplace accidents and fatalities.
        </p>
      </div>

      {/* Key Features */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                  <GlobeAltIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Interactive Mapping</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Visualize workplace incidents on an interactive map with filtering by location, 
                  industry, incident type, and date range.
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                  <BookOpenIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Comprehensive Analytics</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Detailed statistics, trends analysis, and insights to help identify safety patterns 
                  and areas for improvement.
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Real-time Data</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Access to the latest OSHA enforcement and fatality data with regular updates 
                  to ensure current information.
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                  <ShieldCheckIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Safety Resources</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Direct access to OSHA resources, training materials, and reporting tools 
                  to support workplace safety initiatives.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Sources */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Data Sources</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">OSHA Data</h3>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              Our platform integrates data from multiple OSHA sources including enforcement inspections, 
              fatality investigations, and compliance data. All data is publicly available and used 
              in accordance with OSHA's data usage policies.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Data Privacy</h3>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              We prioritize data privacy and do not display any personally identifiable information. 
              All incident data is aggregated and anonymized to protect individual privacy while 
              maintaining the educational and safety value of the information.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Data Updates</h3>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              Data is updated regularly to reflect the latest OSHA investigations and enforcement actions. 
              Users can see when data was last updated and access historical trends over time.
            </p>
          </div>
        </div>
      </div>

      {/* Safety Resources */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Safety Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {safetyResources.map((resource, index) => (
            <a
              key={index}
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="card hover:shadow-md transition-shadow duration-200 border-l-4 border-primary-500"
            >
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <resource.icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">{resource.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{resource.description}</p>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Safety Tips */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
        <h2 className="text-xl font-semibold text-green-900 dark:text-green-100 mb-4">Essential Safety Tips</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {safetyTips.map((tip, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full mt-2 mr-3"></div>
              <p className="text-sm text-green-800 dark:text-green-200">{tip}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Contact Information */}
      <div className="card text-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Get in Touch</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Have questions about workplace safety or suggestions for improving our platform? 
          We'd love to hear from you.
        </p>
        <div className="flex justify-center space-x-4">
          <a
            href="https://www.osha.gov/contactus"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
          >
            Contact OSHA
          </a>
          <a
            href="mailto:safety@example.com"
            className="btn-secondary"
          >
            Email Us
          </a>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-6">
        <p>
          <strong>Disclaimer:</strong> WorkerBooBoo is an educational tool and should not be used 
          as a substitute for professional safety advice or OSHA compliance. Always consult with 
          qualified safety professionals and refer to official OSHA guidelines for workplace safety requirements.
        </p>
        <p className="mt-2">
          This platform is designed to raise awareness and promote workplace safety through 
          data visualization and education.
        </p>
      </div>
    </div>
  )
}

export default About
