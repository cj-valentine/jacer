namespace Jacer.Components;

/// <summary>
/// Pure helpers for the timeline grid: converting between <c>HH:MM</c> strings
/// (the backend's <c>scheduled_time</c> / <c>default_time</c>) and minutes since
/// midnight, and mapping minutes onto 30-minute slots. Kept separate from the
/// component so the arithmetic is unit-testable without rendering.
/// </summary>
public static class TimelineGrid
{
    /// <summary>Minutes since midnight for an <c>HH:MM</c> string; null if absent/unparseable.</summary>
    public static int? MinutesFromHhMm(string? hhmm)
    {
        if (string.IsNullOrWhiteSpace(hhmm))
        {
            return null;
        }

        var parts = hhmm.Split(':');
        if (parts.Length < 2
            || !int.TryParse(parts[0], out var hour)
            || !int.TryParse(parts[1], out var minute))
        {
            return null;
        }

        if (hour is < 0 or > 23 || minute is < 0 or > 59)
        {
            return null;
        }

        return hour * 60 + minute;
    }

    /// <summary>An <c>HH:MM</c> string for minutes since midnight (clamped to a day).</summary>
    public static string HhMmFromMinutes(int minutes)
    {
        var clamped = Math.Clamp(minutes, 0, 24 * 60 - 1);
        return $"{clamped / 60:D2}:{clamped % 60:D2}";
    }

    /// <summary>Number of slots in the window [startHour, endHour) at the given slot size.</summary>
    public static int SlotCount(int startHour, int endHour, int slotMinutes) =>
        Math.Max(0, (endHour - startHour) * 60 / slotMinutes);

    /// <summary>Start-of-day minute for slot <paramref name="slotIndex"/> in the window.</summary>
    public static int SlotStartMinute(int startHour, int slotIndex, int slotMinutes) =>
        startHour * 60 + slotIndex * slotMinutes;
}
