import React from 'react';
import { AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider, IconButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';

const drawerWidth = 240;

const AppBarStyled = styled(AppBar)(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
}));

const DrawerStyled = styled(Drawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
  },
}));

function Navigation() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Document Analysis', icon: <DescriptionIcon />, path: '/documents' },
    { text: 'Legal Research', icon: <SearchIcon />, path: '/research' },
    { text: 'Contract Generation', icon: <AssignmentIcon />, path: '/contracts' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const drawer = (
    <>
      <Toolbar />
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text} component={RouterLink} to={item.path}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </>
  );

  return (
    <>
      <AppBarStyled position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Legal AI Assistant
          </Typography>
        </Toolbar>
      </AppBarStyled>
      <DrawerStyled
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
        }}
        open
      >
        {drawer}
      </DrawerStyled>
    </>
  );
}

export default Navigation;
