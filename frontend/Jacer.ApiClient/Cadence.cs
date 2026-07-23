namespace Jacer.ApiClient;

/// <summary>
/// Mirrors the backend <c>Cadence</c> literal: weekly | fortnightly. Serialised
/// as snake_case lower via <see cref="JacerJson.Options"/>, which matches the
/// FastAPI contract exactly (single words → lowercase).
/// </summary>
public enum Cadence
{
    Weekly,
    Fortnightly,
}
