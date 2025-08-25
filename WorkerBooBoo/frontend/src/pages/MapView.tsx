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
      
      // Debug: Show sample incident dates and coordinates
      if (incidents.length > 0) {
        console.log('📊 Sample incident dates:')
        incidents.slice(0, 5).forEach((incident: any, index: number) => {
          console.log(`  ${index + 1}. ID ${incident.id}: ${incident.incident_date} (${new Date(incident.incident_date).toISOString()})`)
        })
        
        console.log('🔍 Sample incident coordinates:')
        incidents.slice(0, 5).forEach((incident: any, index: number) => {
          console.log(`  ${index + 1}. ID ${incident.id}: coordinates=${incident.coordinates}, type=${typeof incident.coordinates}, isArray=${Array.isArray(incident.coordinates)}`)
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
  
  // Incident detail card state
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)
  const [currentIncidentIndex, setCurrentIncidentIndex] = useState(0)
  const [showIncidentCard, setShowIncidentCard] = useState(false)
  
  useEffect(() => {
    if (filters.start_date || filters.end_date) {
      // Only refetch if user manually set dates, not auto-set
      if (userSetDates) {
        console.log('📅 User date filters changed, refetching incidents...')
        fetchIncidents()
      }
    }
  }, [filters.start_date, filters.end_date, userSetDates])

  // Center map on filtered state
  const centerMapOnState = (stateFilter: string) => {
    if (!map.current || !stateFilter) return
    
    console.log('🗺️ Centering map on state:', stateFilter)
    
    try {
      // Find all incidents for the selected state
      const stateIncidents = incidents.filter(incident => incident.state === stateFilter)
      
      console.log('🔍 State incidents found:', stateIncidents.length)
      console.log('🔍 First few state incidents:', stateIncidents.slice(0, 3).map(i => ({
        id: i.id,
        coordinates: i.coordinates,
        coordType: typeof i.coordinates,
        isArray: Array.isArray(i.coordinates)
      })))
      
      if (stateIncidents.length === 0) {
        console.log('No incidents found for state:', stateFilter)
        return
      }
      
      // Calculate the center point of all incidents in the state with strict validation
      const validCoordinates = stateIncidents
        .filter(incident => {
          // Check if coordinates exist and are an array
          if (!incident.coordinates || !Array.isArray(incident.coordinates) || incident.coordinates.length !== 2) {
            console.warn('❌ Invalid coordinate structure for incident:', incident.id, incident.coordinates)
            return false
          }
          
          // FIXED: API returns [latitude, longitude] but we need [longitude, latitude] for Mapbox
          const [lat, lng] = incident.coordinates // Swap the order to fix the coordinate mismatch
          
          console.log(`🔍 Incident ${incident.id} coordinates: [${lng}, ${lat}], types: lng=${typeof lng}, lat=${typeof lat}`)
          
          // Validate longitude: must be between -180 and 180
          if (typeof lng !== 'number' || isNaN(lng) || lng < -180 || lng > 180) {
            console.warn('❌ Invalid longitude:', lng, 'for incident:', incident.id)
            return false
          }
          
          // Validate latitude: must be between -90 and 90
          if (typeof lat !== 'number' || isNaN(lat) || lat < -90 || lat > 90) {
            console.warn('❌ Invalid latitude:', lat, 'for incident:', incident.id)
            return false
          }
          
          console.log(`✅ Valid coordinates for incident ${incident.id}: [${lng}, ${lat}]`)
          return true
        })
        .map(incident => incident.coordinates)
      
      console.log('🔍 Valid coordinates found:', validCoordinates.length)
      
      if (validCoordinates.length === 0) {
        console.log('❌ No valid coordinates found for state:', stateFilter)
        // Fallback to default state center if no valid coordinates
        const stateCenters: { [key: string]: [number, number] } = {
          'AL': [-86.7911, 32.8067], 'AK': [-152.4044, 61.3707], 'AZ': [-111.4312, 33.7298],
          'AR': [-92.3731, 34.9697], 'CA': [-119.6816, 36.7783], 'CO': [-105.3111, 39.5501],
          'CT': [-72.7550, 41.6032], 'DE': [-75.5071, 39.3185], 'FL': [-81.6868, 27.6648],
          'GA': [-83.6431, 32.1656], 'HI': [-157.4983, 19.8968], 'ID': [-114.4784, 44.2405],
          'IL': [-88.9861, 40.3495], 'IN': [-86.1349, 39.8494], 'IA': [-93.2105, 42.0329],
          'KS': [-96.7265, 38.5266], 'KY': [-84.6701, 37.6681], 'LA': [-91.8678, 31.1695],
          'ME': [-69.3819, 44.6939], 'MD': [-76.6413, 39.0639], 'MA': [-71.5301, 42.2304],
          'MI': [-84.5362, 44.3148], 'MN': [-93.9000, 46.7296], 'MS': [-89.6785, 32.7416],
          'MO': [-92.2884, 38.4561], 'MT': [-110.4544, 46.8797], 'NE': [-99.9018, 41.4925],
          'NV': [-117.0554, 38.8026], 'NH': [-71.5639, 43.1939], 'NJ': [-74.2179, 40.0583],
          'NM': [-106.2485, 34.5199], 'NY': [-74.2179, 43.2994], 'NC': [-79.0193, 35.7596],
          'ND': [-99.7840, 47.5515], 'OH': [-82.7937, 40.4173], 'OK': [-96.9289, 35.0078],
          'OR': [-120.5542, 43.8041], 'PA': [-77.2098, 40.5908], 'RI': [-71.5118, 41.6809],
          'SC': [-80.9450, 33.8569], 'SD': [-99.4388, 44.2998], 'TN': [-86.6920, 35.7478],
          'TX': [-99.9018, 31.9686], 'UT': [-111.8624, 39.3209], 'VT': [-72.7107, 44.0459],
          'VA': [-78.6569, 37.4316], 'WA': [-121.4905, 47.4009], 'WV': [-80.7939, 38.5976],
          'WI': [-89.6165, 44.2685], 'WY': [-107.3025, 42.7475]
        }
        
        const fallbackCenter = stateCenters[stateFilter]
        if (fallbackCenter) {
          console.log('✅ Using fallback center for state:', stateFilter, fallbackCenter)
          map.current.flyTo({
            center: fallbackCenter,
            zoom: 5, // More conservative zoom for fallback centers
            duration: 2000,
            essential: true
          })
        }
        return
      }
      
      // Calculate center point
      const totalLat = validCoordinates.reduce((sum, coord) => sum + coord[1], 0)
      const totalLng = validCoordinates.reduce((sum, coord) => sum + coord[0], 0)
      const centerLat = totalLat / validCoordinates.length
      const centerLng = totalLng / validCoordinates.length
      
      // Final validation of calculated center
      if (isNaN(centerLat) || isNaN(centerLng) || 
          centerLat < -90 || centerLat > 90 || 
          centerLng < -180 || centerLng > 180) {
        console.error('❌ Calculated center coordinates are invalid:', { lat: centerLat, lng: centerLng })
        return
      }
      
      console.log('✅ Centering map at:', { lat: centerLat, lng: centerLng })
      
      // Safety check: ensure coordinates are reasonable before flying
      if (Math.abs(centerLng) > 180 || Math.abs(centerLat) > 90) {
        console.error('❌ Calculated coordinates are out of bounds:', { lng: centerLng, lat: centerLat })
        return
      }
      
      console.log('🚀 Flying to coordinates:', [centerLng, centerLat])
      
      // Calculate appropriate zoom level based on coordinate spread
      const lngs = validCoordinates.map(coord => coord[0])
      const lats = validCoordinates.map(coord => coord[1])
      const lngRange = Math.max(...lngs) - Math.min(...lngs)
      const latRange = Math.max(...lats) - Math.min(...lats)
      
      // Determine zoom level based on coordinate spread
      let zoomLevel = 6 // Default zoom
      if (lngRange > 10 || latRange > 10) {
        zoomLevel = 4 // Large spread - zoom out more
      } else if (lngRange > 5 || latRange > 5) {
        zoomLevel = 5 // Medium spread
      } else if (lngRange < 1 && latRange < 1) {
        zoomLevel = 8 // Small spread - zoom in more
      }
      
      console.log(`🗺️ Coordinate spread: lng=${lngRange.toFixed(2)}, lat=${latRange.toFixed(2)}, zoom=${zoomLevel}`)
      
      // Use fitBounds to show all pins in the state with appropriate padding
      const bounds = new mapboxgl.LngLatBounds()
      validCoordinates.forEach(coord => {
        bounds.extend(coord)
      })
      
      // Add padding to ensure all pins are visible
      map.current.fitBounds(bounds, {
        padding: 50, // Add 50px padding around the bounds
        duration: 2000,
        essential: true
      })
      
      console.log('🗺️ Using fitBounds to show all pins in state')
    } catch (error) {
      console.error('❌ Error centering map on state:', stateFilter, error)
      // Don't crash the app, just log the error
    }
  }

  // Apply client-side filters when incidents or other filters change
  useEffect(() => {
    console.log('🔥 FILTER EFFECT TRIGGERED 🔥')
    console.log('Filters changed:', filters)
    console.log('Incidents count:', incidents.length)
    
    filterIncidents()
    
    // Center map on state if state filter is applied
    if (filters.state) {
      console.log('🗺️ State filter detected, calling centerMapOnState for:', filters.state)
      centerMapOnState(filters.state)
    } else {
      console.log('🗺️ No state filter, skipping map centering')
    }
  }, [incidents, filters.incident_type, filters.state])

  // Reset map to default view
  const resetMapView = () => {
    if (!map.current) return
    
    console.log('🗺️ Resetting map to default view')
    
    // Return to default US center with appropriate zoom
    map.current.flyTo({
      center: [-98.5795, 39.8283], // Center of US
      zoom: 4,
      duration: 1500, // 1.5 second smooth animation
      essential: true
    })
  }

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
    
    // Reset map view when clearing filters
    resetMapView()
  }

  // Incident detail card navigation
  const openIncidentCard = (incident: Incident) => {
    const index = filteredIncidents.findIndex(i => i.id === incident.id)
    setCurrentIncidentIndex(index >= 0 ? index : 0)
    setSelectedIncident(incident)
    setShowIncidentCard(true)
  }

  const closeIncidentCard = () => {
    setShowIncidentCard(false)
    setSelectedIncident(null)
    setCurrentIncidentIndex(0)
  }

  const navigateToNextIncident = () => {
    if (filteredIncidents.length === 0) return
    const nextIndex = (currentIncidentIndex + 1) % filteredIncidents.length
    setCurrentIncidentIndex(nextIndex)
    setSelectedIncident(filteredIncidents[nextIndex])
  }

  const navigateToPreviousIncident = () => {
    if (filteredIncidents.length === 0) return
    const prevIndex = currentIncidentIndex === 0 ? filteredIncidents.length - 1 : currentIncidentIndex - 1
    setCurrentIncidentIndex(prevIndex)
    setSelectedIncident(filteredIncidents[prevIndex])
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'Not specified'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
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
    console.log('Map ready:', !!map.current)
    console.log('Map style loaded:', map.current?.isStyleLoaded())
    console.log('Total incidents:', incidents.length)
    console.log('Filtered incidents:', filteredIncidents.length)
    console.log('Incidents to show:', incidentsToShow.length)
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
      console.log(`🔍 Raw coordinates:`, incident.coordinates)
      
      // Validate coordinates before creating marker
      if (!incident.coordinates || !Array.isArray(incident.coordinates) || incident.coordinates.length !== 2) {
        console.warn('❌ Missing or invalid coordinates for incident:', incident.id, { 
          coordinates: incident.coordinates 
        })
        return
      }

      // Parse coordinates - handle both string and number formats
      let lng: number, lat: number
      if (Array.isArray(incident.coordinates)) {
        // FIXED: API returns [latitude, longitude] but we need [longitude, latitude] for Mapbox
        [lat, lng] = incident.coordinates // Swap the order to fix the coordinate mismatch
      } else {
        console.warn('❌ Coordinates not in expected array format for incident:', incident.id, incident.coordinates)
        return
      }
      
      // Convert to numbers if they're strings
      lng = parseFloat(lng.toString())
      lat = parseFloat(lat.toString())
      
      // Emergency debugging: log ALL coordinate attempts
      console.log(`🔍 EMERGENCY DEBUG - Incident ${incident.id}:`, {
        rawCoordinates: incident.coordinates,
        parsedLng: lng,
        parsedLat: lat,
        lngType: typeof lng,
        latType: typeof lat,
        lngValid: !isNaN(lng) && lng >= -180 && lng <= 180,
        latValid: !isNaN(lat) && lat >= -90 && lat <= 90
      })
      
      console.log(`📍 Coordinates: lng=${lng}, lat=${lat}, types: lng=${typeof lng}, lat=${typeof lat}`)
      
      // Validate coordinate values with strict bounds checking
      if (isNaN(lng) || lng < -180 || lng > 180) {
        console.warn('❌ Invalid longitude for incident:', incident.id, { lng, lat })
        return
      }
      
      if (isNaN(lat) || lat < -90 || lat > 90) {
        console.warn('❌ Invalid latitude for incident:', incident.id, { lng, lat })
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

      // Add click event to marker
      markerEl.addEventListener('click', () => {
        openIncidentCard(incident)
      })

      // Create and add marker
      try {
        console.log(`🎨 Creating marker for incident ${incident.id}`)
        new mapboxgl.Marker(markerEl)
          .setLngLat([lng, lat]) // Already in [longitude, latitude] order
          .addTo(map.current!)
        console.log(`✅ Marker created and added to map for incident ${incident.id}`)
      } catch (error) {
        console.error('❌ Error creating marker for incident:', incident.id, error)
        // Continue with other markers instead of crashing
      }
    })
    
    // Log summary of marker creation
    const markersCreated = document.querySelectorAll('.incident-marker').length
    console.log(`🎯 MARKER CREATION SUMMARY: Created ${markersCreated} markers out of ${incidentsToShow.length} incidents`)
  }

  useEffect(() => {
    if (mapContainer.current && !map.current && mapboxToken) {
      console.log('Initializing map on platform:', navigator.platform)
      console.log('Incidents available:', incidents.length)
      
      // Initialize map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
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

  // Keyboard navigation for incident card
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!showIncidentCard) return
      
      switch (event.key) {
        case 'Escape':
          closeIncidentCard()
          break
        case 'ArrowLeft':
          navigateToPreviousIncident()
          break
        case 'ArrowRight':
          navigateToNextIncident()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [showIncidentCard, currentIncidentIndex, filteredIncidents])
  
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header with Filters Toggle */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Map View - Real Incidents</h1>
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
            <span className="text-sm text-gray-600 dark:text-gray-400">Loading incidents...</span>
          </div>
        )}
        {error && (
          <div className="mt-2 text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        )}
        {!loading && !error && (
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Showing {filteredIncidents.length} of {incidents.length} incidents
            {filters.start_date && filters.end_date && (
              <span className="ml-2 text-green-600 dark:text-green-400">
                📅 {filters.start_date} to {filters.end_date}
              </span>
            )}
            {filters.state && (
              <span className="ml-2 text-blue-600 dark:text-blue-400">
                • Filtered by: {filters.state}
              </span>
            )}
            {incidents.length >= 5000 && (
              <span className="ml-2 text-amber-600 dark:text-amber-400">
                ⚠️ Showing maximum 5000 incidents. Additional data available beyond this limit.
              </span>
            )}
          </div>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date Range Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => {
                  console.log('Start date changed to:', e.target.value)
                  setUserSetDates(true)
                  setFilters({...filters, start_date: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => {
                  console.log('End date changed to:', e.target.value)
                  setUserSetDates(true)
                  setFilters({...filters, end_date: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Incident Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Incident Type</label>
              <select
                value={filters.incident_type}
                onChange={(e) => {
                  console.log('Incident type changed to:', e.target.value)
                  setFilters({...filters, incident_type: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All Types</option>
                <option value="fatality">Fatality</option>
                <option value="injury">Injury</option>
                <option value="near_miss">Near Miss</option>
              </select>
            </div>

            {/* State Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">State</label>
              <select
                value={filters.state}
                onChange={(e) => {
                  console.log('State changed to:', e.target.value)
                  setFilters({...filters, state: e.target.value})
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All States</option>
                {[...new Set(incidents.map(i => i.state))].sort().map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Info */}
          <div className="mt-4 mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
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
            
            {filters.state && (
              <button
                onClick={() => {
                  console.log('Centering map on selected state:', filters.state)
                  centerMapOnState(filters.state)
                }}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors"
                title={`Center map on ${filters.state}`}
              >
                🗺️ Center on {filters.state}
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Incident Detail Card */}
      {showIncidentCard && selectedIncident && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={closeIncidentCard}
        >
          <div 
            className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl h-[85vh] flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Card Header - Fixed height to prevent clipping */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 flex-shrink-0">
              <div className="flex items-center justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl font-bold mb-2 truncate">{selectedIncident.company_name}</h2>
                  <p className="text-blue-100 text-lg">{selectedIncident.city}, {selectedIncident.state}</p>
                </div>
                <button
                  onClick={closeIncidentCard}
                  className="text-white hover:text-gray-200 transition-colors p-2 ml-4 flex-shrink-0"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {/* Navigation Progress */}
              <div className="flex items-center justify-center">
                <button
                  onClick={navigateToPreviousIncident}
                  className="text-white hover:text-blue-200 transition-colors p-2 mr-4"
                  disabled={filteredIncidents.length <= 1}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <span className="text-blue-100 font-medium">
                  {currentIncidentIndex + 1} of {filteredIncidents.length} incidents
                </span>
                
                <button
                  onClick={navigateToNextIncident}
                  className="text-white hover:text-blue-200 transition-colors p-2 ml-4"
                  disabled={filteredIncidents.length <= 1}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Card Content - Fixed height with scrollable content */}
            <div className="p-6 overflow-y-auto flex-1">
              {/* Top Section - Business Info and Description */}
              <div className="space-y-4 mb-6">
                {/* Business Information */}
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-3 text-lg">Business Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-blue-700 dark:text-blue-300 font-medium">Company:</span>
                      <span className="text-blue-900 dark:text-blue-100 font-semibold">{selectedIncident.company_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700 dark:text-blue-300 font-medium">Industry:</span>
                      <span className="text-blue-900 dark:text-blue-100 font-semibold">{selectedIncident.industry}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700 dark:text-blue-300 font-medium">Address:</span>
                      <span className="text-blue-900 dark:text-blue-100 font-semibold">{selectedIncident.address}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700 dark:text-blue-300 font-medium">Location:</span>
                      <span className="text-blue-900 dark:text-blue-100 font-semibold">{selectedIncident.city}, {selectedIncident.state}</span>
                    </div>
                  </div>
                </div>

                {/* Description - Always show, even if empty */}
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-lg">Description</h3>
                  {selectedIncident.description ? (
                    <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">
                      {selectedIncident.description}
                    </p>
                  ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400 italic">No description available for this incident.</p>
                  )}
                </div>
              </div>

              {/* Bottom Section - Incident Details in Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Left Column */}
                <div className="space-y-4">
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Incident Details</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Type:</span>
                        <span className="font-medium capitalize text-gray-900 dark:text-white">{selectedIncident.incident_type.replace('_', ' ')}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Date:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{formatDate(selectedIncident.incident_date)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">OSHA ID:</span>
                        <span className="font-medium font-mono text-xs text-gray-900 dark:text-white">{selectedIncident.osha_id}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Investigation Status</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Status:</span>
                        <span className={`font-medium px-3 py-1 rounded-full text-xs ${
                          selectedIncident.investigation_status === 'closed' 
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' 
                            : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
                        }`}>
                          {selectedIncident.investigation_status}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Citations:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{selectedIncident.citations_issued ? 'Yes' : 'No'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">Penalty:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(selectedIncident.penalty_amount)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Card Footer - Fixed height */}
            <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600 flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  Click outside or press ESC to close
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={navigateToPreviousIncident}
                    className="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg transition-colors text-sm font-medium"
                    disabled={filteredIncidents.length <= 1}
                  >
                    ← Previous
                  </button>
                  <button
                    onClick={navigateToNextIncident}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
                    disabled={filteredIncidents.length <= 1}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
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
