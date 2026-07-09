package io.automatizacionconvocatorias.sdk;

import java.util.Map;
import java.util.Objects;

/**
 * Represents an integration in the Convocatorias marketplace.
 */
public class Integration {
    private String id;
    private String name;
    private String provider;
    private Map<String, Object> configSchema;

    // Constructors
    public Integration() {}

    public Integration(String id, String name, String provider, Map<String, Object> configSchema) {
        this.id = id;
        this.name = name = name;
        this.name = name;
        this.provider = provider;
        this.configSchema = configSchema;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public Map<String, Object> getConfigSchema() {
        return configSchema;
    }

    public void setConfigSchema(Map<String, Object> configSchema) {
        this.configSchema = configSchema;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Integration that = (Integration) o;
        return Objects.equals(id, that.id) &&
                Objects.equals(name, that.name) &&
                Objects.equals(provider, that.provider) &&
                Objects.equals(configSchema, that.configSchema);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, provider, configSchema);
    }

    @Override
    public String toString() {
        return "Integration{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", provider='" + provider + '\'' +
                ", configSchema=" + configSchema +
                '}';
    }
}
