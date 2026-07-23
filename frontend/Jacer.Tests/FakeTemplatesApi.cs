namespace Jacer.Tests;

/// <summary>
/// In-memory <see cref="ITemplatesApi"/> double for bUnit tests. Records created
/// items and serves a fixed template + item set, so the editor can be exercised
/// without an HTTP backend.
/// </summary>
internal sealed class FakeTemplatesApi : ITemplatesApi
{
    private readonly List<TemplateDto> _templates;
    private readonly List<TemplateItemDto> _items;

    public List<TemplateItemCreateDto> CreatedItems { get; } = [];
    public int LockCalls { get; private set; }
    public int UnlockCalls { get; private set; }

    public FakeTemplatesApi(IEnumerable<TemplateDto> templates, IEnumerable<TemplateItemDto> items)
    {
        _templates = templates.ToList();
        _items = items.ToList();
    }

    public Task<IReadOnlyList<TemplateDto>> ListTemplatesAsync(CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<TemplateDto>>(_templates);

    public Task<IReadOnlyList<TemplateItemDto>> ListItemsAsync(string templateId, CancellationToken ct = default) =>
        Task.FromResult<IReadOnlyList<TemplateItemDto>>(_items.Where(i => i.TemplateId == templateId).ToList());

    public Task<TemplateItemDto> CreateItemAsync(string templateId, TemplateItemCreateDto payload, CancellationToken ct = default)
    {
        CreatedItems.Add(payload);
        var created = new TemplateItemDto
        {
            Id = Guid.NewGuid().ToString(),
            TemplateId = templateId,
            DayOfWeek = payload.DayOfWeek,
            Title = payload.Title,
            DurationMinutes = payload.DurationMinutes ?? 30,
            DefaultTime = payload.DefaultTime,
        };
        _items.Add(created);
        return Task.FromResult(created);
    }

    public Task<TemplateDto> CreateTemplateAsync(TemplateCreateDto payload, CancellationToken ct = default)
    {
        var created = TestData.Template(Guid.NewGuid().ToString(), payload.Name);
        _templates.Add(created);
        return Task.FromResult(created);
    }

    public Task<LockResponseDto> LockTemplateAsync(string id, CancellationToken ct = default)
    {
        LockCalls++;
        return Task.FromResult(new LockResponseDto { TemplateId = id, IsLocked = true });
    }

    public Task<LockResponseDto> UnlockTemplateAsync(string id, CancellationToken ct = default)
    {
        UnlockCalls++;
        return Task.FromResult(new LockResponseDto { TemplateId = id, IsLocked = false });
    }

    // Unused by the editor tests.
    public Task<TemplateDto?> GetTemplateAsync(string id, CancellationToken ct = default) =>
        Task.FromResult(_templates.FirstOrDefault(t => t.Id == id));

    public Task<TemplateDto> UpdateTemplateAsync(string id, TemplateUpdateDto payload, CancellationToken ct = default) =>
        Task.FromResult(_templates.First(t => t.Id == id));

    public Task DeleteTemplateAsync(string id, CancellationToken ct = default) => Task.CompletedTask;

    public Task<TemplateItemDto?> GetItemAsync(string itemId, CancellationToken ct = default) =>
        Task.FromResult(_items.FirstOrDefault(i => i.Id == itemId));

    public Task<TemplateItemDto> UpdateItemAsync(string itemId, TemplateItemUpdateDto payload, CancellationToken ct = default) =>
        Task.FromResult(_items.First(i => i.Id == itemId));

    public Task DeleteItemAsync(string itemId, CancellationToken ct = default)
    {
        _items.RemoveAll(i => i.Id == itemId);
        return Task.CompletedTask;
    }
}
