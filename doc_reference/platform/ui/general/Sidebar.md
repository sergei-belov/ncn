# Sidebar Component

## Description
The sidebar component provides secondary navigation and project-specific options.

## Features
- Contains project-specific menu items
- Collapsible for space efficiency
- Shows active project and related options
- Responsive behavior on smaller screens

## Usage Example
```
<VNavigationDrawer v-model="drawer" app clipped>
  <VList>
    <VListItem link>
      <VListItemIcon><VIcon>dashboard</VIcon></VListItemIcon>
      <VListItemTitle>Dashboard</VListItemTitle>
    </VListItem>
  </VList>
</VNavigationDrawer>
```

## Design Guidelines
- Typically located on the left side of the screen
- Appears on project-related pages
- Collapsible for better screen utilization
- Maintains consistent styling across the platform