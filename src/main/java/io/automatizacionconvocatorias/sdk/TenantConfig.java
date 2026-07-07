package io.automatizacionconvocatorias.sdk;

import java.util.Objects;

/**
 * Configuration for the Convocatorias SDK client.
 */
public class TenantConfig {
    private final String apiKey;
    private final String baseUrl;
    private final int timeout;

    public TenantConfig(String apiKey) {
        this(apiKey, "https://api.convocatorias.io/v1", 30);
    }

    public TenantConfig(String apiKey, String baseUrl, int timeout) {
        this.apiKey = Objects.requireNonNull(apiKey, "API key cannot be null");
        this.baseUrl = Objects.requireNonNullElse(baseUrl, "https://api.convocatorias.io/v1");
        this.timeout = timeout > 0 ? timeout : 30;
    }

    public String getApiKey() {
        return apiKey;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public int getTimeout() {
        return timeout;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TenantConfig that = (TenantConfig) o;
        return timeout == that.timeout &&
                Objects.equals(apiKey, that.apiKey) &&
                Objects.equals(baseUrl, that.baseUrl);
    }

    @Override
    public int hashCode() {
        return Objects.hash(apiKey, baseUrl, timeout);
    }

    @Override
    public String toString() {
        return "TenantConfig{" +
                "apiKey='****', " + // Hidden for security
                "baseUrl='" + baseUrl + '\'' +
                ", timeout=" + timeout +
                '}';
    }
}
