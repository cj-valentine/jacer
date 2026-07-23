using Jacer.ApiClient;

namespace Jacer.Components;

/// <summary>
/// Drag-and-drop view-model wrapping an immutable <see cref="TaskDto"/>. The
/// <see cref="Status"/> here is mutable so MudDropContainer can reflect a move
/// optimistically (before the PATCH round-trips); it is reverted if the PATCH fails.
/// </summary>
public sealed class BoardItem
{
    public required TaskDto Task { get; init; }
    public required TaskStatus Status { get; set; }
}
