package io.automatizacionconvocatorias.sdk;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPatch;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.entity.mime.HttpMultipartMode;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * SDK Client for Convocatorias Platform.
 * Provides methods to interact with the Convocatorias API.
 */
public class ConvocatoriaClient implements AutoCloseable {
    private static final String DEFAULT_BASE_URL = "https://api.convocatorias.io/v1";
    private static final String USER_AGENT = "convocatorias-sdk-java/1.0.0";
    
    private final String apiKey;
    private final String baseUrl;
    private final int timeoutSeconds;
    private final CloseableHttpClient httpClient;
    private final ObjectMapper objectMapper;

    /**
     * Creates a new ConvocatoriaClient with the given configuration.
     *
     * @param apiKey   The API key for authentication
     * @param baseUrl  The base URL of the API (optional, defaults to production)
     * @param timeout  Request timeout in seconds (optional, defaults to 30)
     */
    public ConvocatoriaClient(String apiKey, String baseUrl, int timeout) {
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("API key cannot be null or empty");
        }
        this.apiKey = apiKey;
        this.baseUrl = (baseUrl == null || baseUrl.isEmpty()) ? DEFAULT_BASE_URL : baseUrl;
        this.timeoutSeconds = timeout > 0 ? timeout : 30;
        this.httpClient = HttpClients.custom()
                .setUserAgent(USER_AGENT)
                .setDefaultRequestConfig(
                        org.apache.http.client.config.RequestConfig.custom()
                                .setConnectTimeout(this.timeoutSeconds * 1000)
                                .setConnectionRequestTimeout(this.timeoutSeconds * 1000)
                                .setSocketTimeout(this.timeoutSeconds * 1000)
                                .build()
                )
                .build();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Creates a new ConvocatoriaClient with default timeout (30 seconds).
     *
     * @param apiKey   The API key for authentication
     * @param baseUrl  The base URL of the API (optional, defaults to production)
     */
    public ConvocatoriaClient(String apiKey, String baseUrl) {
        this(apiKey, baseUrl, 30);
    }

    /**
     * Creates a new ConvocatoriaClient with default base URL and timeout.
     *
     * @param apiKey The API key for authentication
     */
    public ConvocatoriaClient(String apiKey) {
        this(apiKey, null, 30);
    }

    /**
     * Internal method to execute HTTP requests and parse JSON responses.
     *
     * @param method  HTTP method (GET, POST, PATCH, DELETE)
     * @param path    API endpoint path
     * @param entity  Request entity (can be null for GET/DELETE)
     * @param <T>     Response type
     * @return Parsed response object
     * @throws IOException If there is an error with the HTTP request or response parsing
     */
    private <T> T executeRequest(String method, String path, HttpEntity entity, Class<T> responseType) throws IOException {
        String url = baseUrl + path;
        
        // Create appropriate HTTP request based on method
        org.apache.http.client.methods.CloseableHttpRequest httpRequest;
        switch (method.toUpperCase()) {
            case "GET":
                httpRequest = new HttpGet(url);
                break;
            case "POST":
                httpRequest = new HttpPost(url);
                break;
            case "PATCH":
                httpRequest = new HttpPatch(url);
                break;
            case "DELETE":
                httpRequest = new HttpDelete(url);
                break;
            default:
                throw new IllegalArgumentException("Unsupported HTTP method: " + method);
        }

        // Set headers
        httpRequest.setHeader("Authorization", "Bearer " + apiKey);
        httpRequest.setHeader("Accept", "application/json");
        if (entity != null) {
            httpRequest.setHeader("Content-Type", "application/json");
        }
        httpRequest.setHeader("User-Agent", USER_AGENT);

        // Set entity if provided
        if (entity != null) {
            if (httpRequest instanceof HttpPost) {
                ((HttpPost) httpRequest).setEntity(entity);
            } else if (httpRequest instanceof HttpPatch) {
                ((HttpPatch) httpRequest).setEntity(entity);
            }
        }

        // Execute request
        try (CloseableHttpResponse response = httpClient.execute(httpRequest)) {
            int statusCode = response.getStatusLine().getStatusCode();
            HttpEntity responseEntity = response.getEntity();
            
            // Consume entity to avoid connection leaks
            try {
                if (statusCode >= 200 && statusCode < 300) {
                    if (responseEntity != null) {
                        String responseString = EntityUtils.toString(responseEntity, StandardCharsets.UTF_8);
                        if (responseString.trim().isEmpty()) {
                            return null;
                        }
                        return objectMapper.readValue(responseString, responseType);
                    } else {
                        return null;
                    }
                } else {
                    String errorMessage = "HTTP " + statusCode;
                    if (responseEntity != null) {
                        errorMessage += ": " + EntityUtils.toString(responseEntity, StandardCharsets.UTF_8);
                    }
                    throw new IOException(errorMessage);
                }
            } finally {
                EntityUtils.consume(responseEntity);
            }
        }
    }

    /**
     * Creates a convocatoria event with calendar integration.
     *
     * @param title           Title of the convocatoria
     * @param startDateTime   Start date and time in ISO 8601 format
     * @param attendees       List of attendee email addresses
     * @param location        Optional location
     * @param description     Optional description
     * @return Created convocatoria
     * @throws IOException If there is an error with the API request
     */
    public Convocatoria createConvocatoria(String title, String startDateTime,
                                          List<String> attendees,
                                          String location,
                                          String description) throws IOException {
        Convocatoria convocatoria = new Convocatoria();
        convocatoria.setTitle(title);
        convocatoria.setStartDateTime(startDateTime);
        convocatoria.setAttendees(attendees);
        convocatoria.setLocation(location);
        convocatoria.setDescription(description);
        
        String json = objectMapper.writeValueAsString(convocatoria);
        HttpEntity entity = new StringEntity(json, ContentType.APPLICATION_JSON);
        
        return executeRequest("POST", "/convocatorias", entity, Convocatoria.class);
    }

    /**
     * Overloaded method for creating a convocatoria without optional parameters.
     */
    public Convocatoria createConvocatoria(String title, String startDateTime,
                                          List<String> attendees) throws IOException {
        return createConvocatoria(title, startDateTime, attendees, null, null);
    }

    /**
     * Lists convocatorias for the tenant.
     *
     * @param limit Maximum number of convocatorias to return (default 50)
     * @return List of convocatorias
     * @throws IOException If there is an error with the API request
     */
    public List<Convocatoria> listConvocatorias(int limit) throws IOException {
        Convocatoria[] convocatoriasArray = executeRequest(
                "GET",
                "/convocatorias?limit=" + limit,
                null,
                Convocatoria[].class
        );
        return convocatoriasArray != null ? Arrays.asList(convocatoriasArray) : new ArrayList<>();
    }

    /**
     * Overloaded method with default limit of 50.
     */
    public List<Convocatoria> listConvocatorias() throws IOException {
        return listConvocatorias(50);
    }

    /**
     * Gets a specific convocatoria by ID.
     *
     * @param convocatoriaId The ID of the convocatoria to retrieve
     * @return The convocatoria
     * @throws IOException If there is an error with the API request
     */
    public Convocatoria getConvocatoria(String convocatoriaId) throws IOException {
        return executeRequest("GET", "/convocatorias/" + convocatoriaId, null, Convocatoria.class);
    }

    /**
     * Updates a convocatoria with the provided fields.
     *
     * @param convocatoriaId The ID of the convocatoria to update
     * @param updates        Map of fields to update (key = field name, value = new value)
     * @return Updated convocatoria
     * @throws IOException If there is an error with the API request
     */
    public Convocatoria updateConvocatoria(String convocatoriaId, Map<String, Object> updates) throws IOException {
        String json = objectMapper.writeValueAsString(updates);
        HttpEntity entity = new StringEntity(json, ContentType.APPLICATION_JSON);
        
        return executeRequest("PATCH", "/convocatorias/" + convocatoriaId, entity, Convocatoria.class);
    }

    /**
     * Processes a document and generates a draft using AI (if requested).
     *
     * @param filePath Path to the document file to process
     * @param useLLM   Whether to use LLM for enhanced processing
     * @return Processing result as a map
     * @throws IOException If there is an error with the API request or file access
     */
    public Map<String, Object> processDocument(String filePath, boolean useLLM) throws IOException {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new IllegalArgumentException("File not found: " + filePath);
        }
        
        MultipartEntityBuilder builder = MultipartEntityBuilder.create();
        builder.setMode(HttpMultipartMode.BROWSER_COMPATIBLE);
        builder.addBinaryBody("file", file);
        builder.addTextBody("use_llm", Boolean.toString(useLLM), ContentType.TEXT_PLAIN);
        
        HttpEntity entity = builder.build();
        
        @SuppressWarnings("unchecked")
        Map<String, Object> result = executeRequest(
                "POST",
                "/documents/process",
                entity,
                Map.class
        );
        
        return result != null ? result : new java.util.HashMap<>();
    }

    /**
     * Overloaded method for processDocument with default LLM usage (false).
     */
    public Map<String, Object> processDocument(String filePath) throws IOException {
        return processDocument(filePath, false);
    }

    /**
     * Gets templates from the marketplace, optionally filtered by category.
     *
     * @param category Optional category to filter by
     * @return List of templates
     * @throws IOException If there is an error with the API request
     */
    public List<Template> getTemplates(String category) throws IOException {
        String path = "/templates";
        if (category != null && !category.isEmpty()) {
            path += "?category=" + java.net.URLEncoder.encode(category, StandardCharsets.UTF_8);
        }
        
        Template[] templatesArray = executeRequest(
                "GET",
                path,
                null,
                Template[].class
        );
        return templatesArray != null ? Arrays.asList(templatesArray) : new ArrayList<>();
    }

    /**
     * Overloaded method for getting all templates.
     */
    public List<Template> getTemplates() throws IOException {
        return getTemplates(null);
    }

    /**
     * Gets business metrics for the tenant.
     *
     * @return Business metrics
     * @throws IOException If there is an error with the API request
     */
    public BusinessMetrics getTenantMetrics() throws IOException {
        return executeRequest("GET", "/tenant/metrics", null, BusinessMetrics.class);
    }

    /**
     * Closes the HTTP client and releases resources.
     */
    @Override
    public void close() throws IOException {
        httpClient.close();
    }
}
