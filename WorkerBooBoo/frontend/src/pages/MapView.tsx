import React, { useEffect, useRef, useState, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import axios from 'axios'
import { API_CONFIG } from '../config'

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
  state: string
  start_date: string
  end_date: string
}

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [filteredIncidents, setFilteredIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<MapFilters>({
    incident_type: '',
    state: '',
    start_date: '',
    end_date: ''
  })
  
  // Set Mapbox access token
  const mapboxToken = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || ''
  
  useEffect(() => {
    if (mapboxToken && !mapboxgl.accessToken) {
      mapboxgl.accessToken = mapboxToken
    }
  }, [mapboxToken])

  // Set default date range (12 months back from most recent incident)
  const setDefaultDateRange = (incidents: any[]) => {
    if (incidents.length === 0) return
    
    console.log('📅 Setting default date range from', incidents.length, 'incidents')
    
    // Parse all incident dates and find the most recent
    const incidentDates = incidents.map(incident => {
      const date = new Date(incident.incident_date)
      console.log(`Incident ${incident.id}: ${incident.incident_date} -> ${date.toISOString()}`)
      return date
    })
    
    // Find the most recent incident date
    const mostRecentDate = new Date(Math.max(...incidentDates.map(d => d.getTime())))
    
    // Set end date to most recent, start date to 12 months before
    const startDate = new Date(mostRecentDate)
    startDate.setMonth(startDate.getMonth() - 12)
    
    const endDate = new Date(mostRecentDate)
    
    // If the data is very old (more than 2 years), use a more recent default
    const currentYear = new Date().getFullYear()
    const dataYear = mostRecentDate.getFullYear()
    
    if (dataYear < currentYear - 2) {
      console.log('⚠️ Data is very old, using current year minus 1 year as default')
      const currentDate = new Date()
      endDate.setTime(currentDate.getTime())
      startDate.setTime(currentDate.getTime())
      startDate.setFullYear(currentDate.getFullYear() - 1)
    }
    
    // Validate that we have reasonable dates
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      console.log('❌ Invalid dates detected, using current year minus 1 year as fallback')
      const currentDate = new Date()
      endDate.setTime(currentDate.getTime())
      startDate.setTime(currentDate.getTime())
      startDate.setFullYear(currentDate.getFullYear() - 1)
    }
    
    setFilters(prev => ({
      ...prev,
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    }))
    
    console.log('📅 Default date range set:', {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
      mostRecent: mostRecentDate.toISOString().split('T')[0],
      dataYear,
      currentYear
    })
  }

  // Fetch incidents from API
  const fetchIncidents = async () => {
    try {
      setLoading(true)
      // Build API URL with filters
      let apiUrl = `${API_CONFIG.getApiUrl('/api/maps/incidents')}?limit=5000`
      
      // Add date filters if they exist
      if (filters.start_date) {
        apiUrl += `&start_date=${filters.start_date}`
      }
      if (filters.end_date) {
        apiUrl += `&end_date=${filters.end_date}`
      }
      
      // Add other filters
      if (filters.incident_type) {
        apiUrl += `&incident_type=${filters.incident_type}`
      }
      if (filters.state) {
        apiUrl += `&state=${filters.state}`
      }
      console.log('Fetching incidents from:', apiUrl)
      
      const response = await axios.get(apiUrl)
      
      // Handle different possible response structures
      let incidents = []
      if (response.data && response.data.incidents) {
        incidents = response.data.incidents
      } else if (Array.isArray(response.data)) {
        incidents = response.data
      } else {
        console.warn('Unexpected API response structure:', response.data)
        incidents = []
      }
      
      setIncidents(incidents)
      setError(null)
      
      // Debug: Show sample incident dates
      if (incidents.length > 0) {
        console.log('📊 Sample incident dates:')
        incidents.slice(0, 5).forEach((incident: any, index: number) => {
          console.log(`  ${index + 1}. ID ${incident.id}: ${incident.incident_date} (${new Date(incident.incident_date).toISOString()})`)
        })
      }
      
      // Set default date range after incidents are loaded (only on first load)
      if (!userSetDates) {
        setDefaultDateRange(incidents)
      }
    } catch (err: any) {
      console.error('Error fetching incidents:', err)
      setError('Failed to load incidents. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Filter incidents based on current filters
  const filterIncidents = useCallback(() => {
    console.log('🔥 FILTERING INCIDENTS 🔥')
    console.log('Filters applied:', filters)
    console.log('Total incidents before filtering:', incidents.length)
    
    // Show available states in dataset
    const availableStates = [...new Set(incidents.map(i => i.state))].sort()
    console.log('📊 Available states in dataset:', availableStates)
    
    let filtered = incidents

    if (filters.incident_type) {
      filtered = filtered.filter(incident => 
        incident.incident_type === filters.incident_type
      )
      console.log('After incident type filter:', filtered.length)
    }

    if (filters.state) {
      filtered = filtered.filter(incident => 
        incident.state === filters.state
      )
      console.log('After state filter:', filtered.length)
      console.log('Sample filtered incidents:', filtered.slice(0, 3).map(i => ({ id: i.id, state: i.state, city: i.city })))
    }

    console.log('🎯 FINAL RESULT: Showing', filtered.length, 'of', incidents.length, 'incidents')
    setFilteredIncidents(filtered)
  }, [incidents, filters])

  // Refetch incidents when date filters change (server-side filtering)
  // BUT only if they were manually set by user, not auto-set
  const [userSetDates, setUserSetDates] = useState(false)
  
  useEffect(() => {
    if (filters.start_date || filters.end_date) {
      // Only refetch if user manually set dates, not auto-set
      if (userSetDates) {
        console.log('📅 User date filters changed, refetching incidents...')
        fetchIncidents()
      }
    }
  }, [filters.start_date, filters.end_date, userSetDates])

  // Apply client-side filters when incidents or other filters change
  useEffect(() => {
    console.log('Incidents or client-side filters changed, applying filters...')
    filterIncidents()
  }, [incidents, filters.incident_type, filters.state])

  // Clear all filters
  const clearFilters = () => {
    console.log('Clearing all filters')
    setUserSetDates(false)
    setFilters({
      incident_type: '',
      state: '',
      start_date: '',
      end_date: ''
    })
  }

  // Add incident markers to map
  const addIncidentMarkers = () => {
    if (!map.current) return

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.incident-marker')
    existingMarkers.forEach(marker => marker.remove())

    // Use filtered incidents for markers - if empty, show nothing
    const incidentsToShow = filteredIncidents
    
    console.log('🔥 MARKER CREATION 🔥')
    console.log('Adding markers for incidents:', incidentsToShow.length)
    console.log('Using filtered incidents:', filteredIncidents.length > 0)
    console.log('Filtered incidents:', incidentsToShow)
    console.log('First incident details:', incidentsToShow[0] ? {
      id: incidentsToShow[0].id,
      state: incidentsToShow[0].state,
      city: incidentsToShow[0].city,
      coordinates: incidentsToShow[0].coordinates,
      incident_type: incidentsToShow[0].incident_type
    } : 'No incidents')
    
    console.log('🔥 MARKER CREATION 🔥')
    console.log('Adding markers for incidents:', incidentsToShow.length)
    console.log('Using filtered incidents:', filteredIncidents.length > 0)
    console.log('Filtered incidents:', incidentsToShow)
    console.log('First incident details:', incidentsToShow[0] ? {
      id: incidentsToShow[0].id,
      state: incidentsToShow[0].state,
      city: incidentsToShow[0].city,
      coordinates: incidentsToShow[0].coordinates,
      incident_type: incidentsToShow[0].incident_type
    } : 'No incidents')

    // Only add markers if there are incidents to show
    if (incidentsToShow.length === 0) {
      console.log('No incidents to show, map will be empty')
      return
    }
    
    incidentsToShow.forEach((incident) => {
      console.log(`🎯 Processing incident ${incident.id}: ${incident.city}, ${incident.state}`)
      
      // Validate coordinates before creating marker
      if (!incident.coordinates || !Array.isArray(incident.coordinates) || incident.coordinates.length !== 2) {
        console.warn('❌ Missing or invalid coordinates for incident:', incident.id, { 
          coordinates: incident.coordinates 
        })
        return
      }

      const [lat, lng] = incident.coordinates
      
      console.log(`📍 Coordinates: lat=${lat}, lng=${lng}`)
      
      // Validate coordinate values
      if (typeof lat !== 'number' || typeof lng !== 'number' || 
          lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        console.warn('❌ Invalid coordinate values for incident:', incident.id, { lat, lng })
        return
      }

      // Create marker element
      const markerEl = document.createElement('div')
      markerEl.className = 'incident-marker cursor-pointer'
      markerEl.style.width = '20px'
      markerEl.style.height = '20px'
      markerEl.style.borderRadius = '50%'
      markerEl.style.border = '2px solid white'
      markerEl.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)'
      
      // Color based on incident type
      if (incident.incident_type === 'fatality') {
        markerEl.style.backgroundColor = '#dc2626' // Red
      } else {
        markerEl.style.backgroundColor = '#ea580c' // Orange
      }

      // Create popup content
      const popupContent = `
        <div class="p-2">
          <h3 class="font-bold text-lg mb-1">${incident.company_name}</h3>
          <p class="text-sm text-gray-600 mb-1">${incident.city}, ${incident.state}</p>
          <p class="text-sm text-gray-600 mb-2">${incident.incident_type} • ${incident.industry}</p>
          <p class="text-xs text-gray-500">OSHA ID: ${incident.osha_id}</p>
        </div>
      `

      // Create and add marker
      try {
        console.log(`🎨 Creating marker for incident ${incident.id}`)
        const marker = new mapboxgl.Marker(markerEl)
          .setLngLat([lng, lat]) // Mapbox expects [longitude, latitude]
          .setPopup(new mapboxgl.Popup().setHTML(popupContent))
          .addTo(map.current!)
        console.log(`✅ Marker created and added to map for incident ${incident.id}`)
      } catch (error) {
        console.error('❌ Error creating marker for incident:', incident.id, error)
      }
    })
  }

  useEffect(() => {
    if (mapContainer.current && !map.current && mapboxToken) {
      console.log('Initializing map on platform:', navigator.platform)
      console.log('Incidents available:', incidents.length)
      
      // Initialize map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-98.5795, 39.8283], // Center of US
        zoom: 4
      })

      // Add navigation controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

        // Add incident markers when map loads
  map.current.on('load', () => {
    console.log('Map loaded, incidents available:', incidents.length)
    // Don't add markers here - let the incidents effect handle it
  })
    }
  }, [mapboxToken, incidents])

  // Fetch incidents on component mount
  useEffect(() => {
    fetchIncidents()
  }, [])
  
  // Mac-specific fallback for marker addition - REMOVED to prevent conflicts

  // Add markers when incidents change and map is ready
  useEffect(() => {
    console.log('🔥 MARKER MANAGEMENT 🔥')
    console.log('Incidents changed, count:', incidents.length)
    console.log('Filtered incidents count:', filteredIncidents.length)
    console.log('Map ready:', !!map.current)
    console.log('Map style loaded:', map.current?.isStyleLoaded())
    console.log('Platform:', navigator.platform)
    
    if (incidents.length > 0 && map.current) {
      if (map.current.isStyleLoaded()) {
        console.log('Map ready, adding markers immediately...')
        addIncidentMarkers()
      } else {
        console.log('Map not ready, waiting for style load...')
        // Wait for map to be fully loaded
        const handleMapLoad = () => {
          console.log('Map style loaded, adding markers...')
          addIncidentMarkers()
        }
        
        // For Mac, also add a small delay to ensure stability
        if (navigator.platform.includes('Mac')) {
          setTimeout(() => {
            if (map.current && map.current.isStyleLoaded()) {
              console.log('Mac: Adding markers after delay...')
              addIncidentMarkers()
            }
          }, 500)
        }
        
        map.current.on('idle', handleMapLoad)
        return () => {
          if (map.current) {
            map.current.off('idle', handleMapLoad)
          }
        }
      }
    }
  }, [incidents, filteredIncidents])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Filters Toggle */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">Map View - Real Incidents</h1>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            {showFilters ? 'Hide' : 'Show'} Filters
          </button>
        </div>
        
        {loading && (
          <div className="flex items-center mt-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span className="text-sm text-gray-600">Loading incidents...</span>
          </div>
        )}
        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}
        {!loading && !error && (
          <div className="mt-2 text-sm text-gray-600">
            Showing {filteredIncidents.length} of {incidents.length} incidents
            {filters.start_date && filters.end_date && (
              <span className="ml-2 text-green-600">
                📅 {filters.start_date} to {filters.end_date}
              </span>
            )}
            {filters.state && (
              <span className="ml-2 text-blue-600">
                • Filtered by: {filters.state}
              </span>
            )}
            {incidents.length >= 5000 && (
              <span className="ml-2 text-amber-600">
                ⚠️ Showing maximum 5000 incidents. Additional data available beyond this limit.
              </span>
            )}
          </div>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white border-b border-gray-200 px-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date Range Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => {
                  console.log('Start date changed to:', e.target.value)
                  setUserSetDates(true)
                  setFilters({...filters, start_date: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => {
                  console.log('End date changed to:', e.target.value)
                  setUserSetDates(true)
                  setFilters({...filters, end_date: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Incident Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Incident Type</label>
              <select
                value={filters.incident_type}
                onChange={(e) => {
                  console.log('Incident type changed to:', e.target.value)
                  setFilters({...filters, incident_type: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="fatality">Fatality</option>
                <option value="injury">Injury</option>
                <option value="near_miss">Near Miss</option>
              </select>
            </div>

            {/* State Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
              <select
                value={filters.state}
                onChange={(e) => {
                  console.log('State changed to:', e.target.value)
                  setFilters({...filters, state: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All States</option>
                {[...new Set(incidents.map(i => i.state))].sort().map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Info */}
          <div className="mt-4 mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              💡 <strong>How filtering works:</strong> Date filters trigger a new database query. 
              State and incident type filters are applied to the current results. 
              Use "Refresh Data" to manually update with current filters.
            </p>
          </div>
          
          {/* Filter Action Buttons */}
          <div className="mt-4 flex justify-center space-x-4">
            <button
              onClick={() => {
                console.log('Clear filters button clicked')
                clearFilters()
              }}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              Clear All Filters
            </button>
            
            <button
              onClick={() => {
                console.log('Setting recent date range (current year minus 1 year)')
                setUserSetDates(true)
                const currentDate = new Date()
                const startDate = new Date(currentDate)
                startDate.setFullYear(currentDate.getFullYear() - 1)
                
                setFilters(prev => ({
                  ...prev,
                  start_date: startDate.toISOString().split('T')[0],
                  end_date: currentDate.toISOString().split('T')[0]
                }))
              }}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Set Recent Range
            </button>
            
            <button
              onClick={() => {
                console.log('Refreshing data with current filters')
                fetchIncidents()
              }}
              className="bg-green-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
            >
              Refresh Data
            </button>
          </div>
        </div>
      )}
      
      {/* Map Container */}
      <div className="flex-1 relative">
        <div 
          ref={mapContainer} 
          className="w-full h-[calc(100vh-4rem)]"
        />
      </div>
    </div>
  )
}

export default MapView
