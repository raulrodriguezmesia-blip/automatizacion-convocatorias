package io.automatizacionconvocatorias.sdk;

import java.util.Objects;

/**
 * Represents a template in the Convocatorias marketplace.
 */
public class Template {
    private String id;
    private String name;
    private String category;
    private String content;

    // Constructors
    public Template() {}

    public Template(String id, String name, String category, String content) {
        this.id = id;
        this.name = name;
        this.category = category;
        this.content = content;
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

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Template template = (Template) o;
        return Objects.equals(id, template.id) &&
                Objects.equals(name, template.name) &&
                Objects.equals(category, template.category) &&
                Objects.equals(content, template.content);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, category, content);
    }

    @Override
    public String toString() {
        return "Template{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", category='" + category + '\'' +
                ", content='" + content + '\'' +
                '}';
    }
}
