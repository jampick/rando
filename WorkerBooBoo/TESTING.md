# 🧪 WorkerBooBoo Testing Guide

This document provides comprehensive information about the testing framework for WorkerBooBoo, including backend API tests, frontend component tests, and how to run them.

## 📋 **Testing Overview**

WorkerBooBoo uses a multi-layered testing approach:

- **Backend**: pytest with FastAPI TestClient
- **Frontend**: Vitest with React Testing Library
- **Coverage**: Built-in coverage reporting for both frameworks
- **Mocking**: Comprehensive mocking for external dependencies

## 🚀 **Quick Start**

### **Backend Tests**
```bash
cd backend

# Install testing dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py maps      # Map-related tests
python run_tests.py stats     # Statistics tests
python run_tests.py incidents # Incident tests
python run_tests.py quick     # Fast tests without coverage
```

### **Frontend Tests**
```bash
cd frontend

# Install testing dependencies
npm install

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## 🔧 **Backend Testing Framework**

### **Test Structure**
```
backend/
├── tests/
│   ├── conftest.py              # Test configuration & fixtures
│   ├── routers/
│   │   ├── test_maps.py         # Map endpoint tests
│   │   ├── test_statistics.py   # Statistics endpoint tests
│   │   └── test_incidents.py    # Incident endpoint tests
│   └── run_tests.py             # Test runner script
├── pytest.ini                   # Pytest configuration
└── requirements.txt              # Testing dependencies
```

### **Key Features**
- **In-memory SQLite database** for isolated tests
- **Sample data fixtures** for consistent testing
- **FastAPI TestClient** for API endpoint testing
- **Comprehensive mocking** of external services
- **Coverage reporting** with HTML output

### **Test Categories**

#### **Map Endpoints (`test_maps.py`)**
- ✅ Basic incident retrieval
- ✅ Filtering by incident type, industry, state
- ✅ Date range filtering
- ✅ Geographic bounds filtering
- ✅ Coordinate validation
- ✅ Clustering and heatmap data
- ✅ Empty database handling

#### **Statistics Endpoints (`test_statistics.py`)**
- ✅ Overview statistics
- ✅ Trend analysis (daily, weekly, monthly, yearly)
- ✅ Geographic distribution
- ✅ Filtering and date ranges
- ✅ Data validation
- ✅ Error handling

#### **Incident Endpoints (`test_incidents.py`)**
- ✅ CRUD operations
- ✅ Pagination and sorting
- ✅ Advanced filtering
- ✅ Search functionality
- ✅ Data validation
- ✅ Error scenarios

### **Running Backend Tests**

#### **Using the Test Runner Script**
```bash
# All tests with coverage
python run_tests.py all

# Specific test categories
python run_tests.py maps
python run_tests.py stats
python run_tests.py incidents

# Quick tests (no coverage)
python run_tests.py quick

# Coverage report
python run_tests.py coverage

# Help
python run_tests.py help
```

#### **Using pytest directly**
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/routers/test_maps.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test function
pytest tests/routers/test_maps.py::test_get_map_incidents_basic -v
```

## 🎨 **Frontend Testing Framework**

### **Test Structure**
```
frontend/
├── src/
│   ├── __tests__/
│   │   └── pages/
│   │       ├── MapView.test.tsx      # Map component tests
│   │       └── Statistics.test.tsx   # Statistics component tests
│   └── test/
│       └── setup.ts                  # Test configuration
├── vite.config.ts                    # Vite + test configuration
└── package.json                      # Testing scripts
```

### **Key Features**
- **Vitest** for fast, modern testing
- **React Testing Library** for component testing
- **Comprehensive mocking** of Mapbox, axios, and router
- **Async testing** with proper waitFor patterns
- **User interaction testing** with fireEvent
- **Coverage reporting** with V8 coverage

### **Test Categories**

#### **MapView Component (`MapView.test.tsx`)**
- ✅ Component rendering
- ✅ API data fetching
- ✅ Filter functionality
- ✅ User interactions
- ✅ Error handling
- ✅ Loading states
- ✅ Coordinate validation

#### **Statistics Component (`Statistics.test.tsx`)**
- ✅ Data display
- ✅ Chart rendering
- ✅ Period switching
- ✅ API integration
- ✅ Error states
- ✅ Loading indicators

### **Running Frontend Tests**

#### **Watch Mode (Development)**
```bash
npm test
```
This runs tests in watch mode, automatically re-running when files change.

#### **Single Run**
```bash
npm run test:run
```
Runs all tests once and exits.

#### **With Coverage**
```bash
npm run test:coverage
```
Generates coverage reports in the `coverage/` directory.

#### **With UI**
```bash
npm run test:ui
```
Opens the Vitest UI for interactive test exploration.

## 📊 **Coverage Reports**

### **Backend Coverage**
```bash
python run_tests.py coverage
```
Generates HTML coverage report in `htmlcov/index.html`

### **Frontend Coverage**
```bash
npm run test:coverage
```
Generates coverage report in `coverage/` directory

## 🧩 **Writing New Tests**

### **Backend Test Template**
```python
def test_new_endpoint_functionality(client: TestClient, sample_incidents):
    """Test description"""
    # Arrange
    endpoint = "/api/new-endpoint"
    expected_data = {...}
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == expected_data
```

### **Frontend Test Template**
```typescript
it('should handle new functionality', async () => {
  // Arrange
  mockedAxios.get.mockResolvedValue({ data: mockData })
  
  // Act
  render(<Component />)
  
  // Assert
  await waitFor(() => {
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## 🔍 **Test Data & Fixtures**

### **Backend Sample Data**
The `conftest.py` file provides sample incident data for testing:
- 3 test incidents with different types
- Valid coordinates for map testing
- Various incident types (fatality, injury, near-miss)
- Different industries and states

### **Frontend Mock Data**
Each test file includes mock data:
- API responses
- Component props
- User interactions

## 🚨 **Common Testing Patterns**

### **API Testing**
```python
# Test successful response
response = client.get("/api/endpoint")
assert response.status_code == 200

# Test error response
response = client.get("/api/endpoint")
assert response.status_code == 404

# Test response data
data = response.json()
assert "expected_field" in data
```

### **Component Testing**
```typescript
// Test rendering
expect(screen.getByText('Expected Text')).toBeInTheDocument()

// Test user interaction
fireEvent.click(screen.getByText('Button'))
expect(screen.getByText('Result')).toBeInTheDocument()

// Test async operations
await waitFor(() => {
  expect(screen.getByText('Loaded Data')).toBeInTheDocument()
})
```

## 🐛 **Troubleshooting**

### **Backend Test Issues**
- **Database errors**: Ensure virtual environment is activated
- **Import errors**: Check that all dependencies are installed
- **Test isolation**: Each test gets a fresh database

### **Frontend Test Issues**
- **Mock errors**: Check that all external dependencies are mocked
- **Async issues**: Use `waitFor` for async operations
- **Component errors**: Ensure all required props are provided

### **Common Solutions**
```bash
# Backend: Reinstall dependencies
pip install -r requirements.txt

# Frontend: Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Both: Check test configuration
python run_tests.py help
npm run test:run
```

## 📈 **Performance & Best Practices**

### **Test Speed**
- **Backend**: In-memory database for fast execution
- **Frontend**: Vitest for fast test runner
- **Parallel execution** where possible

### **Test Quality**
- **Isolation**: Each test is independent
- **Coverage**: Aim for >80% coverage
- **Realistic data**: Use realistic test scenarios
- **Error cases**: Test both success and failure paths

### **Maintenance**
- **Update mocks** when dependencies change
- **Review coverage** regularly
- **Refactor tests** when components change
- **Document complex test scenarios**

## 🎯 **Next Steps**

1. **Run existing tests** to ensure everything works
2. **Add tests** for new features
3. **Improve coverage** in low-coverage areas
4. **Set up CI/CD** for automated testing
5. **Add integration tests** for end-to-end workflows

## 📚 **Additional Resources**

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Happy Testing! 🧪✨**
