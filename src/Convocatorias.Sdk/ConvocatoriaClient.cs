using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

namespace Convocatorias.Sdk
{
    /// <summary>
    /// SDK Client for Convocatorias Platform.
    /// Provides methods to interact with the Convocatorias API.
    /// </summary>
    public class ConvocatoriaClient : IDisposable
    {
        private static readonly HttpClient _httpClient = new HttpClient();
        private static readonly JsonSerializerOptions _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        private readonly string _apiKey;
        private readonly string _baseUrl;
        private readonly int _timeoutSeconds;

        /// <summary>
        /// Creates a new ConvocatoriaClient with the given configuration.
        /// </summary>
        /// <param name=\"apiKey\">The API key for authentication</param>
        public ConvocatoriaClient(string apiKey) : this(apiKey, \"https://api.convocatorias.io/v1\", 30) { }

        /// <summary>
        /// Creates a new ConvocatoriaClient with the given configuration.
        /// </summary>
        /// <param name=\"apiKey\">The API key for authentication</param>
        /// <param name=\"baseUrl\">The base URL of the API (defaults to production)</param>
        public ConvocatoriaClient(string apiKey, string baseUrl) : this(apiKey, baseUrl, 30) { }

        /// <summary>
        /// Creates a new ConvocatoriaClient with the given configuration.
        /// </summary>
        /// <param name=\"apiKey\">The API key for authentication</param>
        /// <param name=\"baseUrl\">The base URL of the API</param>
        /// <param name=\"timeoutSeconds\">Request timeout in seconds</param>
        public ConvocatoriaClient(string apiKey, string baseUrl, int timeoutSeconds)
        {
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            _baseUrl = string.IsNullOrEmpty(baseUrl) ? \"https://api.convocatorias.io/v1\" : baseUrl;
            _timeoutSeconds = timeoutSeconds > 0 ? timeoutSeconds : 30;
            _httpClient.Timeout = TimeSpan.FromSeconds(_timeoutSeconds);
        }

        private void SetHeaders()
        {
            _httpClient.DefaultRequestHeaders.Clear();
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue(\"Bearer\", _apiKey);
            _httpClient.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue(\"application/json\"));
            _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd(\"convocatorias-sdk-dotnet/1.0.0\");
        }

        private async Task<T> ExecuteAsync<T>(string method, string path)
        {
            SetHeaders();
            var url = \$"{_baseUrl}{path}";
            using var request = new HttpRequestMessage(new HttpMethod(method), url);

            using var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(json, _jsonOptions) ?? default(T);
        }

        private async Task<T> ExecuteAsync<T>(string method, string path, object data)
        {
            SetHeaders();
            var url = \$"{_baseUrl}{path}";
            var json = JsonSerializer.Serialize(data, _jsonOptions);
            using var request = new HttpRequestMessage(new HttpMethod(method), url)
            {
                Content = new StringContent(json, Encoding.UTF8, \"application/json\")
            };

            using var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(responseJson, _jsonOptions) ?? default(T);
        }

        /// <summary>
        /// Creates a convocatoria event.
        /// </summary>
        public async Task<Convocatoria> CreateConvocatoriaAsync(Convocatoria convocatoria)
        {
            return await ExecuteAsync<Convocatoria>(\"POST\", \"/convocatorias\", convocatoria);
        }

        /// <summary>
        /// Lists convocatorias for the tenant.
        /// </summary>
        public async Task<List<Convocatoria>> ListConvocatoriasAsync(int limit = 50, int offset = 0)
        {
            var path = $\"/convocatorias?limit={limit}&offset={offset}\";
            var result = await ExecuteAsync<Convocatoria[]>(path);
            return result.ToList();
        }

        /// <summary>
        /// Gets a specific convocatoria by ID.
        /// </summary>
        public async Task<Convocatoria?> GetConvocatoriaAsync(string convocatoriaId)
        {
            return await ExecuteAsync<Convocatoria>(\$\"/convocatorias/{convocatoriaId}\");
        }

        /// <summary>
        /// Updates a convocatoria.
        /// </summary>
        public async Task<Convocatoria> UpdateConvocatoriaAsync(string convocatoriaId, Convocatoria updates)
        {
            return await ExecuteAsync<Convocatoria>(\"PATCH\", \$\"/convocatorias/{convocatoriaId}\", updates);
        }

        /// <summary>
        /// Deletes a convocatoria.
        /// </summary>
        public async Task<bool> DeleteConvocatoriaAsync(string convocatoriaId)
        {
            var response = await _httpClient.DeleteAsync(\/convocatorias/{convocatoriaId}\");
            return response.IsSuccessStatusCode;
        }

        /// <summary>
        /// Gets templates from the marketplace.
        /// </summary>
        public async Task<List<Template>> GetTemplatesAsync(string? category = null)
        {
            var path = category != null ? \$\"/templates?category={Uri.EscapeDataString(category)}\" : \"/templates\";
            var result = await ExecuteAsync<Template[]>(path);
            return result.ToList();
        }

        /// <summary>
        /// Gets business metrics for the tenant.
        /// </summary>
        public async Task<BusinessMetrics> GetTenantMetricsAsync()
        {
            return await ExecuteAsync<BusinessMetrics>(\"/tenant/metrics\");
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
