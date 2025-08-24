import React, { useState, useEffect, useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { 
  FunnelIcon, 
  MapIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'
import { API_CONFIG } from '../config'
import { format } from 'date-fns'

// Set your Mapbox access token here
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || ''

interface Incident {
  id: number
  osha_id: string
  company_name: string
  address: string
  city: string
  state: string
  coordinates: [number, number]
  incident_date: string
  incident_type: string
  industry: string
  description: string
  investigation_status: string
  citations_issued: boolean
  penalty_amount: number | null
}

interface MapFilters {
  incident_type: string
  industry: string
  state: string
  start_date: string
  end_date: string
}

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<MapFilters>({
    incident_type: '',
    industry: '',
    state: '',
    start_date: '',
    end_date: ''
  })
  const [showFilters, setShowFilters] = useState(false)
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)
  const [isFlyoutCollapsed, setIsFlyoutCollapsed] = useState(false)

  useEffect(() => {
    if (mapContainer.current && !map.current) {
      initializeMap()
    }
  }, [])

  useEffect(() => {
    fetchIncidents()
  }, [filters.incident_type, filters.industry, filters.state, filters.start_date, filters.end_date])

  // Keyboard shortcut for toggling flyout
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && selectedIncident) {
        setSelectedIncident(null)
      }
      if (event.key === 'Tab' && selectedIncident && event.ctrlKey) {
        event.preventDefault()
        setIsFlyoutCollapsed(!isFlyoutCollapsed)
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [selectedIncident, isFlyoutCollapsed])

  // Add markers when incidents change and map is ready
  useEffect(() => {
    console.log('useEffect triggered - incidents:', incidents.length, 'map ready:', map.current?.isStyleLoaded())
    if (incidents.length > 0 && map.current) {
      console.log('Calling addIncidentMarkers from useEffect')
      addIncidentMarkers()
    }
  }, [incidents])

  const initializeMap = () => {
    if (!mapContainer.current) return

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [-98.5795, 39.8283], // US center
      zoom: 4,
      attributionControl: false
    })

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')
    map.current.addControl(new mapboxgl.FullscreenControl(), 'top-right')

    map.current.on('load', () => {
      console.log('Map loaded, checking if incidents are ready...')
      // Only add markers if incidents are already loaded
      if (incidents.length > 0) {
        addIncidentMarkers()
      }
    })
  }

  const addIncidentMarkers = () => {
    if (!map.current) {
      console.log('Map not ready yet')
      return
    }

    console.log('Adding markers for', incidents.length, 'incidents')
    console.log('Map ready:', map.current.isStyleLoaded())
    console.log('Map loaded:', map.current.loaded())

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.incident-marker')
    existingMarkers.forEach(marker => marker.remove())

    incidents.forEach((incident) => {
      if (!incident.coordinates) {
        console.log('Skipping incident without coordinates:', incident)
        return
      }
      
      // Validate coordinate values
      const [lat, lng] = incident.coordinates
      if (typeof lat !== 'number' || typeof lng !== 'number' || 
          lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        console.log('Skipping incident with invalid coordinates:', incident.coordinates, incident)
        return
      }

      // Create marker element
      const markerEl = document.createElement('div')
      markerEl.className = 'incident-marker'
      markerEl.style.width = '20px'
      markerEl.style.height = '20px'
      markerEl.style.borderRadius = '50%'
      markerEl.style.border = '2px solid white'
      markerEl.style.cursor = 'pointer'
      markerEl.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)'

      // Color based on incident type
      if (incident.incident_type === 'fatality') {
        markerEl.style.backgroundColor = '#dc2626' // red
      } else if (incident.incident_type === 'injury') {
        markerEl.style.backgroundColor = '#ea580c' // orange
      } else {
        markerEl.style.backgroundColor = '#ca8a04' // yellow
      }

      // Add marker to map (no popup text)
      // Mapbox expects [longitude, latitude] but our API returns [latitude, longitude]
      new mapboxgl.Marker(markerEl)
        .setLngLat([lng, lat])
        .addTo(map.current)

      // Add click handler
      markerEl.addEventListener('click', () => {
        setSelectedIncident(incident)
      })
    })
  }



  const fetchIncidents = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      
      if (filters.incident_type) params.append('incident_type', filters.incident_type)
      if (filters.industry) params.append('industry', filters.industry)
      if (filters.state) params.append('state', filters.state)
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)

      console.log('Fetching incidents...')
      const response = await axios.get(API_CONFIG.getApiUrl(`/api/maps/incidents?${params.toString()}`))
      console.log('API Response:', response.data)
      console.log('Incidents count:', response.data.incidents.length)
      setIncidents(response.data.incidents)
      
    } catch (err) {
      setError('Failed to load incidents')
      console.error('Error fetching incidents:', err)
    } finally {
      setLoading(false)
    }
  }

  // Debounced filter change for text inputs
  const debouncedFilterChange = useCallback(
    (key: keyof MapFilters, value: string) => {
      const timeoutId = setTimeout(() => {
        setFilters(prev => ({ ...prev, [key]: value }))
      }, 500) // 500ms delay
      
      return () => clearTimeout(timeoutId)
    },
    []
  )

  const handleFilterChange = (key: keyof MapFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setFilters({
      incident_type: '',
      industry: '',
      state: '',
      start_date: '',
      end_date: ''
    })
  }

  const getIncidentTypeColor = (type: string) => {
    switch (type) {
      case 'fatality': return 'text-red-600 bg-red-100'
      case 'injury': return 'text-orange-600 bg-orange-100'
      default: return 'text-yellow-600 bg-yellow-100'
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Incident Map</h1>
            <p className="text-gray-600">Explore workplace safety incidents across the country</p>
          </div>
                      <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="btn-secondary flex items-center"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filters
              </button>
              <div className="text-sm text-gray-500">
                {incidents.length} incidents shown
              </div>
              <div className="text-xs text-gray-400">
                <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">Esc</kbd> to close, <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">Ctrl+Tab</kbd> to toggle
              </div>
            </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Incident Type
              </label>
              <select
                value={filters.incident_type}
                onChange={(e) => handleFilterChange('incident_type', e.target.value)}
                className="input-field"
              >
                <option value="">All Types</option>
                <option value="fatality">Fatality</option>
                <option value="injury">Injury (SIR Data)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry
              </label>
              <input
                type="text"
                value={filters.industry}
                onChange={(e) => debouncedFilterChange('industry', e.target.value)}
                placeholder="e.g., Construction"
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <input
                type="text"
                value={filters.state}
                onChange={(e) => debouncedFilterChange('state', e.target.value)}
                placeholder="e.g., NY"
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => handleFilterChange('start_date', e.target.value)}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => handleFilterChange('end_date', e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          
          {/* Active Filters Summary */}
          {Object.values(filters).some(value => value) && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <div className="text-sm font-medium text-gray-700 mb-2">Active Filters:</div>
              <div className="flex flex-wrap gap-2">
                {filters.incident_type && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                    Type: {filters.incident_type}
                    <button
                      onClick={() => handleFilterChange('incident_type', '')}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.industry && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                    Industry: {filters.industry}
                    <button
                      onClick={() => handleFilterChange('industry', '')}
                      className="ml-1 text-green-600 hover:text-green-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.state && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                    State: {filters.state}
                    <button
                      onClick={() => handleFilterChange('state', '')}
                      className="ml-1 text-purple-600 hover:text-purple-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.start_date && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                    From: {filters.start_date}
                    <button
                      onClick={() => handleFilterChange('start_date', '')}
                      className="ml-1 text-yellow-600 hover:text-yellow-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.end_date && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                    To: {filters.end_date}
                    <button
                      onClick={() => handleFilterChange('end_date', '')}
                      className="ml-1 text-yellow-600 hover:text-yellow-800"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}
          
          <div className="mt-4 flex items-center justify-between">
            <button
              onClick={clearFilters}
              className="btn-secondary text-sm px-3 py-1"
            >
              Clear all filters
            </button>
            <div className="flex items-center space-x-4">
              {loading && (
                <div className="flex items-center text-sm text-gray-500">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                  Updating map...
                </div>
              )}
              <div className="text-sm text-gray-500">
                Showing {incidents.length} incidents
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Map Container */}
      <div className="flex-1 relative">
        <div ref={mapContainer} className="w-full h-full" />
        
        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading incidents...</p>
            </div>
          </div>
        )}

        {/* Error Overlay */}
        {error && (
          <div className="absolute top-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 max-w-sm z-10">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* No Results Overlay */}
        {!loading && !error && incidents.length === 0 && Object.values(filters).some(value => value) && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-lg p-6 max-w-sm z-10 text-center">
            <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your filters or clearing them to see more incidents.</p>
            <button
              onClick={clearFilters}
              className="btn-primary"
            >
              Clear All Filters
            </button>
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 z-10">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Legend</h3>
          <div className="space-y-2">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Fatalities</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Injuries (SIR Data)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Incident Details Sidebar */}
      {selectedIncident && (
        <div className={`absolute right-0 top-0 h-full bg-white shadow-lg border-l border-gray-200 z-20 transition-all duration-300 ${
          isFlyoutCollapsed ? 'w-16 overflow-hidden' : 'w-96 overflow-y-auto'
        }`}>
          {/* Collapsed state overlay */}
          {isFlyoutCollapsed && (
            <div className="absolute inset-0 bg-gradient-to-b from-white to-gray-50 opacity-90"></div>
          )}
          <div className={`${isFlyoutCollapsed ? 'p-2' : 'p-6'}`}>
            <div className="flex items-center justify-between mb-4">
              {!isFlyoutCollapsed && (
                <h2 className="text-lg font-semibold text-gray-900">Incident Details</h2>
              )}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsFlyoutCollapsed(!isFlyoutCollapsed)}
                  className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 transition-colors"
                  title={isFlyoutCollapsed ? "Expand flyout" : "Collapse flyout"}
                >
                  {isFlyoutCollapsed ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => setSelectedIncident(null)}
                  className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
                  title="Close"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            
            {isFlyoutCollapsed ? (
              <div className="text-center cursor-pointer" onClick={() => setIsFlyoutCollapsed(false)}>
                <div className="text-xs text-gray-500 mb-2 animate-pulse">Click to expand</div>
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mx-auto hover:bg-gray-200 transition-all duration-200 hover:scale-110">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-900">{selectedIncident.company_name}</h3>
                  <p className="text-sm text-gray-600">{selectedIncident.address}</p>
                  <p className="text-sm text-gray-600">{selectedIncident.city}, {selectedIncident.state}</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getIncidentTypeColor(selectedIncident.incident_type)}`}>
                    {selectedIncident.incident_type}
                  </span>
                  <span className="text-sm text-gray-500">•</span>
                  <span className="text-sm text-gray-500">{selectedIncident.industry}</span>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-1">Incident Date</h4>
                  <p className="text-sm text-gray-600">
                    {format(new Date(selectedIncident.incident_date), 'MMMM dd, yyyy')}
                  </p>
                </div>
                
                {selectedIncident.description && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Description</h4>
                    <p className="text-sm text-gray-600">{selectedIncident.description}</p>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Status</h4>
                    <p className="text-sm text-gray-600">{selectedIncident.investigation_status}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Citations</h4>
                    <p className="text-sm text-gray-600">
                      {selectedIncident.citations_issued ? 'Yes' : 'No'}
                    </p>
                  </div>
                </div>
                
                {selectedIncident.penalty_amount && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Penalty Amount</h4>
                    <p className="text-sm text-gray-600">
                      ${selectedIncident.penalty_amount.toLocaleString()}
                    </p>
                  </div>
                )}
                
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    OSHA ID: {selectedIncident.osha_id}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default MapView
