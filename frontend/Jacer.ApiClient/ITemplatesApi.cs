namespace Jacer.ApiClient;

/// <summary>
/// Typed client for the frozen Jacer template endpoints. Templates live under
/// <c>/api/templates/</c> (collection routes keep their trailing slash); items
/// are created/listed nested under a template but read/updated/deleted via the
/// flat <c>/api/template-items/{id}</c> routes, matching the FastAPI contract.
/// </summary>
public interface ITemplatesApi
{
    Task<IReadOnlyList<TemplateDto>> ListTemplatesAsync(CancellationToken ct = default);

    Task<TemplateDto> CreateTemplateAsync(TemplateCreateDto payload, CancellationToken ct = default);

    Task<TemplateDto?> GetTemplateAsync(string id, CancellationToken ct = default);

    Task<TemplateDto> UpdateTemplateAsync(string id, TemplateUpdateDto payload, CancellationToken ct = default);

    Task DeleteTemplateAsync(string id, CancellationToken ct = default);

    Task<LockResponseDto> LockTemplateAsync(string id, CancellationToken ct = default);

    Task<LockResponseDto> UnlockTemplateAsync(string id, CancellationToken ct = default);

    // Items

    Task<IReadOnlyList<TemplateItemDto>> ListItemsAsync(string templateId, CancellationToken ct = default);

    Task<TemplateItemDto> CreateItemAsync(
        string templateId,
        TemplateItemCreateDto payload,
        CancellationToken ct = default);

    Task<TemplateItemDto?> GetItemAsync(string itemId, CancellationToken ct = default);

    Task<TemplateItemDto> UpdateItemAsync(
        string itemId,
        TemplateItemUpdateDto payload,
        CancellationToken ct = default);

    /// <summary>
    /// Set (or clear, with null) a template item's category. A dedicated call
    /// because clearing needs an explicit <c>category_id: null</c>, which the
    /// null-omitting partial-update DTO can't express.
    /// </summary>
    Task<TemplateItemDto> SetItemCategoryAsync(string itemId, string? categoryId, CancellationToken ct = default);

    Task DeleteItemAsync(string itemId, CancellationToken ct = default);
}
