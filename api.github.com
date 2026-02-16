{
  "openapi": "3.1.1",
  "info": {
    "title": "Li+ GitHub Unified I/O",
    "description": "Issue + PR + CI Polling + Git Data API (Full Compatible / No Base64)",
    "version": "0.1.0"
  },
  "servers": [
    { "url": "https://api.github.com" }
  ],
  "components": {
    "schemas": {},
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    }
  },
  "security": [
    { "BearerAuth": [] }
  ],
  "paths": { }
}