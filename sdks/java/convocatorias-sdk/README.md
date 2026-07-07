# Convocatorias SDK for Java

Official Java SDK for the Convocatorias Platform.

## Installation

Add the dependency to your Maven project:

`xml
<dependency>
    <groupId>io.automatizacionconvocatorias</groupId>
    <artifactId>convocatorias-sdk-java</artifactId>
    <version>1.0.0</version>
</dependency>
`

Or for Gradle:

`groovy
implementation 'io.automatizacionconvocatorias:convocatorias-sdk-java:1.0.0'
`

## Usage

`java
import io.automatizacionconvocatorias.sdk.*;

// Configure the client
TenantConfig config = new TenantConfig("your-api-key-here");
ConvocatoriaClient client = new ConvocatoriaClient(config);

// Create a convocatoria
Convocatoria convocatoria = client.createConvocatoria(
    "Reunión de Comité Académico",
    "2026-08-15T10:00:00",
    java.util.Arrays.asList("profesor@uni.edu", "decano@uni.edu"),
    "Sala de Juntas - Edificio A",
    "Reunión mensual del comité académico"
);

// List convocatorias
List<Convocatoria> convocatorias = client.listConvocatorias();

// Get a specific convocatoria
Convocatoria specific = client.getConvocatoria(convocatoria.getId());

// Process a document
java.util.Map<String, Object> result = client.processDocument(
    "convocatoria_template.pdf",
    true // Use LLM for enhanced processing
);

// Get templates
List<Template> templates = client.getTemplates();

// Get tenant metrics
BusinessMetrics metrics = client.getTenantMetrics();

// Don't forget to close the client when done
client.close();
`

## API Documentation

For detailed API documentation, please refer to the [official API documentation](https://api.convocatorias.io/docs).

## Requirements

- Java 17 or higher
- Maven 3.6+ or Gradle 7+

## License

MIT License
