import React, { useState, useEffect, useRef } from 'react'
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
import { format } from 'date-fns'

// Set your Mapbox access token here
mapboxgl.accessToken = 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example'

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

  useEffect(() => {
    if (mapContainer.current && !map.current) {
      initializeMap()
    }
  }, [])

  useEffect(() => {
    fetchIncidents()
  }, [filters])

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
      // Add custom markers for incidents
      addIncidentMarkers()
    })
  }

  const addIncidentMarkers = () => {
    if (!map.current) return

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.incident-marker')
    existingMarkers.forEach(marker => marker.remove())

    incidents.forEach((incident) => {
      if (!incident.coordinates) return

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

      // Create popup
      const popup = new mapboxgl.Popup({
        offset: 25,
        closeButton: false,
        className: 'incident-popup'
      }).setHTML(createPopupContent(incident))

      // Add marker to map
      new mapboxgl.Marker(markerEl)
        .setLngLat(incident.coordinates)
        .setPopup(popup)
        .addTo(map.current)

      // Add click handler
      markerEl.addEventListener('click', () => {
        setSelectedIncident(incident)
      })
    })
  }

  const createPopupContent = (incident: Incident) => {
    return `
      <div class="p-3 max-w-xs">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900 text-sm">${incident.company_name}</h3>
            <p class="text-gray-600 text-xs mt-1">${incident.address}</p>
            <p class="text-gray-600 text-xs">${incident.city}, ${incident.state}</p>
          </div>
          <div class="ml-2">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              incident.incident_type === 'fatality' 
                ? 'bg-red-100 text-red-800' 
                : incident.incident_type === 'injury'
                ? 'bg-orange-100 text-orange-800'
                : 'bg-yellow-100 text-yellow-800'
            }">
              ${incident.incident_type}
            </span>
          </div>
        </div>
        <div class="mt-2 text-xs text-gray-500">
          <p><strong>Date:</strong> ${format(new Date(incident.incident_date), 'MMM dd, yyyy')}</p>
          <p><strong>Industry:</strong> ${incident.industry}</p>
          ${incident.description ? `<p class="mt-1"><strong>Description:</strong> ${incident.description}</p>` : ''}
        </div>
      </div>
    `
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

      const response = await axios.get(`http://localhost:8000/api/maps/incidents?${params.toString()}`)
      setIncidents(response.data.incidents)
      
      // Update markers after incidents change
      setTimeout(() => {
        if (map.current?.isStyleLoaded()) {
          addIncidentMarkers()
        }
      }, 100)
      
    } catch (err) {
      setError('Failed to load incidents')
      console.error('Error fetching incidents:', err)
    } finally {
      setLoading(false)
    }
  }

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
                <option value="injury">Injury</option>
                <option value="near_miss">Near Miss</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry
              </label>
              <input
                type="text"
                value={filters.industry}
                onChange={(e) => handleFilterChange('industry', e.target.value)}
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
                onChange={(e) => handleFilterChange('state', e.target.value)}
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
          
          <div className="mt-4 flex items-center justify-between">
            <button
              onClick={clearFilters}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear all filters
            </button>
            <div className="text-sm text-gray-500">
              Showing {incidents.length} incidents
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
              <span className="text-xs text-gray-600">Injuries</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Other</span>
            </div>
          </div>
        </div>
      </div>

      {/* Incident Details Sidebar */}
      {selectedIncident && (
        <div className="absolute right-0 top-0 h-full w-96 bg-white shadow-lg border-l border-gray-200 z-20 overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Incident Details</h2>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
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
          </div>
        </div>
      )}
    </div>
  )
}

export default MapView
