import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import Statistics from '../../pages/Statistics'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('Statistics Component', () => {
  it('shows loading state initially', () => {
    render(<Statistics />)
    // Look for the loading spinner container
    const loadingContainer = document.querySelector('.flex.items-center.justify-center.h-64')
    expect(loadingContainer).toBeInTheDocument()
  })

  it('renders without crashing', () => {
    render(<Statistics />)
    // Component should render without errors - look for any div
    const container = document.querySelector('div')
    expect(container).toBeInTheDocument()
  })

  it('has loading spinner', () => {
    render(<Statistics />)
    // Should show loading spinner
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })
})
