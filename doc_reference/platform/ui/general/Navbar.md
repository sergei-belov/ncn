# Navbar Component

## Description
The navbar component provides primary navigation across the platform (except on special pages like authentication).

## Features
- Contains logo and branding on the left
- Includes search functionality
- Shows quick access to user profile and settings
- Responsive design for different screen sizes

## Usage Example
```
<VAppBar>
  <VToolbarTitle>QAi Platform</VToolbarTitle>
  <VSpacer />
  <NavbarMenu />
  <UserButton />
</VAppBar>
```

## Design Guidelines
- Should be fixed at the top of the screen on most pages
- Contains essential platform-wide navigation elements
- Responsive behavior on smaller screens

## Links to Screens
- [Projects List](../pages/ProjectsListScreen.md) (URL: `/qai/projects`) - Back to main project list
- [Project Detail](../pages/ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - View project details and statistics
- [Pipelines](../pages/PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - View and manage test case pipelines
- Project Settings - Current placeholder route documented in the frontend application spec
