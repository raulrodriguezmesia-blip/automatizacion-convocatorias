using System.Text.Json.Serialization;

namespace Convocatorias.Sdk
{
    /// <summary>
    /// Represents an integration in the Convocatorias marketplace.
    /// </summary>
    public class Integration
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Provider { get; set; } = string.Empty;
        public Dictionary<string, object>? ConfigSchema { get; set; }
        public string? Description { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        public Integration() { }

        public Integration(string id, string name, string provider)
        {
            Id = id;
            Name = name;
            Provider = provider;
        }

        public Integration(string id, string name, string provider, Dictionary<string, object>? configSchema) : this(id, name, provider)
        {
            ConfigSchema = configSchema;
        }

        public override bool Equals(object? obj)
        {
            return obj is Integration integration &&
                   Id == integration.Id &&
                   Name == integration.Name &&
                   Provider == integration.Provider;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(Id, Name, Provider);
        }

        public override string ToString()
        {
            return \$"Integration{{Id='{Id}', Name='{Name}', Provider='{Provider}'}}";
        }
    }
}
