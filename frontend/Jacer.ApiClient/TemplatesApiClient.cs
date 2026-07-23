using System.Net;
using System.Net.Http.Json;

namespace Jacer.ApiClient;

/// <inheritdoc cref="ITemplatesApi"/>
public sealed class TemplatesApiClient(HttpClient http) : ITemplatesApi
{
    // Collection route keeps its trailing slash on purpose (avoids FastAPI's
    // 307 redirect, which drops POST/PATCH bodies). Item routes are flat.
    private const string Collection = "api/templates/";

    public async Task<IReadOnlyList<TemplateDto>> ListTemplatesAsync(CancellationToken ct = default)
    {
        var result = await http.GetFromJsonAsync<List<TemplateDto>>(Collection, JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<TemplateDto> CreateTemplateAsync(TemplateCreateDto payload, CancellationToken ct = default)
    {
        var response = await http.PostAsJsonAsync(Collection, payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TemplateDto>(JacerJson.Options, ct))!;
    }

    public async Task<TemplateDto?> GetTemplateAsync(string id, CancellationToken ct = default)
    {
        var response = await http.GetAsync($"api/templates/{id}", ct);
        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<TemplateDto>(JacerJson.Options, ct);
    }

    public async Task<TemplateDto> UpdateTemplateAsync(
        string id,
        TemplateUpdateDto payload,
        CancellationToken ct = default)
    {
        var response = await http.PatchAsJsonAsync($"api/templates/{id}", payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TemplateDto>(JacerJson.Options, ct))!;
    }

    public async Task DeleteTemplateAsync(string id, CancellationToken ct = default)
    {
        var response = await http.DeleteAsync($"api/templates/{id}", ct);
        response.EnsureSuccessStatusCode();
    }

    public async Task<LockResponseDto> LockTemplateAsync(string id, CancellationToken ct = default)
    {
        var response = await http.PostAsync($"api/templates/{id}/lock", null, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<LockResponseDto>(JacerJson.Options, ct))!;
    }

    public async Task<LockResponseDto> UnlockTemplateAsync(string id, CancellationToken ct = default)
    {
        var response = await http.PostAsync($"api/templates/{id}/unlock", null, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<LockResponseDto>(JacerJson.Options, ct))!;
    }

    // Items — created/listed nested, mutated flat.

    public async Task<IReadOnlyList<TemplateItemDto>> ListItemsAsync(
        string templateId,
        CancellationToken ct = default)
    {
        var result = await http.GetFromJsonAsync<List<TemplateItemDto>>(
            $"api/templates/{templateId}/items", JacerJson.Options, ct);
        return result ?? [];
    }

    public async Task<TemplateItemDto> CreateItemAsync(
        string templateId,
        TemplateItemCreateDto payload,
        CancellationToken ct = default)
    {
        var response = await http.PostAsJsonAsync(
            $"api/templates/{templateId}/items", payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TemplateItemDto>(JacerJson.Options, ct))!;
    }

    public async Task<TemplateItemDto?> GetItemAsync(string itemId, CancellationToken ct = default)
    {
        var response = await http.GetAsync($"api/template-items/{itemId}", ct);
        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<TemplateItemDto>(JacerJson.Options, ct);
    }

    public async Task<TemplateItemDto> UpdateItemAsync(
        string itemId,
        TemplateItemUpdateDto payload,
        CancellationToken ct = default)
    {
        var response = await http.PatchAsJsonAsync(
            $"api/template-items/{itemId}", payload, JacerJson.Options, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<TemplateItemDto>(JacerJson.Options, ct))!;
    }

    public async Task DeleteItemAsync(string itemId, CancellationToken ct = default)
    {
        var response = await http.DeleteAsync($"api/template-items/{itemId}", ct);
        response.EnsureSuccessStatusCode();
    }
}
