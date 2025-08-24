import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import MapView from '../../pages/MapView'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn()
  }
}))

// Mock mapbox-gl
vi.mock('mapbox-gl', () => ({
  default: {
    Map: vi.fn(() => ({
      addControl: vi.fn(),
      on: vi.fn(),
      addTo: vi.fn(),
      isStyleLoaded: vi.fn(() => true),
      loaded: vi.fn(() => true)
    })),
    Marker: vi.fn(() => ({
      setLngLat: vi.fn(() => ({
        setPopup: vi.fn(() => ({
          addTo: vi.fn()
        }))
      }))
    })),
    Popup: vi.fn(() => ({
      setHTML: vi.fn(),
      offset: vi.fn()
    })),
    NavigationControl: vi.fn(),
    FullscreenControl: vi.fn(),
    accessToken: ''
  }
}))

describe('MapView Component', () => {
  it('renders without crashing', () => {
    render(<MapView />)
    expect(screen.getByText('Incident Map')).toBeInTheDocument()
    expect(screen.getByText('Explore workplace safety incidents across the country')).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    render(<MapView />)
    expect(screen.getByText('Loading incidents...')).toBeInTheDocument()
  })

  it('displays legend with correct colors', () => {
    render(<MapView />)
    
    expect(screen.getByText('Legend')).toBeInTheDocument()
    expect(screen.getByText('Fatalities')).toBeInTheDocument()
    expect(screen.getByText('Injuries')).toBeInTheDocument()
    expect(screen.getByText('Other')).toBeInTheDocument()
  })

  it('shows filters button', () => {
    render(<MapView />)
    expect(screen.getByText('Filters')).toBeInTheDocument()
  })

  it('toggles filters panel visibility', async () => {
    render(<MapView />)
    
    const filtersButton = screen.getByText('Filters')
    fireEvent.click(filtersButton)

    // Check if filters panel is visible
    expect(screen.getByText('Incident Type')).toBeInTheDocument()
    expect(screen.getByText('Industry')).toBeInTheDocument()
    expect(screen.getByText('State')).toBeInTheDocument()
    expect(screen.getByText('Start Date')).toBeInTheDocument()
    expect(screen.getByText('End Date')).toBeInTheDocument()
  })

  it('has incident type filter options', () => {
    render(<MapView />)
    
    const filtersButton = screen.getByText('Filters')
    fireEvent.click(filtersButton)

    const incidentTypeSelect = screen.getByDisplayValue('All Types')
    expect(incidentTypeSelect).toBeInTheDocument()
    
    // Check options
    expect(screen.getByText('Fatality')).toBeInTheDocument()
    expect(screen.getByText('Injury')).toBeInTheDocument()
    expect(screen.getByText('Near Miss')).toBeInTheDocument()
  })

  it('has clear filters button', () => {
    render(<MapView />)
    
    const filtersButton = screen.getByText('Filters')
    fireEvent.click(filtersButton)

    expect(screen.getByText('Clear all filters')).toBeInTheDocument()
  })

  it('has map container', () => {
    render(<MapView />)
    
    // The map container should be present - look for the div with the specific class
    const mapContainer = screen.getByText('Loading incidents...').closest('.flex-1')
    expect(mapContainer).toBeInTheDocument()
  })
})
