package io.automatizacionconvocatorias.sdk;

import java.util.List;
import java.util.Objects;

/**
 * Represents a convocatoria (call for applications/meeting) in the system.
 */
public class Convocatoria {
    private String id;
    private String title;
    private String startDateTime;
    private List<String> attendees;
    private String location;
    private String description;

    // Constructors
    public Convocatoria() {}

    public Convocatoria(String id, String title, String startDateTime, List<String> attendees) {
        this.id = id;
        this.title = title;
        this.startDateTime = startDateTime;
        this.attendees = attendees;
    }

    public Convocatoria(String id, String title, String startDateTime, List<String> attendees, 
                       String location, String description) {
        this.id = id;
        this.title = title;
        this.startDateTime = startDateTime;
        this.attendees = attendees;
        this.location = location;
        this.description = description;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getStartDateTime() {
        return startDateTime;
    }

    public void setStartDateTime(String startDateTime) {
        this.startDateTime = startDateTime;
    }

    public List<String> getAttendees() {
        return attendees;
    }

    public void setAttendees(List<String> attendees) {
        this.attendees = attendees;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Convocatoria that = (Convocatoria) o;
        return Objects.equals(id, that.id) &&
                Objects.equals(title, that.title) &&
                Objects.equals(startDateTime, that.startDateTime) &&
                Objects.equals(attendees, that.attendees) &&
                Objects.equals(location, that.location) &&
                Objects.equals(description, that.description);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, title, startDateTime, attendees, location, description);
    }

    @Override
    public String toString() {
        return "Convocatoria{" +
                "id='" + id + '\'' +
                ", title='" + title + '\'' +
                ", startDateTime='" + startDateTime + '\'' +
                ", attendees=" + attendees +
                ", location='" + location + '\'' +
                ", description='" + description + '\'' +
                '}';
    }
}
