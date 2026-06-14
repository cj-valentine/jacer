using Jacer.ApiClient;

namespace Jacer.Components;

/// <summary>
/// The three status columns shown on the Phase 2 board, in display order.
/// "done" is intentionally excluded from the board for now.
/// </summary>
public static class BoardColumns
{
    public static readonly IReadOnlyList<TaskStatus> Order =
        [TaskStatus.Backlog, TaskStatus.Today, TaskStatus.Scheduled];

    public static string Label(TaskStatus status) => status switch
    {
        TaskStatus.Backlog => "Backlog",
        TaskStatus.Today => "Today",
        TaskStatus.Scheduled => "Scheduled",
        TaskStatus.Done => "Done",
        _ => status.ToString(),
    };

    /// <summary>The board columns a task can move to, i.e. all except its current one.</summary>
    public static IReadOnlyList<TaskStatus> MoveTargetsFor(TaskStatus current) =>
        Order.Where(s => s != current).ToList();
}
