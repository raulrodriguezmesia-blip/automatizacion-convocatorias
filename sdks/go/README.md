# Go SDK for Convocatorias Platform
# Status: Alpha (Planned for Q3 2027)

Package convocatorias provides client library for the Convocatorias Platform API.

## Installation

```bash
go get github.com/automatizacion-convocatorias/convocatorias-sdk/go
```

## Quick Start

```go
package main

import (
    "context"
    "log"
    
    "github.com/automatizacion-convocatorias/convocatorias-sdk/go"
)

func main() {
    client := convocatorias.NewClient(&convocatorias.Config{
        APIKey:  "your-api-key",
        BaseURL: "https://api.convocatorias.io/v1",
    })
    
    // Create convocatoria
    evento, err := client.CreateConvocatoria(context.Background(), &convocatorias.ConvocatoriaRequest{
        Title:        "Reunión de Comité",
        StartDatetime: "2026-08-15T10:00:00",
        Attendees:    []string{"profesor@uni.edu"},
        Location:     "Sala A",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("Created convocatoria ID: %s", evento.ID)
}
```

## Features

- LTI 1.3 integration
- xAPI statement generation  
- Multi-tenant support
- Usage metrics tracking

## License

MIT - same as main platform