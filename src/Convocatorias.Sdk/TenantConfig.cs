using System;

namespace Convocatorias.Sdk
{
    /// <summary>
    /// Configuration for the Convocatorias SDK client.
    /// </summary>
    public class TenantConfig
    {
        public string ApiKey { get; }
        public string BaseUrl { get; }
        public int Timeout { get; }

        public TenantConfig(string apiKey)
            : this(apiKey, "https://api.convocatorias.io/v1", 30) { }

        public TenantConfig(string apiKey, string baseUrl, int timeout)
        {
            ApiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            BaseUrl = string.IsNullOrEmpty(baseUrl) ? "https://api.convocatorias.io/v1" : baseUrl;
            Timeout = timeout > 0 ? timeout : 30;
        }
    }
}
