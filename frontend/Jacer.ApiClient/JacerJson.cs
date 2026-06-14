using System.Text.Json;
using System.Text.Json.Serialization;

namespace Jacer.ApiClient;

/// <summary>
/// Shared serialisation settings for talking to the Jacer FastAPI backend.
/// The backend uses snake_case field names and lowercase string enums, so we
/// map property names with <see cref="JsonNamingPolicy.SnakeCaseLower"/> and
/// register a matching enum converter. <see cref="JsonIgnoreCondition.WhenWritingNull"/>
/// lets the partial-update DTOs (PATCH) send only the fields that were set.
/// </summary>
public static class JacerJson
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower) },
    };
}
