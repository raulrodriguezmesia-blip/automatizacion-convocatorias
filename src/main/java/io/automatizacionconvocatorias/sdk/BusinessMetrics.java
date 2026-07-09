package io.automatizacionconvocatorias.sdk;

import java.util.Objects;

/**
 * Represents business metrics for a tenant.
 */
public class BusinessMetrics {
    private String tenantId;
    private int convocatoriasMes;
    private double horasAhorradas;
    private double participacionPromedio;
    private Double nps; // Can be null
    private int apiCallsTotal;
    private double modelAccuracy;

    // Constructors
    public BusinessMetrics() {}

    public BusinessMetrics(String tenantId, int convocatoriasMes, double horasAhorradas,
                          double participacionPromedio, Double nps, int apiCallsTotal,
                          double modelAccuracy) {
        this.tenantId = tenantId;
        this.convocatoriasMes = convocatoriasMes;
        this.horasAhorradas = horasAhorradas;
        this.participacionPromedio = participacionPromedio;
        this.nps = nps;
        this.apiCallsTotal = apiCallsTotal;
        this.modelAccuracy = modelAccuracy;
    }

    // Getters and Setters
    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public int getConvocatoriasMes() {
        return convocatoriasMes;
    }

    public void setConvocatoriasMes(int convocatoriasMes) {
        this.convocatoriasMes = convocatoriasMes;
    }

    public double getHorasAhorradas() {
        return horasAhorradas;
    }

    public void setHorasAhorradas(double horasAhorradas) {
        this.horasAhorradas = horasAhorradas;
    }

    public double getParticipacionPromedio() {
        return participacionPromedio;
    }

    public void setParticipacionPromedio(double participacionPromedio) {
        this.participacionPromedio = participacionPromedio;
    }

    public Double getNps() {
        return nps;
    }

    public void setNps(Double nps) {
        this.nps = nps;
    }

    public int getApiCallsTotal() {
        return apiCallsTotal;
    }

    public void setApiCallsTotal(int apiCallsTotal) {
        this.apiCallsTotal = apiCallsTotal;
    }

    public double getModelAccuracy() {
        return modelAccuracy;
    }

    public void setModelAccuracy(double modelAccuracy) {
        this.modelAccuracy = modelAccuracy;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        BusinessMetrics that = (BusinessMetrics) o;
        return convocatoriasMes == that.convocatoriasMes &&
                Double.compare(that.horasAhorradas, horasAhorradas) == 0 &&
                Double.compare(that.participacionPromedio, participacionPromedio) == 0 &&
                Objects.equals(nps, that.nps) &&
                apiCallsTotal == that.apiCallsTotal &&
                Double.compare(that.modelAccuracy, modelAccuracy) == 0 &&
                Objects.equals(tenantId, that.tenantId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(tenantId, convocatoriasMes, horasAhorradas,
                participacionPromedio, nps, apiCallsTotal, modelAccuracy);
    }

    @Override
    public String toString() {
        return "BusinessMetrics{" +
                "tenantId='" + tenantId + '\'' +
                ", convocatoriasMes=" + convocatoriasMes +
                ", horasAhorradas=" + horasAhorradas +
                ", participacionPromedio=" + participacionPromedio +
                ", nps=" + nps +
                ", apiCallsTotal=" + apiCallsTotal +
                ", modelAccuracy=" + modelAccuracy +
                '}';
    }
}
