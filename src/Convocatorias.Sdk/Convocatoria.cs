using System;
using System.Collections.Generic;

namespace Convocatorias.Sdk
{
    /// <summary>
    /// Represents a convocatoria (call for applications/meeting) in the system.
    /// </summary>
    public class Convocatoria
    {
        public string Id { get; set; }
        public string Title { get; set; }
        public string StartDateTime { get; set; }
        public List<string> Attendees { get; set; } = new List<string>();
        public string Location { get; set; }
        public string Description { get; set; }

        public Convocatoria() { }

        public Convocatoria(string id, string title, string startDateTime, List<string> attendees)
        {
            Id = id;
            Title = title;
            StartDateTime = startDateTime;
            Attendees = attendees ?? new List<string>();
        }

        public Convocatoria(string id, string title, string startDateTime, List<string> attendees,
                            string location, string description)
        {
            Id = id;
            Title = title;
            StartDateTime = startDateTime;
            Attendees = attendees ?? new List<string>();
            Location = location;
            Description = description;
        }
    }
}
