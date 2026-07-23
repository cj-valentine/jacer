namespace Jacer.Components;

/// <summary>
/// A request to bump a task forward by a number of days, raised by a card's
/// bump gestures ("→ Tomorrow" = 1, "→ Next week" = 7) and handled by the
/// <c>Board</c>, which sets scheduled_date accordingly and moves it to Scheduled.
/// </summary>
public readonly record struct TaskBump(string TaskId, int DaysAhead);
