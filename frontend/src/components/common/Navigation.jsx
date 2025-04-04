import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, Button, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider, Avatar, Menu, MenuItem } from '@mui/material';
import { styled } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import EditNoteIcon from '@mui/icons-material/EditNote';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: 0,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: drawerWidth,
    }),
  }),
);

const Navigation = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const location = useLocation();
  
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };
  
  const menuItems = [
    { text: 'Document Review', icon: <DescriptionIcon />, path: '/documents' },
    { text: 'Legal Research', icon: <SearchIcon />, path: '/research' },
    { text: 'Contract Drafting', icon: <EditNoteIcon />, path: '/contracts' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];
  
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Legal AI Assistant
          </Typography>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>JD</Avatar>
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
          >
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <AccountCircleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Profile</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <List>
            {menuItems.map((item) => (
              <ListItem 
                key={item.text} 
                component={Link} 
                to={item.path}
                button
                selected={location.pathname === item.path}
                sx={{ 
                  color: 'inherit', 
                  textDecoration: 'none',
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.12)',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ 
                  color: location.pathname === item.path ? 'primary.main' : 'inherit' 
                }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              LLM Model
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              fullWidth
              startIcon={<SettingsIcon />}
              component={Link}
              to="/settings"
            >
              GPT-4
            </Button>
          </Box>
        </Box>
      </Drawer>
      
      <Main open={drawerOpen}>
        <Toolbar /> {/* This creates space below the AppBar */}
        {children}
      </Main>
    </Box>
  );
};

export default Navigation;
