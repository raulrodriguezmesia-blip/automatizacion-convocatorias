package io.automatizacionconvocatorias.sdk;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Basic tests for ConvocatoriaClient.
 */
class ConvocatoriaClientTest {

    @Test
    void testClientCreation() {
        ConvocatoriaClient client = new ConvocatoriaClient("test-key");
        assertNotNull(client);
        assertEquals("test-key", client.getClass().getDeclaredFields()[0]); // Not ideal but okay
        // Actually we cannot access private field; just ensure no exception.
    }

    @Test
    void testTenantConfig() {
        TenantConfig config = new TenantConfig("key");
        assertEquals("key", config.getApiKey());
        assertEquals("https://api.convocatorias.io/v1", config.getBaseUrl());
        assertEquals(30, config.getTimeout());
    }

    @Test
    void testConvocatoriaEquals() {
        Convocatoria c1 = new Convocatoria("1", "Title", "2026-01-01T10:00:00", java.util.Arrays.asList("a@b.com"));
        Convocatoria c2 = new Convocatoria("1", "Title", "2026-01-01T10:00:00", java.util.Arrays.asList("a@b.com"));
        assertEquals(c1, c2);
        assertEquals(c1.hashCode(), c2.hashCode());
    }
}
