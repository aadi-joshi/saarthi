# SUVIDHA Frontend

React-based kiosk interface for the SUVIDHA digital helpdesk system.

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment

The development server proxies API requests to `http://localhost:8000`. Ensure the backend is running before starting development.

## Structure

```
src/
├── pages/          # Route components
├── components/     # Reusable UI elements
├── context/        # State providers
├── services/       # API integration
├── i18n/           # Translations
└── styles/         # Design system
```
