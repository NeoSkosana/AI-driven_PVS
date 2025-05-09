import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const Navbar: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            textDecoration: 'none',
            color: 'inherit',
            flexGrow: 1,
          }}
        >
          Problem Validation System
        </Typography>
        <Box>
          <Button
            component={RouterLink}
            to="/validate"
            color="inherit"
            startIcon={<AddIcon />}
          >
            New Validation
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
