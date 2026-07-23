namespace Jacer.Components;

/// <summary>
/// Time-of-day bands for the weekly templates grid. Template items carry an
/// optional <c>default_time</c> (HH:MM); the grid groups them into bands so a
/// week reads as a small morning/afternoon/evening matrix rather than a raw
/// list. Items with no time fall into <see cref="Anytime"/>.
/// </summary>
public enum TimeBand
{
    Morning,
    Afternoon,
    Evening,
    Anytime,
}

/// <summary>Pure helpers for mapping between times, bands and weekday labels.</summary>
public static class TimeBands
{
    /// <summary>Bands in display order (rows of the grid).</summary>
    public static readonly IReadOnlyList<TimeBand> Order =
        [TimeBand.Morning, TimeBand.Afternoon, TimeBand.Evening, TimeBand.Anytime];

    /// <summary>Weekday labels indexed by the backend's day_of_week (0 = Monday … 6 = Sunday).</summary>
    public static readonly IReadOnlyList<string> DayLabels =
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    public static string Label(TimeBand band) => band switch
    {
        TimeBand.Morning => "Morning",
        TimeBand.Afternoon => "Afternoon",
        TimeBand.Evening => "Evening",
        TimeBand.Anytime => "Anytime",
        _ => band.ToString(),
    };

    /// <summary>
    /// The band a <c>default_time</c> falls into. Null/blank/unparseable → Anytime.
    /// Morning &lt; 12:00 ≤ Afternoon &lt; 17:00 ≤ Evening.
    /// </summary>
    public static TimeBand BandOf(string? defaultTime)
    {
        if (string.IsNullOrWhiteSpace(defaultTime))
        {
            return TimeBand.Anytime;
        }

        var hhmm = defaultTime.Split(':');
        if (hhmm.Length < 1 || !int.TryParse(hhmm[0], out var hour))
        {
            return TimeBand.Anytime;
        }

        return hour switch
        {
            < 12 => TimeBand.Morning,
            < 17 => TimeBand.Afternoon,
            _ => TimeBand.Evening,
        };
    }

    /// <summary>
    /// The default_time a newly-added item gets when created in a band. Anytime
    /// yields null (no scheduled time); other bands seed a representative hour
    /// the user can refine later.
    /// </summary>
    public static string? DefaultTimeFor(TimeBand band) => band switch
    {
        TimeBand.Morning => "09:00",
        TimeBand.Afternoon => "13:00",
        TimeBand.Evening => "18:00",
        _ => null,
    };
}
