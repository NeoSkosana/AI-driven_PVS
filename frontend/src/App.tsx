import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ProblemForm from './pages/ProblemForm';
import ValidationResults from './pages/ValidationResults';

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/validate" element={<ProblemForm />} />
          <Route path="/results/:id" element={<ValidationResults />} />
        </Routes>
      </Box>
    </Box>
  );
};

export default App;
