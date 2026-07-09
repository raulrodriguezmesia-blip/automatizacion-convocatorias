using System.Text.Json.Serialization;

namespace Convocatorias.Sdk
{
    /// <summary>
    /// Represents a template in the Convocatorias marketplace.
    /// </summary>
    public class Template
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public string? Description { get; set; }
        public int Version { get; set; } = 1;
        public bool IsActive { get; set; } = true;
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        public Template() { }

        public Template(string id, string name, string category, string content)
        {
            Id = id;
            Name = name;
            Category = category;
            Content = content;
        }

        public Template(string id, string name, string category, string content, string? description) : this(id, name, category, content)
        {
            Description = description;
        }

        public override bool Equals(object? obj)
        {
            return obj is Template template &&
                   Id == template.Id &&
                   Name == template.Name &&
                   Category == template.Category &&
                   Content == template.Content;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(Id, Name, Category, Content);
        }

        public override string ToString()
        {
            return \$"Template{{Id='{Id}', Name='{Name}', Category='{Category}'}}";
        }
    }
}
