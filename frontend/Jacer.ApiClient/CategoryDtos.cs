namespace Jacer.ApiClient;

/// <summary>
/// A category as returned by the backend (<c>/api/categories</c>). Maps to the
/// FastAPI <c>Category</c> model via snake_case serialisation.
/// </summary>
public sealed record CategoryDto
{
    public required string Id { get; init; }
    public required string Name { get; init; }

    /// <summary>Hex colour drawn from the backend's fixed muted palette.</summary>
    public required string Colour { get; init; }
}

/// <summary>
/// Payload for <c>POST /api/categories/</c>. Only <see cref="Name"/> is required;
/// an omitted colour is auto-assigned round-robin from the palette by the backend.
/// </summary>
public sealed record CategoryCreateDto
{
    public required string Name { get; init; }
    public string? Colour { get; init; }
}

/// <summary>Payload for <c>PATCH /api/categories/{id}</c> — partial update.</summary>
public sealed record CategoryUpdateDto
{
    public string? Name { get; init; }
    public string? Colour { get; init; }
}
