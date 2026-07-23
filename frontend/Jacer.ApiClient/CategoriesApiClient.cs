using System.Net.Http.Json;

namespace Jacer.ApiClient;

/// <inheritdoc cref="ICategoriesApi"/>
public sealed class CategoriesApiClient(HttpClient http) : ICategoriesApi
{
    // Collection route keeps its trailing slash on purpose (avoids FastAPI's
    // 307 redirect, which drops POST bodies).
    private const string Collection = "api/categories/";

    public async Task<IReadOnlyList<CategoryDto>> ListCategoriesAsync(CancellationToken ct = default)
    {
        var result = await http.GetFromJsonAsync<List<CategoryDto>>(Collection, JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<IReadOnlyList<string>> GetPaletteAsync(CancellationToken ct = default)
    {
        var result = await http.GetFromJsonAsync<List<string>>("api/categories/palette", JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<CategoryDto> CreateCategoryAsync(CategoryCreateDto payload, CancellationToken ct = default)
    {
        var response = await http.PostAsJsonAsync(Collection, payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<CategoryDto>(JacerJson.Options, ct))!;
    }

    public async Task<CategoryDto> UpdateCategoryAsync(string id, CategoryUpdateDto payload, CancellationToken ct = default)
    {
        var response = await http.PatchAsJsonAsync($"api/categories/{id}", payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<CategoryDto>(JacerJson.Options, ct))!;
    }

    public async Task DeleteCategoryAsync(string id, CancellationToken ct = default)
    {
        var response = await http.DeleteAsync($"api/categories/{id}", ct);
        response.EnsureSuccessStatusCode();
    }
}
