namespace Jacer.Components;

/// <summary>
/// Per-session board UI state that should survive navigating away and back
/// (registered scoped, so it lives for the Blazor Server circuit = the session).
/// Holds which collapsible groups are open — the tasks themselves always come
/// fresh from the API.
/// </summary>
public sealed class BoardUiState
{
    /// <summary>Upcoming group starts expanded (Amendment 1); the user can collapse it.</summary>
    public bool UpcomingExpanded { get; set; } = true;

    private readonly HashSet<string> _collapsedCategories = [];

    public bool IsCategoryCollapsed(string key) => _collapsedCategories.Contains(key);

    public void ToggleCategory(string key)
    {
        if (!_collapsedCategories.Add(key))
        {
            _collapsedCategories.Remove(key);
        }
    }
}
