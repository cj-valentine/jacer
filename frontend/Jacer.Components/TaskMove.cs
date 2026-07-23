using Jacer.ApiClient;

namespace Jacer.Components;

/// <summary>
/// A request to move a task to a new status column, raised by a card's move
/// buttons and handled by the <c>Board</c> (which issues the PATCH).
/// </summary>
public readonly record struct TaskMove(string TaskId, TaskStatus Target);
