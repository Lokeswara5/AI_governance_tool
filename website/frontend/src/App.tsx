import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './theme';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Policies from './pages/Policies';
import Analysis from './pages/Analysis';
import Settings from './pages/Settings';
import Organizations from './pages/Organizations';
import Users from './pages/Users';

// Create React Query client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/policies" element={<Policies />} />
              <Route path="/analysis/:id" element={<Analysis />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/organizations" element={<Organizations />} />
              <Route path="/users" element={<Users />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;