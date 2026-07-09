namespace Convocatorias.Sdk
{
    /// <summary>
    /// Represents business metrics for a tenant.
    /// </summary>
    public class BusinessMetrics
    {
        public string TenantId { get; set; } = string.Empty;
        public int ConvocatoriasMes { get; set; }
        public double HorasAhorradas { get; set; }
        public double ParticipacionPromedio { get; set; }
        public double? Nps { get; set; }
        public int ApiCallsTotal { get; set; }
        public double ModelAccuracy { get; set; }
        public DateTime? LastUpdated { get; set; }

        public BusinessMetrics() { }

        public BusinessMetrics(string tenantId, int convocatoriasMes, double horasAhorradas,
            double participacionPromedio, double? nps, int apiCallsTotal, double modelAccuracy)
        {
            TenantId = tenantId;
            ConvocatoriasMes = convocatoriasMes;
            HorasAhorradas = horasAhorradas;
            ParticipacionPromedio = participacionPromedio;
            Nps = nps;
            ApiCallsTotal = apiCallsTotal;
            ModelAccuracy = modelAccuracy;
        }

        public override bool Equals(object? obj)
        {
            return obj is BusinessMetrics metrics &&
                   TenantId == metrics.TenantId &&
                   ConvocatoriasMes == metrics.ConvocatoriasMes &&
                   HorasAhorradas == metrics.HorasAhorradas &&
                   ParticipacionPromedio == metrics.ParticipacionPromedio &&
                   Nps == metrics.Nps &&
                   ApiCallsTotal == metrics.ApiCallsTotal &&
                   ModelAccuracy == metrics.ModelAccuracy;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(TenantId, ConvocatoriasMes, HorasAhorradas,
                ParticipacionPromedio, Nps, ApiCallsTotal, ModelAccuracy);
        }

        public override string ToString()
        {
            return \$"BusinessMetrics{{TenantId='{TenantId}', ConvocatoriasMes={ConvocatoriasMes}, HorasAhorradas={HorasAhorradas}}}";
        }
    }
}
