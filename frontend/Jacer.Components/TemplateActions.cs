namespace Jacer.Components;

/// <summary>In-place edit of a template item's title.</summary>
public readonly record struct TemplateTitleEdit(string ItemId, string Title);

/// <summary>In-place edit of a template item's duration (minutes).</summary>
public readonly record struct TemplateDurationEdit(string ItemId, int Minutes);

/// <summary>Assign a template item to a category, or clear it (null).</summary>
public readonly record struct TemplateCategoryAssignment(string ItemId, string? CategoryId);
