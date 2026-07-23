namespace Jacer.Components;

/// <summary>
/// One item placed on a <c>DayTimeline</c>: a positioned block sized by its
/// duration. The component is deliberately agnostic about what the item "is"
/// (a task, a template item) — callers map their domain object to this and
/// render the card body via <c>ItemContent</c>.
/// </summary>
public sealed record TimelineItem
{
    public required string Id { get; init; }
    public required string Title { get; init; }

    /// <summary>Start time as minutes since midnight (e.g. 09:30 → 570).</summary>
    public required int StartMinute { get; init; }

    public required int DurationMinutes { get; init; }

    /// <summary>Category edge colour (hex), or null for uncategorised.</summary>
    public string? Colour { get; init; }

    /// <summary>Whether this item diverges from its template (shows a dot).</summary>
    public bool Diverged { get; init; }
}

/// <summary>Raised when a timeline item is dragged to a new start time.</summary>
public readonly record struct TimelineMove(string ItemId, int StartMinute);

/// <summary>Raised when a timeline item is resized to a new duration.</summary>
public readonly record struct TimelineResize(string ItemId, int DurationMinutes);
