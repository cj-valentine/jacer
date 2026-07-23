namespace Jacer.ApiClient;

/// <summary>
/// Typed client for the additive categories endpoints (<c>/api/categories/</c>,
/// Phase 3.5). Collection routes keep their trailing slash, matching the rest of
/// the FastAPI contract.
/// </summary>
public interface ICategoriesApi
{
    Task<IReadOnlyList<CategoryDto>> ListCategoriesAsync(CancellationToken ct = default);

    /// <summary>The fixed muted palette (hex strings) category colours are drawn from.</summary>
    Task<IReadOnlyList<string>> GetPaletteAsync(CancellationToken ct = default);

    Task<CategoryDto> CreateCategoryAsync(CategoryCreateDto payload, CancellationToken ct = default);

    Task<CategoryDto> UpdateCategoryAsync(string id, CategoryUpdateDto payload, CancellationToken ct = default);

    Task DeleteCategoryAsync(string id, CancellationToken ct = default);
}
